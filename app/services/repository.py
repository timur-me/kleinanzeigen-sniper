import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generic, List, Optional, Protocol, Type, TypeVar, Union

from loguru import logger
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


class Repository(Protocol[T]):
    """Base repository protocol for all repositories."""
    
    def get_all(self) -> List[T]:
        """Get all items."""
        ...
    
    def get_by_id(self, id_value: Any) -> Optional[T]:
        """Get an item by its ID."""
        ...
    
    def save(self, item: T) -> T:
        """Save an item (create or update)."""
        ...
    
    def delete(self, id_value: Any) -> bool:
        """Delete an item by its ID."""
        ...


class JSONRepository(Generic[T]):
    """JSON file-based repository implementation."""
    
    def __init__(self, file_path: Path, model_class: Type[T], id_field: str = "id"):
        self.file_path = file_path
        self.model_class = model_class
        self.id_field = id_field
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
    
    def get_all(self) -> List[T]:
        """Get all items from storage and convert to model instances."""
        items = self._read_all()
        return [self.model_class.model_validate(item) for item in items]
    
    def get_by_id(self, id_value: Any) -> Optional[T]:
        """Get a specific item by its ID."""
        items = self._read_all()
        for item in items:
            if item.get(self.id_field) == id_value:
                return self.model_class.model_validate(item)
        return None
    
    def save(self, item: T) -> T:
        """Save a model to storage (create or update)."""
        items = self._read_all()
        
        # Check if item exists
        id_value = getattr(item, self.id_field)
        for i, existing_item in enumerate(items):
            if existing_item.get(self.id_field) == id_value:
                # Update
                items[i] = item.model_dump()
                self._write_all(items)
                return item
        
        # Create new
        items.append(item.model_dump())
        self._write_all(items)
        return item
    
    def delete(self, id_value: Any) -> bool:
        """Delete an item by its ID."""
        items = self._read_all()
        new_items = [item for item in items if item.get(self.id_field) != id_value]
        
        if len(new_items) < len(items):
            self._write_all(new_items)
            return True
        return False 