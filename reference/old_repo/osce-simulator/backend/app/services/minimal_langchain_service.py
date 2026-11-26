from .minimal_chat_service import MinimalChatService
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class MinimalLangChainService:
    """Minimal LangChain service with just chat functionality."""
    
    def __init__(self):
        # Initialize only the minimal chat service
        self.chat_service = MinimalChatService()
        logger.info("Minimal LangChain service initialized")

    async def chat_with_patient(self, message: str) -> str:
        """Minimal chat with patient - just prompt and raw LLM response."""
        return await self.chat_service.chat_with_patient(message)
