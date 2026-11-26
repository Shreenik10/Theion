from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, AIMessage
from typing import Dict, Any, List, Optional
from ..core.config import get_settings
from ..schemas.patient import PatientCaseRequest, PatientCase
from ..schemas.chat import ChatMessage, ChatResponse
import os
import uuid
import json
import logging
from datetime import datetime
import re
from dotenv import load_dotenv

# Read API key directly from file for reliability
api_key = None
try:
    dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
    if os.path.exists(dotenv_path):
        with open(dotenv_path, 'r') as f:
            env_content = f.read()
            for line in env_content.strip().split('\n'):
                if line.startswith('OPENAI_API_KEY='):
                    api_key = line.split('=', 1)[1].strip()
                    print(f"DEBUG: API Key read directly from file: {api_key[:8]}...")
                    break
except Exception as e:
    print(f"Error reading API key from file: {str(e)}")

# Still try the regular method as fallback
settings = get_settings()
if not api_key:
    api_key = settings.OPENAI_API_KEY
    print(f"DEBUG: Using API key from settings: {api_key[:8] if api_key else 'None'}...")

logger = logging.getLogger(__name__)

# Pydantic models for structured output
class PatientCaseOutput(BaseModel):
    id: str = Field(description="Unique case identifier")
    name: str = Field(description="Patient's full name (e.g., 'Sarah Johnson', 'Michael Chen')")
    chief_complaint: str = Field(description="Main complaint")
    history_of_present_illness: str = Field(description="Detailed history")
    past_medical_history: str = Field(description="Relevant past medical history")
    medications: List[str] = Field(description="List of medications")
    allergies: List[str] = Field(description="List of allergies")
    social_history: str = Field(description="Relevant social history")
    family_history: str = Field(description="Relevant family history")
    vital_signs: Dict[str, str] = Field(description="Vital signs")
    physical_examination: str = Field(description="Physical examination findings")
    labs: Dict[str, str] = Field(description="Laboratory results")
    imaging: Dict[str, str] = Field(description="Imaging results")
    difficulty: str = Field(description="Case difficulty level")
    age: int = Field(description="Patient age")
    gender: str = Field(description="Patient gender")
    personality_traits: Dict[str, bool] = Field(description="Personality traits")
    behavioral_settings: Dict[str, bool] = Field(description="Behavioral settings")

class EvaluationOutput(BaseModel):
    history_taking_score: int = Field(description="Score for history taking (0-5)")
    communication_score: int = Field(description="Score for communication (0-5)")
    clinical_reasoning_score: int = Field(description="Score for clinical reasoning (0-5)")
    professionalism_score: int = Field(description="Score for professionalism (0-5)")
    time_efficiency_score: int = Field(description="Score for time efficiency (0-5)")
    feedback: str = Field(description="Detailed feedback")

# LLM rubric aligned to OSCE rubric structure
class LlmRubricScores(BaseModel):
    # Core Assessment Categories (0-6 each)
    introduction_collaboration: int = Field(description="0-6: Introduction & collaboration with patient, biographical data, PMH Part 1")
    past_medical_history_part2: int = Field(description="0-6: Past Medical History Part 2 - medications and allergies")
    family_history: int = Field(description="0-6: Family History - 3 generations and hereditary conditions")
    functional_assessment_part1: int = Field(description="0-6: Functional Assessment Part 1 - activity, mobility, sleep, nutrition, elimination")
    functional_assessment_part2: int = Field(description="0-6: Functional Assessment Part 2 - coping, smoking/vaping, advanced care planning")
    review_of_systems: int = Field(description="0-6: Review of Systems - must be related to PMHx or Family Hx")
    health_promotion_opportunities: int = Field(description="0-6: Opportunities for Health Promotion - 3 health promotion items")
    quality_health_promotion: int = Field(description="0-6: Quality of Health Promotion - communication style and evidence-based recommendations")
    
    # Global Appreciation Categories
    patient_centered_care: int = Field(description="0-6: Global Appreciation - Patient Centered Care")
    interview_style: int = Field(description="0-6: Global Appreciation - Interview Style")
    organization: int = Field(description="0-6: Global Appreciation - Organization")
    clinical_judgment: int = Field(description="0-10: Global Appreciation - Clinical Judgment, Reasoning and Knowledge")
    professionalism: int = Field(description="0-6: Global Appreciation - Professionalism")


class LlmRubricFeedback(BaseModel):
    # Core Assessment Categories
    introduction_collaboration: str
    past_medical_history_part2: str
    family_history: str
    functional_assessment_part1: str
    functional_assessment_part2: str
    review_of_systems: str
    health_promotion_opportunities: str
    quality_health_promotion: str
    
    # Global Appreciation Categories
    patient_centered_care: str
    interview_style: str
    organization: str
    clinical_judgment: str
    professionalism: str
    overall: str


class LlmRubricOutput(BaseModel):
    scores: LlmRubricScores
    feedback: LlmRubricFeedback

# Chat output with emotion
class ChatEmotionOutput(BaseModel):
    reply: str = Field(description="Patient reply text without speaker labels")
    emotion: str = Field(description="Short description of the patient's emotional state (3-10 words)")

