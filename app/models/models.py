from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, validator


class User(BaseModel):
    """User model for storing Telegram user information."""
    
    user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_admin: bool = False
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    def full_name(self) -> str:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.username:
            return self.username
        return str(self.user_id)


class SearchSettings(BaseModel):
    """Search settings model for storing user's search preferences."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: int
    item_name: str
    location: str
    radius_km: int = 10
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    @validator('radius_km')
    def validate_radius(cls, v):
        """Validate radius is within reasonable bounds."""
        if v < 0:
            return 0
        if v > 100:
            return 100
        return v


class Item(BaseModel):
    """Item model for storing information about items found on Kleinanzeigen."""
    
    id: str
    title: str
    description: Optional[str] = None
    price: Optional[str] = None
    location: Optional[str] = None
    url: str
    image_urls: List[str] = []
    is_sent: Dict[int, bool] = {}  # Maps user_id to whether the item has been sent to them
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    def mark_as_sent(self, user_id: int):
        """Mark item as sent to a specific user."""
        self.is_sent[str(user_id)] = True
        self.updated_at = datetime.now()
    
    def is_sent_to(self, user_id: int) -> bool:
        """Check if item has been sent to a specific user."""
        return self.is_sent.get(str(user_id), False) 