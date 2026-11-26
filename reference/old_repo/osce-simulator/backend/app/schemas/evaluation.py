from pydantic import BaseModel
from typing import Optional

class EvaluationRequest(BaseModel):
    case_id: str
    conversation_id: str
    notes: Optional[str] = None
    time_taken: Optional[int] = None