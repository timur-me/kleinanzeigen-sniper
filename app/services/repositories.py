from typing import List, Optional

from app.config.settings import settings
from app.models.models import Item, Notification, SearchSettings, User
from app.services.repository import JSONRepository


class UserRepository(JSONRepository[User]):
    """Repository for User models."""
    
    def __init__(self):
        super().__init__(settings.USERS_FILE, User, "user_id")
    
    def get_active_users(self) -> List[User]:
        """Get all active users."""
        return [user for user in self.get_all() if user.is_active]


class SearchSettingsRepository(JSONRepository[SearchSettings]):
    """Repository for SearchSettings models."""
    
    def __init__(self):
        super().__init__(settings.SEARCH_SETTINGS_FILE, SearchSettings)
    
    def get_by_id(self, uuid: str) -> Optional[SearchSettings]:
        """Get a search settings by its UUID."""
        return next((s for s in self.get_all() if s.id == uuid), None)
    
    def get_by_user_id(self, user_id: int) -> List[SearchSettings]:
        """Get all search settings for a specific user."""
        return [s for s in self.get_all() if s.user_id == user_id]
    
    def get_active_searches(self) -> List[SearchSettings]:
        """Get all active search settings."""
        return [s for s in self.get_all() if s.is_active]


class ItemRepository(JSONRepository[Item]):
    """Repository for Item models."""
    
    def __init__(self):
        super().__init__(settings.ITEMS_FILE, Item)
    
    def get_or_create_by_kleinanzeigen_id(self, item_id: str, data: dict) -> Item:
        """Get an existing item or create a new one if it doesn't exist."""
        item = self.get_by_id(item_id)
        
        if item:
            # Update existing item
            item.raw_data = data
            item.last_updated = settings.NOW()
            return self.save(item)
        
        # Create new item
        new_item = Item(id=item_id, raw_data=data)
        return self.save(new_item)


class NotificationRepository(JSONRepository[Notification]):
    """Repository for Notification models."""
    
    def __init__(self):
        super().__init__(settings.NOTIFICATIONS_FILE, Notification)
    
    def get_pending_notifications(self) -> List[Notification]:
        """Get all pending notifications."""
        return [n for n in self.get_all() if not n.is_sent]
    
    def get_pending_notifications_for_user(self, user_id: int) -> List[Notification]:
        """Get pending notifications for a specific user."""
        return [n for n in self.get_all() if not n.is_sent and n.user_id == user_id]
    
    def create_notification_if_not_exists(self, item_id: str, user_id: int, search_id: str, sent: bool = False) -> Optional[Notification]:
        """Create a notification if it doesn't already exist."""
        # Check if notification already exists
        for notification in self.get_all():
            if (notification.item_id == item_id and 
                notification.user_id == user_id and 
                notification.search_id == search_id):
                return None  # Notification already exists
        
        # Create new notification
        notification = Notification(
            item_id=item_id,
            user_id=user_id,
            search_id=search_id,
            is_sent=sent
        )
        return self.save(notification)


# Create singleton instances
user_repository = UserRepository()
search_settings_repository = SearchSettingsRepository()
item_repository = ItemRepository()
notification_repository = NotificationRepository() 