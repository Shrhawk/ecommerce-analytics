from typing import Any, Dict, Optional
from pydantic_settings import BaseSettings

from pydantic import PostgresDsn


class Settings(BaseSettings):
    """
    Application settings.
    
    This class handles all configuration settings for the application,
    including database connection, API settings, and other environment variables.
    """
    
    PROJECT_NAME: str = "E-commerce Analytics API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    SQLALCHEMY_DATABASE_URI: str

    # Debug settings
    SQL_ECHO: bool = False

    class Config:
        case_sensitive = True
        env_file = ".env"


# Create settings instance
settings = Settings() 