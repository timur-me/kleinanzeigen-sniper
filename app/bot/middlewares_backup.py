from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from loguru import logger

from app.config.settings import settings
from app.models.models import User
from app.services.storage import user_storage


class UserAccessMiddleware(BaseMiddleware):
    """Middleware to check user access and register new users."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        """Handle middleware logic."""
        # Get user ID from message
        user = event.from_user
        if not user:
            # No user in event, skip middleware
            return await handler(event, data)
        
        user_id = user.id
        
        # Check if user is in admin list for admin-only commands
        is_admin = user_id in settings.ADMIN_USER_IDS
        
        # Check if this is an admin-only command
        text = getattr(event, "text", "")
        if text and text.startswith("/admin") and not is_admin:
            logger.warning(f"User {user_id} tried to access admin command: {text}")
            await event.answer("❌ You don't have permission to use this command.")
            return None
        
        # Check if user exists in the database
        existing_user = user_storage.get_by_id(user_id)
        
        if not existing_user:
            # Create new user
            new_user = User(
                user_id=user_id,
                username=user.username,
                first_name=user.first_name, 
                last_name=user.last_name,
                is_admin=is_admin
            )
            
            user_storage.save(new_user)
            logger.info(f"New user registered: {new_user.full_name()} (ID: {user_id})")
        else:
            # Update user data if changed
            has_changes = False
            
            if existing_user.username != user.username:
                existing_user.username = user.username
                has_changes = True
                
            if existing_user.first_name != user.first_name:
                existing_user.first_name = user.first_name
                has_changes = True
                
            if existing_user.last_name != user.last_name:
                existing_user.last_name = user.last_name
                has_changes = True
                
            if has_changes:
                user_storage.save(existing_user)
                logger.debug(f"Updated user data for {existing_user.full_name()} (ID: {user_id})")
        
        # Continue processing
        return await handler(event, data) 
    
