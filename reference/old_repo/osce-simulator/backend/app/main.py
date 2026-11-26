from fastapi import FastAPI, HTTPException, Depends, Request, Response, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from .core.config import get_settings
from .schemas.patient import PatientCaseRequest, PatientCase
from .schemas.chat import ChatRequest, ChatResponse
from .core.auth import create_access_token, get_current_username, get_allowed_users
from .services.session_manager import SessionManager
from .services.specialized_evaluation_service import SpecializedEvaluationService
from .schemas.specialized_evaluation import SpecializedEvaluationResponse
from .schemas.evaluation import EvaluationRequest
from .services.langchain_service import LangChainService
import time
from typing import Dict, Any, List
import logging
import traceback
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Theia OSCE API for generating and evaluating patient cases",
    docs_url=None,  # Disable default docs
    redoc_url=None,  # Disable default redoc
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Initialize LangChain service
langchain_service = LangChainService()
import os
session_manager = SessionManager()
evaluation_service = SpecializedEvaluationService()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting (raised to better support interactive UI operations)
RATE_LIMIT = 120  # requests per minute
RATE_LIMIT_WINDOW = 60  # seconds
request_history: Dict[str, List[float]] = {}

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()
    
    # Clean up old requests
    if client_ip in request_history:
        request_history[client_ip] = [t for t in request_history[client_ip] 
                                    if current_time - t < RATE_LIMIT_WINDOW]
    
    # Check rate limit
    if client_ip in request_history and len(request_history[client_ip]) >= RATE_LIMIT:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Please try again later."}
        )
    
    # Add current request
    if client_ip not in request_history:
        request_history[client_ip] = []
    request_history[client_ip].append(current_time)
    
    response = await call_next(request)
    return response

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        title=f"{settings.PROJECT_NAME} - Swagger UI",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
    )

@app.get("/")
async def root():
    return {
        "message": "Welcome to OSCE Simulator API",
        "docs_url": "/docs",
        "api_url": settings.API_V1_STR
    }

# ---- Auth Endpoints ----
@app.post("/api/auth/login")
async def login(form: dict, response: Response):
    # Very basic login: username/password from body, default credentials [REDACTED for TheiaXR reference copy]
    username = form.get("username")
    password = form.get("password")
    allowed = get_allowed_users()
    if username not in allowed or allowed.get(username) != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": username}, expires_minutes=60)
    # HttpOnly cookie
    response.set_cookie(
        key="osce_access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60*60,
        domain="localhost",  # Allow cookie to be shared with localhost
    )
    return {"username": username}

@app.post("/api/auth/logout")
async def logout(response: Response):
    response.delete_cookie("osce_access_token")
    return {"ok": True}

@app.get("/api/auth/me")
async def me(username: str = Depends(get_current_username)):
    return {"username": username}

