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
    USER_AGENTS_FILE: str = "user_agents.txt"
    
    # JSON storage settings
    DATA_DIR: Path = ROOT_DIR / "data"
    USERS_FILE: Path = DATA_DIR / "users.json"
    SEARCH_SETTINGS_FILE: Path = DATA_DIR / "search_settings.json"
    ITEMS_FILE: Path = DATA_DIR / "items.json"
    NOTIFICATIONS_FILE: Path = DATA_DIR / "notifications.json"
    
    # Logging
    LOG_DIR: Path = ROOT_DIR / "logs"
    LOG_LEVEL: str = "INFO"

    # Database settings
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "kleinanzeigen-sniper"
    
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
os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(settings.LOG_DIR, exist_ok=True) 