class LangChainService:
    def __init__(self):
        # Use API key read directly from file
        self.api_key = api_key
        
        # Validate API key
        if not self.api_key:
            logger.error("No OpenAI API key found. Please set OPENAI_API_KEY in your .env file.")
            raise ValueError("OpenAI API key is required. Please set OPENAI_API_KEY in your .env file.")
        
        # Initialize LangChain ChatOpenAI
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            api_key=self.api_key,
            max_tokens=2048,  # Increased for detailed feedback
            model_kwargs={
                "presence_penalty": 0.2,  # encourage new content
                "frequency_penalty": 0.5, # reduce verbatim repetition
            },
        )
        
        # Initialize output parser
        self.patient_parser = JsonOutputParser(pydantic_object=PatientCaseOutput)
        self.evaluation_parser = JsonOutputParser(pydantic_object=EvaluationOutput)
        self.rubric_parser = JsonOutputParser(pydantic_object=LlmRubricOutput)
        
        # Initialize conversation memories for each case
        self.conversation_memories: Dict[str, ConversationBufferMemory] = {}
        
        logger.info(f"LangChain service initialized with model: gpt-3.5-turbo, API key starting with: {self.api_key[:8]}...")
        
        # In-memory storage for patient cases during development
        self.patient_cases = {}

    def _ensure_complete_case(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fill any missing PatientCase required fields with sensible defaults."""
        # Normalize incoming structure (dict or Pydantic model)
        if data is None:
            out: Dict[str, Any] = {}
        elif isinstance(data, dict):
            out = dict(data)
        elif hasattr(data, "dict"):
            try:
                out = data.dict()
            except Exception:
                out = dict(data.__dict__)
        elif hasattr(data, "model_dump"):
            out = data.model_dump()  # type: ignore[attr-defined]
        else:
            try:
                out = json.loads(json.dumps(data, default=lambda o: getattr(o, "__dict__", str(o))))
            except Exception:
                out = {}
        
        def _values_to_strings(obj: Dict[str, Any]) -> Dict[str, str]:
            result: Dict[str, str] = {}
            if not isinstance(obj, dict):
                return {}
            for key, value in obj.items():
                if isinstance(value, str):
                    result[key] = value
                elif isinstance(value, (int, float)):
                    result[key] = str(value)
                elif isinstance(value, (list, dict)):
                    try:
                        # Prefer human-friendly summarization for common lab/imaging nests
                        if isinstance(value, dict):
                            flat = "; ".join(f"{k}: {v}" for k, v in value.items())
                            result[key] = flat
                        else:
                            result[key] = ", ".join(map(str, value))
                    except Exception:
                        result[key] = json.dumps(value, ensure_ascii=False)
                else:
                    result[key] = str(value)
            return result
        # Required simple fields
        out.setdefault("labs", {})
        out["labs"] = _values_to_strings(out.get("labs", {}))
        out.setdefault("imaging", {})
        out["imaging"] = _values_to_strings(out.get("imaging", {}))
        out.setdefault("difficulty", "simple")
        out.setdefault("age", 30)
        out.setdefault("gender", "female")
        # Personality / behavior
        if not isinstance(out.get("personality_traits"), dict):
            out["personality_traits"] = {"shy": False, "introverted": False, "anxious": True, "talkative": True, "defensive": False, "friendly": True}
        else:
            for k in ["shy","introverted","anxious","talkative","defensive","friendly"]:
                out["personality_traits"].setdefault(k, False)
        if not isinstance(out.get("behavioral_settings"), dict):
            out["behavioral_settings"] = {"cooperative": True, "provides_complete_answers": True, "emotional": False}
        else:
            for k, v in {"cooperative": True, "provides_complete_answers": True, "emotional": False}.items():
                out["behavioral_settings"].setdefault(k, v)
        # Vitals presence
        out.setdefault("vital_signs", {})
        if isinstance(out["vital_signs"], dict):
            out["vital_signs"] = _values_to_strings(out["vital_signs"]) or {}
        # Name/ID defaults
        out.setdefault("id", str(uuid.uuid4()))
        out.setdefault("name", out.get("name", "Patient"))
        out.setdefault("chief_complaint", out.get("chief_complaint", "Unknown"))
        out.setdefault("history_of_present_illness", out.get("history_of_present_illness", "Unknown"))
        out.setdefault("past_medical_history", out.get("past_medical_history", "Unknown"))
        out.setdefault("medications", out.get("medications", []))
        out.setdefault("allergies", out.get("allergies", []))
        out.setdefault("social_history", out.get("social_history", "Unknown"))
        out.setdefault("family_history", out.get("family_history", "Unknown"))
        out.setdefault("physical_examination", out.get("physical_examination", "Unremarkable"))
        return out

    def _get_or_create_memory(self, memory_key: str) -> ConversationBufferMemory:
        """Get or create a conversation memory for a specific key (conversation/session or case)."""
        if memory_key not in self.conversation_memories:
            self.conversation_memories[memory_key] = ConversationBufferMemory(
                return_messages=True,
                memory_key="chat_history"
            )
        return self.conversation_memories[memory_key]

    def _add_to_memory(self, memory_key: str, human_message: str, ai_message: str):
        """Add a conversation exchange to the memory."""
        memory = self._get_or_create_memory(memory_key)
        memory.chat_memory.add_user_message(human_message)
        memory.chat_memory.add_ai_message(ai_message)

    def _is_repetitive(self, previous: str, current: str) -> bool:
        """Detect if current reply largely repeats the previous one."""
        try:
            if not previous or not current:
                return False
            prev = re.sub(r"\s+", " ", previous.strip().lower())
            cur = re.sub(r"\s+", " ", current.strip().lower())
            if prev == cur:
                return True
            # Token overlap ratio
            prev_tokens = set(re.findall(r"\w+", prev))
            cur_tokens = set(re.findall(r"\w+", cur))
            if not prev_tokens or not cur_tokens:
                return False
            overlap = len(prev_tokens & cur_tokens) / max(1, len(cur_tokens))
            # If more than 80% of current tokens are in previous, consider repetitive
            return overlap > 0.8
        except Exception:
            return False

    def _rewrite_direct_answer(self, case: Dict[str, Any], question: str, current_reply: str, style_instructions: str) -> str:
        """Ask LLM to rewrite the reply to directly answer the doctor's question without restating background."""
        try:
            pmh = case.get("past_medical_history", "Unknown")
            meds = ", ".join(case.get("medications", []) or []) or "None"
            allergies = ", ".join(case.get("allergies", []) or []) or "None"
            prompt = ChatPromptTemplate.from_template(
                """
                Rewrite the patient's reply to directly answer the doctor's question ONLY.
                - Do NOT restate background/profile unless asked explicitly.
                - If the question asks for info not in profile (e.g., height/weight) and the patient wouldn't know, say you are not sure or don't recall; do not invent data.
                - Keep it aligned with style rules: {style_instructions}
                - Output ONLY the patient reply (no labels, no JSON).

                Profile quick facts (for consistency only):
                PMH: {pmh}; Meds: {meds}; Allergies: {allergies}

                Doctor's question:
                {question}

                Original reply:
                {reply}
                """
            )
            chain = prompt | self.llm
            out = chain.invoke({
                "style_instructions": style_instructions,
                "pmh": pmh,
                "meds": meds,
                "allergies": allergies,
                "question": question,
                "reply": current_reply,
            })
            text = getattr(out, "content", out) or ""
            return re.sub(r"^(?:Patient|Doctor|Assistant)\s*:\s*", "", text, flags=re.IGNORECASE).strip() or current_reply
        except Exception:
            return current_reply

    def _try_factoid_answer(self, case: Dict[str, Any], question: str) -> Optional[str]:
        """Return a concise first-person answer for simple fact questions without calling the LLM.

        Covers: age, name, gender, medications, allergies, PMH/social/family when explicitly asked.
        """
        try:
            q = (question or "").strip().lower()
            if not q:
                return None
            # Age
            if re.search(r"\b(how old|age)\b", q):
                age = case.get("age")
                if age is not None:
                    return f"I'm {age} years old."
            # Name
            if re.search(r"\b(name|what's your name|what is your name)\b", q):
                name = case.get("name") or ""
                if name:
                    return f"My name is {name}."
            # Gender/sex
            if re.search(r"\b(gender|sex)\b", q):
                gender = case.get("gender")
                if gender:
                    return f"I'm {gender}."
            # Medications
            if re.search(r"\b(meds?|medications?|medicine|do you take any)\b", q):
                meds = case.get("medications", []) or []
                text = ", ".join(meds) if meds else "I'm not on any medications."
                return text if meds else "I'm not on any medications."
            # Allergies
            if re.search(r"\ballerg(y|ies)\b", q):
                alls = case.get("allergies", []) or []
                return f"I'm allergic to {', '.join(alls)}." if alls else "I don't have any allergies that I know of."
            # PMH
            if re.search(r"\b(past medical|medical history|conditions|illnesses)\b", q):
                pmh = case.get("past_medical_history")
                return f"My past medical history: {pmh}." if pmh else "I don't have any significant past medical history."
            # Social
            if re.search(r"\b(social history|do you smoke|alcohol|drugs|occupation|work)\b", q):
                sh = case.get("social_history")
                return sh if sh else None
            # Family
            if re.search(r"\bfamily history|family|parents|siblings\b", q):
                fh = case.get("family_history")
                return fh if fh else None
            return None
        except Exception:
            return None

    def _enforce_first_person_and_profile_consistency(self, case: Dict[str, Any], reply_text: str, style_instructions: str) -> str:
        """If the reply is in third-person or contradicts key facts, rewrite to first-person with exact profile values."""
        try:
            if not reply_text:
                return reply_text

            text_lower = reply_text.lower()
            # Heuristic triggers for third-person clinical style
            third_person_triggers = [
                "the patient", "presents with", "she ", "he ", "mrs.", "mr.", " ms. ", "patient presents"
            ]
            violates_person = any(t in text_lower for t in third_person_triggers)

            # Detect an age mention in reply, and compare with case age if numeric
            stated_age_match = re.search(r"(\d{1,3})\s*[- ]?year[- ]?old", reply_text, flags=re.IGNORECASE)
            age_mismatch = False
            if isinstance(case.get("age"), int) and stated_age_match:
                try:
                    stated_age = int(stated_age_match.group(1))
                    age_mismatch = stated_age != int(case.get("age"))
                except Exception:
                    age_mismatch = False

            # If no issues detected, return as-is
            if not (violates_person or age_mismatch):
                return reply_text

            # Prepare exact profile facts
            age = case.get("age", "Unknown")
            gender = case.get("gender", "Unknown")
            pmh = case.get("past_medical_history", "Unknown")
            meds = ", ".join(case.get("medications", []) or []) or "None"
            allergies = ", ".join(case.get("allergies", []) or []) or "None"
            name = case.get("name", "")

            prompt = ChatPromptTemplate.from_template(
                """
                Rewrite the patient's reply so it is strictly FIRST-PERSON (I, my, me) and consistent with these facts:
                - Name: {name}
                - Age: {age}
                - Gender: {gender}
                - PMH: {pmh}
                - Meds: {medications}
                - Allergies: {allergies}

                Requirements:
                - Do NOT use phrases like "the patient", "she/he", "presents with"; speak as the patient.
                - Replace any conflicting details with the exact facts above.
                - Keep the same overall meaning and tone, and follow these style rules: {style_instructions}
                - Output ONLY the corrected patient reply text. No JSON, no commentary, no speaker labels.

                Original reply:
                {reply}
                """
            )

            chain = prompt | self.llm
            fixed = chain.invoke({
                "name": name,
                "age": age,
                "gender": gender,
                "pmh": pmh,
                "medications": meds,
                "allergies": allergies,
                "style_instructions": style_instructions,
                "reply": reply_text,
            })
            corrected = getattr(fixed, "content", fixed) or ""
            # Final cleanup: strip speaker labels if any
            corrected = re.sub(r"^(?:Patient|Doctor|Assistant)\s*:\s*", "", corrected, flags=re.IGNORECASE).strip()
            return corrected if corrected else reply_text
        except Exception:
            return reply_text

    def _infer_emotion(self, case: Dict[str, Any], reply_text: str) -> str:
        """Infer a plausible emotion from profile and content without an extra LLM call."""
        try:
            traits = case.get("personality_traits", {}) if isinstance(case.get("personality_traits"), dict) else {}
            behav = case.get("behavioral_settings", {}) if isinstance(case.get("behavioral_settings"), dict) else {}
            cc = (case.get("chief_complaint") or "").lower()
            text = (reply_text or "").lower()

            # Baseline from traits
            candidates: List[str] = []
            if traits.get("anxious"):
                candidates.append("Anxious")
            if traits.get("defensive"):
                candidates.append("Defensive")
            if traits.get("friendly"):
                candidates.append("Warm")
            if traits.get("shy") or traits.get("introverted"):
                candidates.append("Reserved")

            if not candidates:
                candidates.append("Calm")

            # Amplify by complaint/content
            worry_keywords = ["chest pain", "shortness of breath", "sob", "faint", "dizzy", "severe", "sharp", "worse", "bleed", "palpit"]
            discomfort_keywords = ["pain", "nausea", "vomit", "headache", "cramp", "tender", "ache"]
            frustration_keywords = ["why", "again", "tired of", "don\'t want", "stop asking", "annoy"]

            if any(k in cc or k in text for k in worry_keywords):
                candidates.insert(0, "Concerned")
            elif any(k in cc or k in text for k in discomfort_keywords):
                candidates.insert(0, "Uncomfortable")
            if any(k in text for k in frustration_keywords) or traits.get("defensive"):
                candidates.insert(0, "Irritated")

            # Behavioral emotional flag reduces odds of "Neutral"
            if behav.get("emotional") and "Neutral" in candidates:
                candidates = [c for c in candidates if c != "Neutral"]

            # Construct short 3-6 word phrase
            unique = []
            for c in candidates:
                if c not in unique:
                    unique.append(c)
            phrase = ", ".join(unique[:2])
            if not phrase:
                phrase = "Calm"
            return phrase
        except Exception:
            return "Concerned"

    def _reconcile_emotion(self, case: Dict[str, Any], reply_text: str, llm_emotion: Optional[str]) -> str:
        """Prefer model emotion if specific and coherent; otherwise replace with inferred."""
        inferred = self._infer_emotion(case, reply_text)
        if not llm_emotion:
            return inferred
        e = llm_emotion.strip()
        if not e:
            return inferred
        low = e.lower()
        generic = {"neutral", "ok", "okay", "fine", "normal"}
        traits = case.get("personality_traits", {}) if isinstance(case.get("personality_traits"), dict) else {}

        # If anxious/defensive traits, avoid "neutral" outputs
        if (traits.get("anxious") or traits.get("defensive")) and any(g in low for g in generic):
            return inferred
        # Keep short and concise (3-10 words)
        words = re.split(r"\s+", e)
        if len(words) > 10:
            return inferred
        return e

    async def generate_patient_case(self, difficulty: str, age: int, gender: str, personality_traits: list, behavioral_settings: dict) -> PatientCase:
        try:
            logger.debug("Generating patient case with parameters: %s", {
                "difficulty": difficulty,
                "age": age,
                "gender": gender,
                "personality_traits": personality_traits,
                "behavioral_settings": behavioral_settings
            })

            # Create prompt template
            prompt = ChatPromptTemplate.from_template("""
            Generate a detailed OSCE patient case with the following specifications:
            Difficulty: {difficulty}
            Age: {age}
            Gender: {gender}
            Personality Traits: {personality_traits}
            Behavioral Settings: {behavioral_settings}

            Generate a realistic and educational patient case that medical students can practice with.
            The case should be appropriate for the specified difficulty level and include all required fields.
            
            IMPORTANT: Generate a realistic full name for the patient (e.g., "Sarah Johnson", "Michael Chen", "Maria Rodriguez").
            The name should be appropriate for the patient's age, gender, and cultural background.
            
            {format_instructions}
            """)

            # Create the chain
            chain = prompt | self.llm | self.patient_parser

            # Prepare personality traits dict
            personality_dict = {trait: trait in personality_traits for trait in [
                "shy", "introverted", "anxious", "talkative", "defensive", "friendly"
            ]}

            # Run the chain
            result = await chain.ainvoke({
                "difficulty": difficulty,
                "age": age,
                "gender": gender,
                "personality_traits": ", ".join(personality_traits),
                "behavioral_settings": json.dumps(behavioral_settings),
                "format_instructions": self.patient_parser.get_format_instructions()
            })
            
            # Ensure ID is set
            if not result.get("id"):
                result["id"] = str(uuid.uuid4())
            
            # Ensure completeness and store
            result = self._ensure_complete_case(result)
            # Final defensive coercion for nested dicts in labs/imaging/vitals
            for field in ("labs", "imaging", "vital_signs"):
                try:
                    if isinstance(result.get(field), dict):
                        coerced = {}
                        for k, v in result[field].items():
                            if isinstance(v, str):
                                coerced[k] = v
                            elif isinstance(v, (int, float)):
                                coerced[k] = str(v)
                            elif isinstance(v, dict):
                                coerced[k] = "; ".join(f"{ik}: {iv}" for ik, iv in v.items())
                            elif isinstance(v, list):
                                coerced[k] = ", ".join(map(str, v))
                            else:
                                coerced[k] = json.dumps(v, ensure_ascii=False)
                        result[field] = coerced
                except Exception:
                    pass
            self.patient_cases[result["id"]] = result
            
            # Initialize memory for this case
            self._get_or_create_memory(result["id"])
            
            logger.debug("Generated case data: %s", result)
            return PatientCase(**self._ensure_complete_case(result))

        except Exception as e:
            logger.error("Error generating patient case: %s", str(e), exc_info=True)
            raise

    async def get_patient_case(self, case_id: str) -> PatientCase:
        """Retrieve a patient case by ID."""
        try:
            if case_id in self.patient_cases:
                complete = self._ensure_complete_case(self.patient_cases[case_id])
                return PatientCase(**complete)
            raise Exception(f"Patient case with ID {case_id} not found")
        except Exception as e:
            logger.error(f"Error retrieving patient case: {str(e)}")
            raise

    async def evaluate_response(self, case_id: str, response: str) -> Dict[str, Any]:
        """Evaluate a student's response to a patient case."""
        try:
            # Get the case if it exists
            case = None
            if case_id in self.patient_cases:
                case = self._ensure_complete_case(self.patient_cases[case_id])
            
            # Create prompt template
            prompt = ChatPromptTemplate.from_template("""
            Evaluate the following OSCE response based on these criteria:
            1. History taking completeness
            2. Communication effectiveness
            3. Clinical reasoning
            4. Professionalism
            5. Time efficiency

            {case_details}
            
            Student's Response:
            {response}

            Provide a detailed evaluation with scores (0-5) for each criterion and specific feedback.
            
            {format_instructions}
            """)

            # Create the chain
            chain = prompt | self.llm | self.evaluation_parser

            # Run the chain
            result = await chain.ainvoke({
                "case_details": f"Case details: {json.dumps(case)}" if case else "No case details available",
                "response": response,
                "format_instructions": self.evaluation_parser.get_format_instructions()
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error in evaluate_response: {str(e)}")
            raise Exception(f"Failed to evaluate response: {str(e)}")

    async def evaluate_performance(self, *, case: Optional[dict], conversation: dict, notes: Optional[str]) -> Dict[str, Any]:
        """LLM-based rubric evaluation using conversation transcript and optional notes."""
        try:
            # Prepare transcript
            messages = conversation.get("messages", [])
            lines: List[str] = []
            for m in messages:
                role = m.get("role")
                content = m.get("content", "")
                if role == "user":
                    lines.append(f"Doctor: {content}")
                elif role == "assistant":
                    lines.append(f"Patient: {content}")
            transcript = "\n".join(lines)

            # Prompt for LLM rubric scoring using OSCE rubric
            prompt = ChatPromptTemplate.from_template(
                """
                You are an OSCE examiner evaluating a nursing student's health history assessment. Use the following OSCE rubric to evaluate the doctor-patient interaction.

                OSCE RUBRIC (Total: 82 points):

                CORE ASSESSMENT CATEGORIES (6 points each = 48 points):
                1. introduction_collaboration (0-6): Introduction & collaboration with patient, biographical data, PMH Part 1
                   - E (6 points): 8+ elements, consent acquired
                   - P (5 points): 7 elements
                   - D (3.5 points): 5-6 elements
                   - U (1 point): 1-4 elements, no consent
                   - N/A (0 points): Section omitted

                2. past_medical_history_part2 (0-6): Past Medical History Part 2 - medications and allergies
                   - E (6 points): 8+ elements
                   - P (5 points): 7 elements
                   - D (3.5 points): 5-6 elements
                   - U (1 point): 1-4 elements
                   - N/A (0 points): Section omitted

                3. family_history (0-6): Family History - 3 generations and hereditary conditions
                   - E (6 points): 5+ elements, all 3 generations explained
                   - P (5 points): 4 elements
                   - D (3.5 points): 3 elements
                   - U (1 point): 1-2 elements
                   - N/A (0 points): Section omitted

                4. functional_assessment_part1 (0-6): Functional Assessment Part 1 - activity, mobility, sleep, nutrition, elimination
                   - E (6 points): 6+ elements
                   - P (5 points): 5 elements
                   - D (3.5 points): 4 elements
                   - U (1 point): 1-3 elements
                   - N/A (0 points): Section omitted

                5. functional_assessment_part2 (0-6): Functional Assessment Part 2 - coping, smoking/vaping, advanced care planning
                   - E (6 points): 7+ elements
                   - P (5 points): 6 elements
                   - D (3.5 points): 4-5 elements
                   - U (1 point): 1-3 elements
                   - N/A (0 points): Section omitted

                6. review_of_systems (0-6): Review of Systems - must be related to PMHx or Family Hx
                   - E (6 points): 5+ elements
                   - P (5 points): 4 elements
                   - D (3.5 points): 3 elements
                   - U (1 point): 1-2 elements
                   - N/A (0 points): Section omitted

                7. health_promotion_opportunities (0-6): Opportunities for Health Promotion - 3 health promotion items
                   - E (6 points): 3+ health promotion items
                   - P (5 points): 2 health promotion items
                   - D (3.5 points): 1 health promotion item
                   - U (1 point): Attempted but incomplete
                   - N/A (0 points): No education provided

                8. quality_health_promotion (0-6): Quality of Health Promotion - communication style and evidence-based recommendations
                   - E (6 points): Breaks down information, verifies understanding, evidence-based and tailored
                   - P (5 points): Mostly breaks down information, somewhat attentive to understanding
                   - D (3.5 points): Does not break down information well, vaguely attempts to adapt
                   - U (1 point): Does not break down information, not attentive to understanding
                   - N/A (0 points): No education provided

                GLOBAL APPRECIATION CATEGORIES:
                9. patient_centered_care (0-6): Patient Centered Care
                   - E (6 points): Always validates patient experience, considers beliefs/concerns, adapts interactions
                   - P (5 points): Takes into consideration most patient beliefs/concerns
                   - D (3.5 points): Takes into consideration some patient beliefs/concerns
                   - U (1 point): Does not consider patient beliefs/concerns

                10. interview_style (0-6): Interview Style
                    - E (6 points): Uses open-ended questions, guides with purposeful close-ended questions, avoids negative phrasing
                    - P (5 points): Uses statements instead of questions, guides most of interview appropriately
                    - D (3.5 points): Uses statements, guides some of interview, uses some negative phrasing
                    - U (1 point): Does not use open-ended questions, frequently uses negative phrasing

                11. organization (0-6): Organization
                    - E (6 points): Completes assessment in orderly manner
                    - P (5 points): Completes assessment mostly in orderly manner, minimal disorganization
                    - D (3.5 points): Completes assessment somewhat orderly, some disorganization
                    - U (1 point): Does not complete assessment in orderly manner

                12. clinical_judgment (0-10): Clinical Judgment, Reasoning and Knowledge
                    - E (10 points): Demonstrates sound clinical knowledge, good knowledge of pertinent clinical data
                    - P (7 points): Demonstrates some clinical knowledge, mostly demonstrates knowledge of pertinent data
                    - D (5 points): Demonstrates incomplete clinical knowledge, incomplete knowledge of pertinent data
                    - U (3 points): Demonstrates minimal clinical knowledge, minimal knowledge of pertinent data

                13. professionalism (0-6): Professionalism
                    - E (6 points): No professionalism concerns
                    - P (5 points): Minor professionalism concerns
                    - D (3.5 points): Some professionalism concerns
                    - U (1 point): Significant professionalism concerns

                Case details (may be null):
                {case_details}

                Transcript:
                {transcript}

                Notes (may be empty):
                {notes}

                IMPORTANT: For each category, provide both a score (integer) and detailed feedback (string) explaining why that score was given. The feedback should be specific and constructive.

                CRITICAL: All JSON keys must be quoted strings. Ensure every key in both "scores" and "feedback" objects is properly quoted.

                Provide JSON only that matches this schema exactly:
                {format_instructions}
                """
            )

            # Get raw LLM response first
            llm_response = await self.llm.ainvoke(prompt.format(
                case_details=json.dumps(case) if case else "null",
                transcript=transcript,
                notes=notes or "",
                format_instructions=self.rubric_parser.get_format_instructions(),
            ))
            
            # Clean up malformed JSON
            content = llm_response.content
            logger.debug("Raw LLM response: %s", content)
            
            # Fix common JSON issues
            import re
            # Fix double-quoted keys like ""clinical_judgment""
            content = re.sub(r'""([^"]+)""', r'"\1"', content)
            # Fix unquoted keys in feedback section
            content = re.sub(r'(\w+):"([^"]*)"', r'"\1":"\2"', content)
            content = re.sub(r'(\w+):"([^"]*)"', r'"\1":"\2"', content)  # Run twice to catch nested issues
            # Fix missing quotes around empty values
            content = re.sub(r':""', r':""', content)
            # Fix trailing commas before closing braces
            content = re.sub(r',(\s*[}\]])', r'\1', content)
            
            # Try to parse the cleaned JSON
            try:
                result: Dict[str, Any] = self.rubric_parser.parse(content)
                return result
            except Exception as parse_error:
                logger.error("Failed to parse LLM response: %s", parse_error)
                logger.error("Cleaned content: %s", content)
                # Return a default evaluation if parsing fails
                return {
                    "scores": {
                        "introduction_collaboration": 0,
                        "past_medical_history_part2": 0,
                        "family_history": 0,
                        "functional_assessment_part1": 0,
                        "functional_assessment_part2": 0,
                        "review_of_systems": 0,
                        "health_promotion_opportunities": 0,
                        "quality_health_promotion": 0,
                        "patient_centered_care": 0,
                        "interview_style": 0,
                        "organization": 0,
                        "clinical_judgment": 0,
                        "professionalism": 0
                    },
                    "feedback": {
                        "introduction_collaboration": "Evaluation parsing failed",
                        "past_medical_history_part2": "Evaluation parsing failed",
                        "family_history": "Evaluation parsing failed",
                        "functional_assessment_part1": "Evaluation parsing failed",
                        "functional_assessment_part2": "Evaluation parsing failed",
                        "review_of_systems": "Evaluation parsing failed",
                        "health_promotion_opportunities": "Evaluation parsing failed",
                        "quality_health_promotion": "Evaluation parsing failed",
                        "patient_centered_care": "Evaluation parsing failed",
                        "interview_style": "Evaluation parsing failed",
                        "organization": "Evaluation parsing failed",
                        "clinical_judgment": "Evaluation parsing failed",
                        "professionalism": "Evaluation parsing failed",
                        "overall": "Evaluation parsing failed due to malformed JSON response"
                    }
                }
        except Exception as e:
            logger.error("Error in evaluate_performance: %s", str(e), exc_info=True)
            raise

    async def chat_with_patient(self, case_id: str, message: str, chat_history: List[ChatMessage] = None, memory_key: Optional[str] = None) -> ChatResponse:
        try:
            logger.debug("Chat request - Case ID: %s, Message: %s", case_id, message)
            
            # Get the patient case from storage
            case = None
            if case_id in self.patient_cases:
                case = self.patient_cases[case_id]
            else:
                # Case not found - use a generic complete case for now (not stored)
                case = self._ensure_complete_case({
                    "id": case_id,
                    "name": "Patient",
                    "chief_complaint": "Chest pain",
                    "history_of_present_illness": "Patient has been experiencing chest pain for 2 days",
                    "past_medical_history": "Unknown",
                    "medications": [],
                    "allergies": [],
                    "social_history": "Unknown",
                    "family_history": "Unknown",
                    "physical_examination": "Unremarkable",
                    "personality_traits": {"anxious": True, "talkative": True},
                    "behavioral_settings": {"cooperative": True, "emotional": False, "provides_complete_answers": True}
                })

            # Convert personality traits to list for prompt and build style rules
            traits_dict = case.get("personality_traits", {}) if isinstance(case.get("personality_traits"), dict) else {}
            personality_traits = [trait for trait, value in traits_dict.items() if value]
            behav = case.get('behavioral_settings', {}) if isinstance(case.get('behavioral_settings'), dict) else {}

            style_parts: List[str] = []
            if traits_dict.get('talkative'):
                style_parts.append("Be talkative: in the reply field produce 3-6 full sentences (about 60-120 words) with spontaneous relevant details.")
            if traits_dict.get('shy') or traits_dict.get('introverted'):
                style_parts.append("Be brief and hesitant: in the reply field produce 1-2 short sentences (<= 25 words total); avoid volunteering extra information unless asked directly.")
            if traits_dict.get('anxious'):
                style_parts.append("Sound worried or uncertain when appropriate (e.g., 'I'm a bit worried', 'I'm not sure').")
            if traits_dict.get('friendly'):
                style_parts.append("Be warm and polite; include courteous phrases (e.g., 'please', 'thank you').")
            if traits_dict.get('defensive'):
                style_parts.append("Be guarded and somewhat curt; push back occasionally (e.g., 'Why do you need to know that?'). Keep replies concise (1-3 short sentences).")

            if behav.get('cooperative') is False:
                style_parts.append("Be minimally cooperative: sometimes deflect or give partial answers unless prompted again.")
            if behav.get('provides_complete_answers') is False:
                style_parts.append("Avoid complete answers unless specifically prompted for more detail.")
            if behav.get('emotional'):
                style_parts.append("Let emotions show (e.g., anxious tone, frustration, or relief) when contextually appropriate.")

            style_instructions = " ".join(style_parts) if style_parts else "Maintain a neutral, realistic tone."
            
            # Get the conversation memory (prefer conversation/session id if provided)
            key = memory_key or case_id
            memory = self._get_or_create_memory(key)
            
            # Build structured patient profile fields for stricter adherence
            demographics = {
                "age": case.get('age', 'Unknown'),
                "gender": case.get('gender', 'Unknown'),
            }
            pmh = case.get('past_medical_history', 'Unknown')
            meds = ", ".join(case.get('medications', []) or [])
            allergies = ", ".join(case.get('allergies', []) or [])
            social = case.get('social_history', 'Unknown')
            family = case.get('family_history', 'Unknown')
            vitals = case.get('vital_signs', {})

            # Create prompt template with memory
            prompt = ChatPromptTemplate.from_template("""
            # System Prompt: Saylor Lee — Conversational Primary-Care Encounter

            You are role-playing **Saylor Lee**, a PATIENT in a primary-care intake. You are seeking medical care from the doctor. You are NOT a healthcare provider.

            CRITICAL ROLE CLARITY:
            - You are a PATIENT seeking care from the doctor
            - You should NEVER say things like "How can I help you?", "How can I help you today?", "How can I assist you?", "How can I assist you today?", or any variation of offering to help the doctor
            - You are here to receive medical care, not provide it
            - The doctor is helping YOU, not the other way around
            - Respond as someone who needs medical attention and is answering the doctor's questions
            - You are the one being helped, not the helper
            - If someone says "I need help" or asks for help, you should respond as a patient who needs help, not offer to help them
            - If someone says "yes help me" or similar, they are asking for help - you should respond as a patient seeking help, not offer to help them
            - NEVER offer to help the doctor - you are the patient seeking help
            - The doctor is the one who helps patients, not the other way around

            Stay natural, concise, and cooperative. Never invent facts beyond those listed. Only reveal information when the user asks for it at the appropriate level of specificity. If an item is marked **ONLY IF EXPLICITLY ASKED**, do not volunteer it unprompted.
            
            IMPORTANT: Do NOT volunteer extra information. Answer only what is specifically asked. If asked "Do you consent?", just say "Yes, I consent." Do not add your name, age, medical history, or medications unless specifically asked.

            When the same topic is asked again, keep details **consistent** but feel free to **paraphrase** lightly.

            If the clinician asks *both* of two topics at once (e.g., "reaction and epipen"), include both answers in one response.

            Use first-person ("I…") and conversational tone. If a question is vague, answer at the most reasonable general level you're allowed to share; do not overshare gated details unless the wording clearly asks for them.

            ## Key Information About Saylor Lee

            **Background**: You moved from Ottawa to Montreal about six months ago and are new to this clinic. You're here for an initial check-up.

            **Medical History**: You were diagnosed with Type 2 Diabetes about 5 years ago. You've also experienced anxiety on and off with major life events and started treatment about 2 years ago. The medication has helped a lot.

            **Name**: When asked for your name, respond naturally with "Saylor Lee" or "I'm Saylor Lee."

            **Opening Responses**: 
            - For general greetings like "Hello" or "How are you?", respond naturally and conversationally
            - For "What brings you in today?" or similar questions, mention that you moved from Ottawa to Montreal about six months ago and are here for an initial check-up
            - Be warm and friendly but not overly formal

            ## Medical History

            * **General medical history**: "I was diagnosed with Type 2 Diabetes about 5 years ago. I've also experienced anxiety on and off with major life events and started treatment about 2 years ago. The medication has helped a lot."
            * **Cholesterol — ONLY IF EXPLICITLY ASKED**: "I was diagnosed with high cholesterol at the same time as my diabetes."
            * **Surgical history**: "I had my appendix removed when I was 20. No complications."
            * **Obstetrical history**: "I've never been pregnant; no miscarriages or abortions."
            * **Recent medical exam / access**: "My last medical exam was 6 months ago for a routine diabetes follow-up. Since moving, I haven't seen anyone here yet."

            ## Medications

            * **Current prescriptions**: 
              - **Base medications**: "I take Metformin 500 mg twice daily for diabetes and Cipralex 10 mg daily for anxiety."
              - **Cholesterol medication**: "I also take Lipitor 20 mg nightly for high cholesterol." (ONLY mention this if the doctor has explicitly asked about cholesterol or high cholesterol)
            * **OTC**: "I take Tylenol for headaches about once a month—650 mg (two tablets)."
            * **Supplements**: "I don't take any herbal supplements or natural products."
            * **Non-prescription (if asked generally)**: Combine the OTC and supplement lines above.
            
            **IMPORTANT**: When asked about medications, start with the base medications (Metformin and Cipralex). Only add Lipitor if cholesterol has been explicitly discussed.

            ## Allergies & Safety

            * **Food allergy**: "I'm allergic to peanuts."
            * **Allergic reaction — ONLY IF EXPLICITLY ASKED**: "My last reaction was a few years ago—facial swelling and difficulty breathing."
            * **Epipen — ONLY IF EXPLICITLY ASKED**: "I don't carry an epi-pen, but I know how to use one—'Orange to the thigh and blue to the sky.'"
            * **Medic alert bracelet — ONLY IF EXPLICITLY ASKED**: "I don't wear a medic alert bracelet."
            * If asked for **combos** (e.g., reaction+epipen or reaction+bracelet or all three), include the relevant combined details in one reply.
            * **Medication allergies**: "I don't have any medication allergies."
            * **Environmental allergies**: "I don't have any environmental allergies."
            * **Communicable diseases**: "I don't have any history of communicable diseases."
            * **STBBI testing — ONLY IF EXPLICITLY ASKED (STI/STD/STBBI)**: "My partner and I were tested two years ago, and all results were negative."

            ## Immunizations

            * **General status**: "I keep my vaccines up to date and plan to get the flu shot this year."
            * **Details/dates or access in Montreal — ONLY IF EXPLICITLY ASKED**: "My last immunization was the flu vaccine last fall. I'm not sure how to get my vaccines here in Montreal since moving."

            ## Systems Review & Lifestyle

            * **HEENT**: "I get headaches about once per month and take Tylenol. No other head, eye, ear, nose, or throat issues."
            * **Respiratory**: "I don't have any respiratory issues."

              * **Cough — ONLY IF EXPLICITLY ASKED**: "No, I don't have a cough."
            * **Cardiovascular**: "I don't have any cardiovascular issues."
            * **Peripheral vascular**: "I don't have any peripheral vascular issues."
            * **Genitourinary**: "I don't have any genitourinary issues."
            * **Musculoskeletal**: "I don't have any musculoskeletal issues."
            * **Neurological**: "I don't have any neurological issues."
            * **Endocrine (general)**: "I have diabetes, but it's well-controlled."

              * **Endocrine symptoms — ONLY IF EXPLICITLY ASKED** (weight loss, fever, chills, night sweats): "No, I haven't had any unintentional weight loss, fever, chills, or night sweats."
            * **Elimination**: "I have regular daily bowel movements—formed—with no urinary issues."
            * **Sleep**: "I usually get about 6 hours a night. I don't wake during the night, but I have trouble falling asleep because I make mental to-do lists."
            * **Nutrition (general)**: "I made drastic changes after my diabetes diagnosis 5 years ago, worked with a diabetes team, and I'm following my partner's vegetarian diet."

              * **24-hour recall — ONLY IF EXPLICITLY ASKED**: "Breakfast: oatmeal with fresh berries. Lunch: lentil soup with a mixed green salad. Dinner: vegetable stir-fry with tofu. Snacks: nuts and fruit."
            * **Activities**

              * **General**: "My main physical activities are walking and golf."
              * **Walking — ONLY IF EXPLICITLY ASKED**: "I used to walk 30 minutes every evening, but since moving into town I haven't walked as much. I'd like to get back to daily walks."
              * **Golf — ONLY IF EXPLICITLY ASKED**: "I golf every Saturday over the summer months, mostly for networking."
              * If asked for **both**, combine walking + golf in one answer.
            * **Mobility**: "I don't have any mobility issues."
            * **Assistive devices**: "I don't need any assistive devices."
            * **Skin/hair**: "I don't have skin issues, but I've noticed a little hair thinning and some hair loss in the shower."
            * **Nail clubbing — ONLY IF EXPLICITLY ASKED**: "No, I don't have any nail clubbing."
            * **Foot sensation — ONLY IF EXPLICITLY ASKED**: "No numbness, tingling, or loss of sensation in my feet."
            * **Vision changes — ONLY IF EXPLICITLY ASKED**: "I haven't noticed any changes in my vision."

            ## Social, Mental Health, Substances, Safety

            * **Mental health (current)**: "No other mental health concerns beyond the anxiety I mentioned, which is treated with medication."
            * **Coping**: "I need to use coping strategies more. I used to like going for walks but haven't prioritized that lately. I've heard of journaling but haven't tried it."
            * **Smoking/vaping (general)**: "I currently vape. I don't have any other smoking history."

              * **Vaping details — ONLY IF EXPLICITLY ASKED**: "I go through about one nicotine cartridge per day and have been vaping for 5 years. It used to help with stress."
            * **Alcohol**: "I usually have one beer or a glass of wine after work, sometimes two on weekends."
            * **Substances**: "I've never used any substances."
            * **Environmental hazards**: "I don't have any environmental hazards."
            * **Sexual health**: "I'm in a monogamous relationship. My last STBBI test was 2 years ago and it was negative. I don't use contraception or protective barriers."
            * **Financial**: "I don't have any financial issues."
            * **Relationships**: "I've been in a committed relationship for about 32 years—it's a good relationship. We have a supportive family, lots of friends and community, and I like my new colleagues. We don't have children."
            * **Spiritual resources**: "I don't have any spiritual resources."

            ## Family History

            * "My mother lives in Florida and has well-controlled type 2 diabetes. My father passed away 5 years ago from lung cancer. I have one sister around 62 who's healthy; we're close, and I'm close with my nieces and nephews—they get along with my partner. I don't know my grandparents' health history."

            ## Advanced Care Planning

            * **General**: "No one has ever talked to me about advanced care planning. I'd like more information."
            * **Details — ONLY IF EXPLICITLY ASKED**: "I've assumed my partner would be my medical power of attorney. I have an up-to-date will. I don't have any code status established. No other concerns."

            ### Consistency & Follow-ups

            * If asked the **same topic** again, keep facts identical, but you may rephrase for naturalness.
            * If the clinician asks broadly (e.g., "non-prescription meds"), include all relevant sub-items (OTC + supplements).
            * If the clinician asks about **multiple restricted items together**, share the combined details in one reply.
            
            IMPORTANT: Maintain consistent memory of the conversation.
            If the doctor repeats a question, politely provide the same answer again (do not say they already asked).
            Only acknowledge prior questioning if the doctor explicitly asks about it (e.g., "Did I ask your name earlier?").
            
            CONVERSATION FLOW: 
            - Vary your responses naturally - don't repeat the same phrases
            - Respond contextually to what the doctor is asking
            - If asked "How are you?" multiple times, you can vary your response (e.g., "I'm doing well, thanks", "I'm good, how about you?", "Pretty good, thank you")
            - Be conversational and natural, not robotic or repetitive
            - REMEMBER: You are a PATIENT - you answer questions, you don't ask "How can I help you?"
            - You are seeking care, not providing it
            
            CONSISTENCY RULES:
            - Always give the same factual information when asked the same question
            - If asked about medications multiple times, always mention the same medications
            - If asked about your age, always give the same age
            - If asked about medical conditions, always mention the same conditions
            - Maintain consistency in your medical history, medications, and personal information

            CRITICAL: You MUST respond with valid JSON only. Do not include any text before or after the JSON.
            
            Output rules:
            - Output ONLY valid JSON that matches this schema exactly:
              {format_instructions}
              Where "reply" is the patient's message text (no speaker labels).
            
            Example response format:
            {{"reply": "I'm doing well, thank you. How are you?"}}
            
            CONSISTENCY RULES:
            - Always give the same factual information when asked the same question
            - If asked about medications multiple times, always mention the same medications
            - If asked about your age, always give the same age
            - If asked about medical conditions, always mention the same conditions
            - Maintain consistency in your medical history, medications, and personal information
            - Do NOT volunteer extra information unless specifically asked
            - Answer only what is asked, nothing more
            - Do NOT change your answers based on what the doctor says
            - If you said "No, I don't have a cough" then stick with that answer
            - Do NOT invent new symptoms or conditions
            - Be consistent with your previous responses
            
            REPETITION RULES:
            - Do NOT repeat information you have already shared in this conversation
            - If you already mentioned moving from Ottawa to Montreal, do NOT mention it again unless specifically asked
            - If you already said you're here for an initial check-up, do NOT repeat this unless specifically asked
            - Keep responses concise and avoid repeating background information
            - Only provide new information or answer the specific question asked
            
            CONVERSATION STYLE:
            - Do NOT constantly say "thank you" or "thanks" in every response
            - Be natural and conversational, not overly polite or formal
            - Avoid repetitive phrases like "Thank you for asking" or "Thank you for helping"
            - Keep responses direct and to the point
            
            WRONG EXAMPLES (DO NOT SAY THESE):
            - "How can I help you?"
            - "How can I assist you?"
            - "How can I assist you today?"
            - "What can I do for you?"
            - "How can I help you today?"
            - "How can I help?"
            - "What can I do?"
            - Any variation of offering to help the doctor
            
            CORRECT PATIENT RESPONSES:
            - "I'm here for my check-up"
            - "I moved here recently and need to establish care"
            - "I'm doing well, thank you"
            - "I have some concerns about my health"
            - "I'm here for my appointment" (when someone asks for help)
            - "I need medical care" (when someone asks for help)
            
            {chat_history}
            
            Doctor: {message}
            """)

            # Create the chain with memory and parse JSON
            from langchain_core.output_parsers import JsonOutputParser
            parser = JsonOutputParser(pydantic_object=ChatEmotionOutput)
            chain_parsed = prompt | self.llm | parser
            chain_text = prompt | self.llm

            # Build explicit role-tagged history for clarity
            history_lines: List[str] = []
            for m in memory.chat_memory.messages:
                if isinstance(m, HumanMessage):
                    history_lines.append(f"Doctor: {m.content}")
                elif isinstance(m, AIMessage):
                    history_lines.append(f"Patient: {m.content}")
            history_text = "\n".join(history_lines)

            # Get response from LangChain with memory
            inputs = {
                "case_id": case_id,
                "patient_name": case.get('name', 'Unknown'),
                "chief_complaint": case.get('chief_complaint', 'Unknown'),
                "history": case.get('history_of_present_illness', 'Unknown'),
                "age": demographics.get('age', 'Unknown'),
                "gender": demographics.get('gender', 'Unknown'),
                "pmh": pmh,
                "medications": meds or 'None',
                "allergies": allergies or 'None',
                "social_history": social,
                "family_history": family,
                "vital_signs": json.dumps(vitals or {}),
                "personality_traits": ", ".join(personality_traits),
                "behavioral_settings": json.dumps(case.get('behavioral_settings', {})),
                "style_instructions": style_instructions,
                "chat_history": history_text,
                "message": message,
                "format_instructions": parser.get_format_instructions(),
            }
            try:
                result = await chain_parsed.ainvoke(inputs)
            except Exception:
                # Fallback: get raw text and extract JSON object
                raw = await chain_text.ainvoke(inputs)
                text = getattr(raw, "content", raw)
                # Extract first JSON object
                match = re.search(r"\{[\s\S]*\}", text)
                data = {}
                if match:
                    try:
                        data = json.loads(match.group(0))
                    except Exception:
                        # Attempt to fix common issues (single quotes -> double quotes)
                        try:
                            data = json.loads(match.group(0).replace("'", '"'))
                        except Exception:
                            data = {}
                result = data

            # Extract fields
            reply_text = (result.get("reply") or "").strip() if isinstance(result, dict) else ""
            emotion_text = (result.get("emotion") or "").strip() if isinstance(result, dict) else ""

            # If model produced empty reply, ask LLM once more with a stricter repair prompt
            if not reply_text:
                repair_prompt = ChatPromptTemplate.from_template(
                    """
                    You must return JSON ONLY (no prose, no backticks) that matches this schema exactly:
                    {format_instructions}

                    Requirements:
                    - reply must be non-empty text in the patient's voice
                    - Use the provided profile values verbatim when asked (Age: {age}, Gender: {gender}, PMH: {pmh}, Meds: {medications}, Allergies: {allergies})

                    Profile:
                    Case ID: {case_id}; Name: {patient_name}; CC: {chief_complaint}; Hx: {history};
                    Age: {age}; Gender: {gender}; PMH: {pmh}; Meds: {medications}; Allergies: {allergies};
                    Social: {social_history}; Family: {family_history}; Vitals: {vital_signs}

                    Chat so far:
                    {chat_history}

                    Doctor: {message}
                    """
                )
                repair_chain = repair_prompt | self.llm | parser
                try:
                    repaired = await repair_chain.ainvoke({
                        **inputs,
                        "format_instructions": parser.get_format_instructions(),
                    })
                    reply_text = (repaired.get("reply") or "").strip()
                    emotion_text = (repaired.get("emotion") or emotion_text or "").strip()
                except Exception:
                    # If repair also fails, try raw text and JSON extract again
                    raw2 = await chain_text.ainvoke(inputs)
                    text2 = getattr(raw2, "content", raw2)
                    match2 = re.search(r"\{[\s\S]*\}", text2)
                    if match2:
                        try:
                            data2 = json.loads(match2.group(0))
                            reply_text = (data2.get("reply") or reply_text or "").strip()
                            emotion_text = (data2.get("emotion") or emotion_text or "").strip()
                        except Exception:
                            pass

            # Enforce first-person voice and profile consistency if needed
            reply_text = self._enforce_first_person_and_profile_consistency(case, reply_text, style_instructions)
            # If repeating previous assistant content, rewrite to directly answer
            prev_assistant = ""
            if memory.chat_memory.messages:
                for m in reversed(memory.chat_memory.messages):
                    if isinstance(m, AIMessage):
                        prev_assistant = m.content or ""
                        break
            if self._is_repetitive(prev_assistant, reply_text):
                # First try a deterministic factoid answer
                fact = self._try_factoid_answer(case, message)
                if fact:
                    reply_text = fact
                else:
                    reply_text = self._rewrite_direct_answer(case, message, reply_text, style_instructions)
            # Reconcile emotion with profile and content
            emotion_text = self._reconcile_emotion(case, reply_text, emotion_text)

            # Add the conversation to memory
            self._add_to_memory(key, message, reply_text)

            # Check if this is a final response
            content = reply_text
            # Remove accidental speaker labels that models occasionally prepend
            content = re.sub(r"^(?:Patient|Doctor|Assistant)\s*:\s*", "", content, flags=re.IGNORECASE)
            is_final = any(keyword in content.lower() for keyword in 
                         ["discharge", "diagnosis confirmed", "treatment plan", "goodbye", "thank you doctor"])

            return ChatResponse(
                case_id=case_id,
                message=content,
                is_final=is_final,
                emotion=emotion_text or None,
            )

        except Exception as e:
            logger.error("Error in chat with patient: %s", str(e), exc_info=True)
            raise

    def clear_conversation_memory(self, key: str):
        """Clear the conversation memory for a specific key (conversation/session or case)."""
        if key in self.conversation_memories:
            del self.conversation_memories[key]
            logger.info(f"Cleared conversation memory for key: {key}")

    def get_conversation_history(self, key: str) -> List[Dict[str, str]]:
        """Get the conversation history for a specific key (conversation/session or case)."""
        if key in self.conversation_memories:
            memory = self.conversation_memories[key]
            return [
                {"role": "user", "content": msg.content} if isinstance(msg, HumanMessage) else {"role": "assistant", "content": msg.content}
                for msg in memory.chat_memory.messages
            ]
        return []