@app.post(f"{settings.API_V1_STR}/patient", response_model=PatientCase)
async def create_patient_case(request: PatientCaseRequest, username: str = Depends(get_current_username)):
    """Generate a new patient case based on the provided settings."""
    try:
        logger.debug("Received request to generate patient case")
        logger.debug(f"Request data: {request.dict()}")
        
        # Generate patient case using LangChain
        case_data = await langchain_service.generate_patient_case(
            difficulty=request.difficulty.value,
            age=request.age,
            gender=request.gender.value,
            personality_traits=[trait for trait, value in request.personality_traits.dict().items() if value],
            behavioral_settings=request.behavioral_settings.dict()
        )
        
        logger.debug("Successfully generated patient case")
        return case_data
    except Exception as e:
        logger.error(f"Error generating patient case: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        if "API key" in str(e):
            raise HTTPException(status_code=401, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post(f"{settings.API_V1_STR}/evaluate")
async def evaluate_case_response(request: EvaluationRequest, username: str = Depends(get_current_username)) -> SpecializedEvaluationResponse:
    """LLM-driven rubric evaluation using conversation history and optional notes."""
    try:
        conv = session_manager.get_conversation(request.conversation_id, username)
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Case hint for LLM
        case_hint = None
        try:
            case_hint = await langchain_service.get_patient_case(request.case_id)
            case_hint = case_hint.dict() if hasattr(case_hint, "dict") else dict(case_hint)
        except Exception:
            case_hint = None

        # Use specialized evaluation service to evaluate transcript
        evaluation_result = await evaluation_service.evaluate_all_categories(conv, case_details=case_hint)
        
        result = SpecializedEvaluationResponse(
            case_id=request.case_id,
            conversation_id=request.conversation_id,
            scores=evaluation_result["scores"],
            feedback=evaluation_result["feedback"],
            total_score=evaluation_result["total_score"],
            max_possible=evaluation_result["max_possible"],
            time_taken=request.time_taken,
            details={"evaluation_raw": evaluation_result}
        )
        
        # Persist the evaluation result
        evaluation_service.persist(request.conversation_id, result)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error evaluating case response: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get(f"{settings.API_V1_STR}/settings")
async def get_settings():
    """Return available settings for patient case generation."""
    return {
        "difficulty_levels": ["simple", "medium", "hard"],
        "personality_traits": {
            "shy": [True, False],
            "introverted": [True, False],
            "anxious": [True, False],
            "talkative": [True, False],
            "defensive": [True, False],
            "friendly": [True, False]
        },
        "behavioral_settings": {
            "cooperative": [True, False],
            "provides_complete_answers": [True, False],
            "emotional": [True, False]
        }
    }


@app.get(f"{settings.API_V1_STR}/patient/{{case_id}}", response_model=PatientCase)
async def get_patient_case(case_id: str):
    try:
        return await langchain_service.get_patient_case(case_id)
    except Exception as e:
        logger.error(f"Error retrieving patient case: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_patient(request: ChatRequest, username: str = Depends(get_current_username)):
    try:
        logger.debug("Received chat request: %s", request.dict())
        # ensure session: reuse only if it exists, otherwise create fresh
        candidate = request.session_id
        logger.debug("Session candidate: %s", candidate)
        if candidate and session_manager.get_session(candidate):
            session_id = candidate
            logger.debug("Reusing existing session: %s", session_id)
            # Touch the session to keep it alive
            session_manager.touch_session(session_id)
        else:
            session_id = session_manager.create_session(user_id=username, case_id=request.case_id)
            logger.debug("Created new session: %s", session_id)
            # Attempt to set a patient profile summary as the conversation title
            try:
                case_obj = await langchain_service.get_patient_case(request.case_id)
                case = case_obj.dict() if hasattr(case_obj, "dict") else dict(case_obj)
                name = case.get("name") or "Patient"
                age = case.get("age")
                gender = case.get("gender")
                gender_short = "M" if str(gender).lower().startswith("m") else ("F" if str(gender).lower().startswith("f") else "?")
                cc = case.get("chief_complaint") or "Unknown"
                title = f"{name} • {age if age is not None else '?'}{gender_short} • CC: {cc}"
                session_manager.rename_conversation(session_id, username, title[:80])
            except Exception:
                # If case not found, keep default title; will be improved on first message append
                pass
        response = await langchain_service.chat_with_patient(
            case_id=request.case_id,
            message=request.message,
            memory_key=session_id,
        )
        # append messages to conversation store
        session_manager.append_message(session_id, role="user", content=request.message)
        session_manager.append_message(session_id, role="assistant", content=response.message)
        # include session id in response body so client can persist it
        response.session_id = session_id
        logger.debug("Generated chat response: %s", response.dict())
        return response
    except Exception as e:
        logger.error("Error in chat: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/transcribe")
async def transcribe_audio(audio_file: UploadFile = File(...), username: str = Depends(get_current_username)):
    """Transcribe audio file using OpenAI's transcription API."""
    try:
        # Check file type
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="File must be an audio file")
        
        # Read the audio file content
        audio_content = await audio_file.read()
        
        # Import OpenAI client
        from openai import OpenAI
        import tempfile
        import os
        
        # Get OpenAI API key from settings
        openai_api_key = settings.OPENAI_API_KEY
        if not openai_api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        # Create OpenAI client
        client = OpenAI(api_key=openai_api_key)
        
        # Save audio content to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_file.write(audio_content)
            temp_file_path = temp_file.name
        
        try:
            # Open the temporary file and transcribe
            with open(temp_file_path, 'rb') as audio_file_obj:
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file_obj,
                    response_format="text"
                )
            
            return {
                "transcription": transcription,
                "success": True
            }
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.VERSION
    }



