from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = datetime.now()

class ChatRequest(BaseModel):
    case_id: str
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    case_id: str
    message: str
    timestamp: datetime = datetime.now()
    is_final: bool = False  # Indicates if this is the final response in the chat
    session_id: Optional[str] = None
    emotion: Optional[str] = None