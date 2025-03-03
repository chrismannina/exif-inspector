"""Application configuration module."""
import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Application settings using Pydantic for validation and type checking."""

    # API settings
    api_v1_str: str = "/api/v1"
    project_name: str = "EXIF Checker API"
    project_description: str = "API for checking and extracting EXIF data from images"
    version: str = "1.0.0"

    # CORS settings - parse comma-separated string from .env
    allowed_origins_str: str = Field(default="*", alias="ALLOWED_ORIGINS")

    # Environment
    environment: str = Field(default="development")

    # File settings
    # Hardcoded to 50MB to ensure this is the value used
    max_file_size: float = Field(default=50.0, description="Maximum file size in MB")
    temp_dir: Path = Field(
        default=Path("temp_uploads"), description="Directory for temporary files"
    )

    # Static file settings
    static_dir: Path = Field(
        default=BASE_DIR / "frontend" / "static",
        description="Directory for static files",
    )

    # Server settings
    host: str = Field(default="0.0.0.0", description="Host to bind the server to")
    port: int = Field(default=8000, description="Port to bind the server to")

    # Logging settings
    log_level: str = Field(default="INFO", description="Logging level")

    # Model configuration
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    def get_log_level(self) -> int:
        """
        Convert string log level to logging module constant.

        Returns:
            int: The logging level as a constant from the logging module
        """
        levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        return levels.get(self.log_level.upper(), logging.INFO)

    @property
    def allowed_origins(self) -> List[str]:
        """
        Parse allowed origins from string to list.

        Returns:
            List[str]: List of allowed origins for CORS
        """
        if self.allowed_origins_str == "*":
            return ["*"]
        return [origin.strip() for origin in self.allowed_origins_str.split(",")]


# Create settings instance
settings = Settings()


# Define uppercase aliases for backward compatibility
# This approach allows access through both settings.api_v1_str and settings.API_V1_STR
class SettingsProxy:
    def __init__(self, settings_instance):
        self._settings = settings_instance

    def __getattr__(self, name):
        # Try to get the lowercase version if uppercase is requested
        if name.isupper():
            lowercase_name = name.lower()
            if hasattr(self._settings, lowercase_name):
                return getattr(self._settings, lowercase_name)

            # Special case for allowed_origins which uses a property
            if name == "ALLOWED_ORIGINS":
                return self._settings.allowed_origins

        # Fall back to the actual settings instance
        return getattr(self._settings, name)


# Replace the settings instance with our proxy
settings = SettingsProxy(settings)
