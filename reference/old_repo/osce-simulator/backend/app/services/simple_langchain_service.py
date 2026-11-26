from .patient_service import PatientService
from .simple_chat_service import SimpleChatService
from .evaluation_service import EvaluationService
from ..schemas.patient import PatientCase
from ..schemas.chat import ChatMessage, ChatResponse
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class SimpleLangChainService:
    """Simplified LangChain service with only core functionality."""
    
    def __init__(self):
        # Initialize all sub-services
        self.patient_service = PatientService()
        self.chat_service = SimpleChatService()
        self.evaluation_service = EvaluationService()
        
        # Share patient cases between services
        self.patient_cases = self.patient_service.patient_cases
        self.chat_service.patient_cases = self.patient_cases
        self.evaluation_service.patient_cases = self.patient_cases
        
        # Share conversation memories between services
        self.conversation_memories = self.patient_service.conversation_memories
        self.chat_service.conversation_memories = self.conversation_memories
        self.evaluation_service.conversation_memories = self.conversation_memories
        
        logger.info("Simple LangChain service initialized with all sub-services")

    # Patient service methods
    async def generate_patient_case(self, difficulty: str, age: int, gender: str, personality_traits: list, behavioral_settings: dict) -> PatientCase:
        """Generate a new patient case."""
        return await self.patient_service.generate_patient_case(difficulty, age, gender, personality_traits, behavioral_settings)

    async def get_patient_case(self, case_id: str) -> PatientCase:
        """Retrieve a patient case by ID."""
        return await self.patient_service.get_patient_case(case_id)

    # Chat service methods
    async def chat_with_patient(self, case_id: str, message: str, chat_history: List[ChatMessage] = None, memory_key: Optional[str] = None) -> ChatResponse:
        """Simplified chat with a patient - only core prompt and LLM call."""
        return await self.chat_service.chat_with_patient(case_id, message, chat_history, memory_key)

    # Evaluation service methods
    async def evaluate_response(self, case_id: str, response: str) -> Dict[str, Any]:
        """Evaluate a student's response to a patient case."""
        return await self.evaluation_service.evaluate_response(case_id, response)

    async def evaluate_performance(self, *, case: Optional[dict], conversation: dict, notes: Optional[str]) -> Dict[str, Any]:
        """LLM-based rubric evaluation using conversation transcript and optional notes."""
        return await self.evaluation_service.evaluate_performance(case=case, conversation=conversation, notes=notes)

    # Memory management methods
    def clear_conversation_memory(self, key: str):
        """Clear the conversation memory for a specific key."""
        self.patient_service.clear_conversation_memory(key)
        self.chat_service.clear_conversation_memory(key)
        self.evaluation_service.clear_conversation_memory(key)

    def get_conversation_history(self, key: str) -> List[Dict[str, str]]:
        """Get the conversation history for a specific key."""
        return self.patient_service.get_conversation_history(key)

    def _get_or_create_memory(self, memory_key: str):
        """Get or create a conversation memory for a specific key."""
        return self.patient_service._get_or_create_memory(memory_key)

    def _ensure_complete_case(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fill any missing PatientCase required fields with sensible defaults."""
        return self.patient_service._ensure_complete_case(data)
