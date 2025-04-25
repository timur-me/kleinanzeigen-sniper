import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Type, TypeVar, Union

from loguru import logger
from pydantic import BaseModel

from app.config.settings import settings
from app.models.models import Item, SearchSettings, User

T = TypeVar('T', bound=BaseModel)


class JSONStorage:
    """JSON file-based storage for models."""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Make sure the JSON file exists, create it if it doesn't."""
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump([], f)
    
    def _read_all(self) -> List[Dict]:
        """Read all items from the JSON file."""
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error reading from {self.file_path}: {e}")
            return []
    
    def _write_all(self, items: List[Dict]):
        """Write all items to the JSON file."""
        try:
            with open(self.file_path, 'w') as f:
                json.dump(items, f, default=self._json_serializer, indent=2)
        except Exception as e:
            logger.error(f"Error writing to {self.file_path}: {e}")
    
    def _json_serializer(self, obj):
        """Custom JSON serializer to handle datetime objects."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")
    
    def get_all(self, model_class: Type[T]) -> List[T]:
        """Get all items from storage and convert to model instances."""
        items = self._read_all()
        return [model_class(**item) for item in items]
    
    def get_by_id(self, model_class: Type[T], id_field: str, id_value: Union[str, int]) -> Optional[T]:
        """Get a specific item by its ID."""
        items = self._read_all()
        for item in items:
            if item.get(id_field) == id_value:
                return model_class(**item)
        return None
    
    def save(self, model: BaseModel, id_field: str) -> BaseModel:
        """Save a model to storage (create or update)."""
        items = self._read_all()
        
        # Check if item exists
        id_value = getattr(model, id_field)
        for i, item in enumerate(items):
            if item.get(id_field) == id_value:
                # Update
                items[i] = model.model_dump()
                self._write_all(items)
                return model
        
        # Create new
        items.append(model.model_dump())
        self._write_all(items)
        return model
    
    def delete(self, id_field: str, id_value: Union[str, int]) -> bool:
        """Delete an item by its ID."""
        items = self._read_all()
        new_items = [item for item in items if item.get(id_field) != id_value]
        
        if len(new_items) < len(items):
            self._write_all(new_items)
            return True
        return False


class UserStorage(JSONStorage):
    """Storage for User models."""
    
    def __init__(self):
        super().__init__(settings.USERS_FILE)
    
    def get_all(self) -> List[User]:
        return super().get_all(User)
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        return super().get_by_id(User, "user_id", user_id)
    
    def save(self, user: User) -> User:
        return super().save(user, "user_id")
    
    def delete(self, user_id: int) -> bool:
        return super().delete("user_id", user_id)


class SearchSettingsStorage(JSONStorage):
    """Storage for SearchSettings models."""
    
    def __init__(self):
        super().__init__(settings.SEARCH_SETTINGS_FILE)
    
    def get_all(self) -> List[SearchSettings]:
        return super().get_all(SearchSettings)
    
    def get_by_id(self, setting_id: str) -> Optional[SearchSettings]:
        return super().get_by_id(SearchSettings, "id", setting_id)
    
    def get_by_user_id(self, user_id: int) -> List[SearchSettings]:
        all_settings = self.get_all()
        return [s for s in all_settings if s.user_id == user_id]
    
    def save(self, settings: SearchSettings) -> SearchSettings:
        return super().save(settings, "id")
    
    def delete(self, setting_id: str) -> bool:
        return super().delete("id", setting_id)


class ItemStorage(JSONStorage):
    """Storage for Item models."""
    
    def __init__(self):
        super().__init__(settings.ITEMS_FILE)
    
    def get_all(self) -> List[Item]:
        return super().get_all(Item)
    
    def get_by_id(self, item_id: str) -> Optional[Item]:
        return super().get_by_id(Item, "id", item_id)
    
    def save(self, item: Item) -> Item:
        return super().save(item, "id")
    
    def delete(self, item_id: str) -> bool:
        return super().delete("id", item_id)
    
    def get_unsent_for_user(self, user_id: int) -> List[Item]:
        """Get items that haven't been sent to a specific user."""
        all_items = self.get_all()
        return [item for item in all_items if not item.is_sent_to(user_id)]


# Singleton instances
user_storage = UserStorage()
search_settings_storage = SearchSettingsStorage()
item_storage = ItemStorage() 