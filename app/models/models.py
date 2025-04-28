from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

from app.kleinanzeigen.models import KleinanzeigenItem


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
    was_used: bool = False
    
    def mark_as_used(self):
        """Mark search as used."""
        self.was_used = True
        self.updated_at = datetime.now()
    
    @field_validator('radius_km')
    def validate_radius(cls, v):
        """Validate radius is within reasonable bounds."""
        if not isinstance(v, int):
            try:
                v = int(v)
            except ValueError:
                raise ValueError("Radius must be an integer")
        
        if v < 0:
            return 0

        return v


class Item(BaseModel):
    """Model for storing Kleinanzeigen items."""
    
    id: str  # ID from Kleinanzeigen
    raw_data: Dict[str, Any]  # Raw data from Kleinanzeigen API
    first_seen: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    
    def to_kleinanzeigen_item(self) -> KleinanzeigenItem:
        """Convert raw data to KleinanzeigenItem object."""
        return KleinanzeigenItem(self.raw_data)


class Notification(BaseModel):
    """Model for tracking item notifications to users."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    item_id: str  # ID of the Kleinanzeigen item
    user_id: int  # ID of the user to notify
    search_id: str  # ID of the search that found the item
    is_sent: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    sent_at: Optional[datetime] = None
    
    def mark_as_sent(self):
        """Mark notification as sent."""
        self.is_sent = True
        self.sent_at = datetime.now()


class ItemNotification(BaseModel):
    """Model for storing item data and its notification status."""
    
    item: KleinanzeigenItem
    notifications: List[Notification] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def add_notification(self, user_id: int, search_id: str) -> Notification:
        """Add a new notification for a user."""
        notification = Notification(
            item_id=self.item.id,
            user_id=user_id,
            search_id=search_id
        )
        self.notifications.append(notification)
        return notification

    def get_pending_notifications(self) -> List[Notification]:
        """Get all pending notifications."""
        return [n for n in self.notifications if not n.is_sent]

    def get_sent_notifications(self) -> List[Notification]:
        """Get all sent notifications."""
        return [n for n in self.notifications if n.is_sent] 