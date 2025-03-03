"""Application configuration module."""
import os
import logging
from typing import List
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings:
    """Application settings."""
    
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "EXIF Checker API"
    PROJECT_DESCRIPTION: str = "API for checking and extracting EXIF data from images"
    VERSION: str = "1.0.0"
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # File settings
    # Hardcoded to 50MB to ensure this is the value used
    MAX_FILE_SIZE: float = 50.0  # in MB
    TEMP_DIR: Path = Path(os.getenv("TEMP_DIR", "temp_uploads"))
    
    # Static file settings
    STATIC_DIR: Path = BASE_DIR / "frontend" / "static"
    
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    def __init__(self):
        # Parse ALLOWED_ORIGINS from environment
        origins = os.getenv("ALLOWED_ORIGINS", "*")
        if origins == "*":
            self.ALLOWED_ORIGINS = ["*"]
        else:
            self.ALLOWED_ORIGINS = origins.split(",")
        
        # Force MAX_FILE_SIZE to be 50MB regardless of environment
        self.MAX_FILE_SIZE = 50.0

    def get_log_level(self) -> int:
        """Convert string log level to logging constant."""
        log_levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        return log_levels.get(self.LOG_LEVEL.upper(), logging.INFO)


# Create settings instance
settings = Settings() 