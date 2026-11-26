from pydantic_settings import BaseSettings
from typing import Optional, List
from functools import lru_cache
import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Ensure .env file is loaded
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
logger.debug(f"Looking for .env file at: {dotenv_path}")
load_dotenv(dotenv_path)

class Settings(BaseSettings):
    PROJECT_NAME: str = "OSCE Simulator API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = None
    
    # Database Configuration
    DATABASE_URL: Optional[str] = None
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Server Configuration
    PORT: int = 8000
    NODE_ENV: str = "development"
    
    class Config:
        case_sensitive = True
        env_file = dotenv_path
        extra = "allow"  # Allow extra fields in the settings

@lru_cache()
def get_settings() -> Settings:
    logger.debug("Loading settings from environment...")
    logger.debug(f"Current working directory: {os.getcwd()}")
    
    # Log environment variables for debugging (without sensitive values)
    env_vars = {k: v[:4] + '...' if k == 'OPENAI_API_KEY' and v else v 
                for k, v in os.environ.items() if k.startswith('OPENAI_') or k in ['PROJECT_NAME', 'VERSION', 'API_V1_STR']}
    logger.debug(f"Environment variables: {env_vars}")
    
    # Load settings directly from environment variables first
    openai_key = os.environ.get('OPENAI_API_KEY')
    
    settings = Settings()
    
    # Override with environment value if present
    if openai_key:
        settings.OPENAI_API_KEY = openai_key
        logger.debug(f"Using OPENAI_API_KEY from environment variables")
    
    logger.debug("Settings loaded:")
    logger.debug(f"OPENAI_API_KEY present: {'Yes' if settings.OPENAI_API_KEY else 'No'}")
    logger.debug(f"OPENAI_API_KEY length: {len(settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else 0}")
    logger.debug(f"OPENAI_API_KEY first 4 chars: {settings.OPENAI_API_KEY[:4] if settings.OPENAI_API_KEY else 'None'}")
    
    return settings 