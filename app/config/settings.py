import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Callable

from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()

# Project root directory
ROOT_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    """Application settings"""
    
    # Bot settings
    BOT_TOKEN: str
    ADMIN_USER_IDS: List[int]
    
    # Kleinanzeigen settings
    KLEINANZEIGEN_API_URL: str = "https://www.kleinanzeigen.de"
    KLEINANZEIGEN_AUTH_TOKEN: str = None
    REQUEST_INTERVAL: int = 30  # seconds
    NOTIFICATION_INTERVAL: int = 60  # seconds
    
    # Logging
    LOG_DIR: Path = ROOT_DIR / "logs"
    LOG_LEVEL: str = "INFO"

    # Database settings
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "kleinanzeigen-sniper"

    # Scan settings
    KLEINANZEIGEN_CONCURRENT_REQUESTS_FOR_SCAN: int = 5
    KLEINANZEIGEN_MAX_ITEMS_PER_PAGE: int = 10
    
    @field_validator("ADMIN_USER_IDS", mode="before")
    def validate_admin_ids(cls, v):
        """Parse JSON string to list if needed"""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # Try to parse comma-separated string
                return [int(x.strip()) for x in v.split(",")]
        return v
    
    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


    class Config:
        env_file = ".env"
        case_sensitive = True
    
    # Helper function to get current time (useful for testing)
    @property
    def NOW(self) -> Callable[[], datetime]:
        return datetime.now


# Create instance of settings
settings = Settings()

# Ensure data and log directories exist
os.makedirs(settings.LOG_DIR, exist_ok=True) 