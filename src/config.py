"""
Configuration management for Prompt Forge Studio
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""

    # API Configuration
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "claude-sonnet-4-5-20250929")
    ANALYSIS_MODEL: str = os.getenv("ANALYSIS_MODEL", "claude-sonnet-4-5-20250929")

    # API Limits
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "4096"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "1.0"))
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 2.0  # seconds

    # Database
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "./promptforge.db")

    # App Settings
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    APP_NAME: str = "Prompt Forge Studio"
    APP_VERSION: str = "0.1.0"

    @classmethod
    def validate(cls) -> bool:
        """Validate critical configuration"""
        if not cls.ANTHROPIC_API_KEY:
            return False
        return True

    @classmethod
    def set_api_key(cls, api_key: str):
        """Set API key at runtime"""
        cls.ANTHROPIC_API_KEY = api_key
        os.environ["ANTHROPIC_API_KEY"] = api_key

config = Config()
