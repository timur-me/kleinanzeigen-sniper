from aiogram import Bot
from loguru import logger

from app.builders.message_builder import SingleKleinanzeigenItemMessageBuilder
from app.db.models import Notification, User
from app.db.repositories import (
    ItemRepository, 
    NotificationRepository, 
    UserRepository,
)
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
            repo = NotificationRepository(session)
            notifications = await repo.get_pending_notifications_for_user(user.user_id)
        
        if not notifications:
            return
        
        logger.info(f"Sending {len(notifications)} notifications to user {user.user_id} ({user.full_name()})")
        
        for notification in notifications:
            success = await self.send_notification(bot, user, notification)
            
            if success:
                # Mark as sent
                notification.mark_as_sent()
                await repo.save(notification)
    
    async def send_notification(self, bot: Bot, user: User, notification: Notification) -> bool:
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
            message_builder = SingleKleinanzeigenItemMessageBuilder(kleinanzeigen_item)
            
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
            logger.error(f"Error sending notification {notification.id} to user {user.user_id}: {e}")
            return False


# Create singleton instance
notification_service = NotificationService() 