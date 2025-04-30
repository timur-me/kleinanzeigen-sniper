import asyncio
from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter
from loguru import logger

from app.builders.message_builder import SingleKleinanzeigenItemMessageBuilder
from app.db.models import Notification, SearchSettings, User
from app.db.repositories import (
    ItemRepository, 
    NotificationRepository, 
    UserRepository,
)
from app.services import SearchSettingsService
from app.db.database import async_session


class NotificationService:
    """Service for sending notifications about new items to users."""
    
    def __init__(self):
        pass
    
    async def send_pending_notifications(self, bot: Bot):
        """Send all pending notifications to users."""
        # Get all active users
        async with async_session() as session:
            repo = UserRepository(session)
            users = await repo.get_active_users()
        
        for user in users:
            await self.send_notifications_for_user(bot, user)
    
    async def send_notifications_for_user(self, bot: Bot, user: User):
        """Send pending notifications for a specific user."""
        # Get pending notifications for this user
        async with async_session() as session:
            notification_repo = NotificationRepository(session)
            search_settings_repo = SearchSettingsService(session)

            notifications = await notification_repo.get_pending_notifications_for_user(user.user_id)
        
            if not notifications:
                return
            
            logger.info(f"Sending {len(notifications)} notifications to user {user.user_id} ({user.full_name()})")
            
            for notification in notifications:
                search_settings = await search_settings_repo.get_by_id(notification.search_id)
                try:
                    success = await self.send_notification(bot, user, notification, search_settings)
                except TelegramRetryAfter as e:
                    logger.error(f"Flood limits exceeded. Retrying in {e.retry_after} seconds.")
                    await asyncio.sleep(e.retry_after)
                    success = False
                except Exception as e:
                    logger.error(f"Error sending notification {notification.id} to user {user.user_id}: {e}")
                    success = False
                
                if success:
                    # Mark as sent
                    notification.mark_as_sent()
                    await notification_repo.save(notification)
    
    async def send_notification(self, bot: Bot, user: User, notification: Notification, search_settings: SearchSettings) -> bool:
        """Send a single notification to a user."""
        try:
            # Get the item
            async with async_session() as session:
                repo = ItemRepository(session)
                item = await repo.get_by_id(notification.item_id)

            if not item:
                logger.error(f"Item {notification.item_id} not found for notification {notification.id}")
                return False
            
            # Convert to KleinanzeigenItem for display
            kleinanzeigen_item = item.to_kleinanzeigen_item()
            
            # Create message
            message_builder = SingleKleinanzeigenItemMessageBuilder(kleinanzeigen_item, search_settings)
            
            # Send message with media if available
            if message_builder.message_media:
                # Send media group
                await bot.send_media_group(
                    chat_id=user.user_id,
                    media=message_builder.message_media
                )
            else:
                # No media, send text only
                await bot.send_message(
                    chat_id=user.user_id,
                    text=message_builder.message_text,
                    parse_mode="Markdown"
                )
            
            logger.debug(f"Notification {notification.id} sent to user {user.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending notification {notification.id} to user {user.user_id}: {e}, msg: {message_builder.message_text}")
            return False


# Create singleton instance
notification_service = NotificationService() 