@app.get("/api/conversation/{conversation_id}/history")
async def get_conversation_history(conversation_id: str):
    """Get the conversation history for a specific conversation/session."""
    try:
        history = langchain_service.get_conversation_history(conversation_id)
        return {
            "conversation_id": conversation_id,
            "history": history,
            "message_count": len(history)
        }
    except Exception as e:
        logger.error(f"Error retrieving conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/conversation/{conversation_id}/memory")
async def clear_conversation_memory(conversation_id: str):
    """Clear the conversation memory for a specific conversation/session."""
    try:
        langchain_service.clear_conversation_memory(conversation_id)
        return {
            "conversation_id": conversation_id,
            "message": "Conversation memory cleared successfully"
        }
    except Exception as e:
        logger.error(f"Error clearing conversation memory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ---- Conversation History APIs (per user) ----
@app.get("/api/conversations")
async def list_conversations(username: str = Depends(get_current_username)):
    return {"items": session_manager.list_conversations(username)}

@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: str, username: str = Depends(get_current_username)):
    conv = session_manager.get_conversation(conversation_id, username)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    # Include evaluation if exists
    eval_data = evaluation_service.load(conversation_id)
    if eval_data:
        conv["evaluation"] = eval_data.dict()
    return conv

@app.get("/api/evaluations")
async def list_evaluations(username: str = Depends(get_current_username)):
    """List all evaluations for the authenticated user."""
    user_conversations = session_manager.list_conversations(username)
    evaluations = []
    
    for conv in user_conversations:
        eval_data = evaluation_service.load(conv["conversation_id"])
        if eval_data:
            # Convert to dict if it's a Pydantic model
            if hasattr(eval_data, "model_dump"):
                eval_dict = eval_data.model_dump()
            elif hasattr(eval_data, "dict"):
                eval_dict = eval_data.dict()
            else:
                eval_dict = dict(eval_data)
            
            # Add required fields for frontend
            eval_dict.update({
                "id": conv["conversation_id"],  # Use conversation_id as id
                "conversation_id": conv["conversation_id"],
                "case_id": conv.get("case_id", ""),
                "patientName": conv.get("title", "Unknown Patient"),
                "date": conv.get("updated_at", int(datetime.now().timestamp())),
                "score": eval_dict.get("total_score", 0),
                "maxScore": eval_dict.get("max_possible", 65),
                "timeTaken": f"{int(eval_dict.get('time_taken', 0) // 60):02d}:{int(eval_dict.get('time_taken', 0) % 60):02d}" if eval_dict.get("time_taken") is not None else "In Progress",
                "status": "completed" if eval_dict.get("total_score") is not None else "in-progress"
            })
            evaluations.append(eval_dict)
    
    return {"items": evaluations}

@app.get("/api/evaluations/{conversation_id}")
async def get_evaluation(conversation_id: str, username: str = Depends(get_current_username)):
    """Get evaluation data for a specific conversation."""
    eval_data = evaluation_service.load(conversation_id)
    if not eval_data:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return eval_data

@app.patch("/api/conversations/{conversation_id}")
async def rename_conversation(conversation_id: str, payload: Dict[str, str], username: str = Depends(get_current_username)):
    title = payload.get("title")
    if not title:
        raise HTTPException(status_code=400, detail="title is required")
    if not session_manager.rename_conversation(conversation_id, username, title):
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"ok": True}

@app.post("/api/conversations/{conversation_id}/archive")
async def archive_conversation(conversation_id: str, username: str = Depends(get_current_username)):
    if not session_manager.archive_conversation(conversation_id, username):
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"ok": True}

@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, username: str = Depends(get_current_username)):
    if not session_manager.delete_conversation(conversation_id, username):
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"ok": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 