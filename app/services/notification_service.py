from aiogram import Bot
from loguru import logger

from app.builders.message_builder import SingleItemMessageBuilder
from app.bot.keyboards import get_item_link_keyboard
from app.models.models import Notification, User
from app.services.repositories import (
    ItemRepository, 
    NotificationRepository, 
    UserRepository,
    item_repository,
    notification_repository,
    user_repository
)


class NotificationService:
    """Service for sending notifications about new items to users."""
    
    def __init__(
        self,
        item_repo: ItemRepository = item_repository,
        notification_repo: NotificationRepository = notification_repository,
        user_repo: UserRepository = user_repository
    ):
        self.item_repo = item_repo
        self.notification_repo = notification_repo
        self.user_repo = user_repo
    
    async def send_pending_notifications(self, bot: Bot):
        """Send all pending notifications to users."""
        # Get all active users
        users = self.user_repo.get_active_users()
        
        for user in users:
            await self.send_notifications_for_user(bot, user)
    
    async def send_notifications_for_user(self, bot: Bot, user: User):
        """Send pending notifications for a specific user."""
        # Get pending notifications for this user
        notifications = self.notification_repo.get_pending_notifications_for_user(user.user_id)
        
        if not notifications:
            return
        
        logger.info(f"Sending {len(notifications)} notifications to user {user.user_id} ({user.full_name()})")
        
        for notification in notifications:
            success = await self.send_notification(bot, user, notification)
            
            if success:
                # Mark as sent
                notification.mark_as_sent()
                self.notification_repo.save(notification)
    
    async def send_notification(self, bot: Bot, user: User, notification: Notification) -> bool:
        """Send a single notification to a user."""
        try:
            # Get the item
            item = self.item_repo.get_by_id(notification.item_id)
            if not item:
                logger.error(f"Item {notification.item_id} not found for notification {notification.id}")
                return False
            
            # Convert to KleinanzeigenItem for display
            kleinanzeigen_item = item.to_kleinanzeigen_item()
            
            # Create message
            message_builder = SingleItemMessageBuilder(kleinanzeigen_item)
            
            # Create keyboard
            keyboard = get_item_link_keyboard(kleinanzeigen_item.ad_link)
            
            # Send message with media if available
            if message_builder.message_media:
                # Send media group
                await bot.send_media_group(
                    chat_id=user.user_id,
                    media=message_builder.message_media
                )
                
                # Send keyboard separately
                await bot.send_message(
                    chat_id=user.user_id,
                    text="Click below to view the item:",
                    reply_markup=keyboard
                )
            else:
                # No media, send text only
                await bot.send_message(
                    chat_id=user.user_id,
                    text=message_builder.message_text,
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
            
            logger.debug(f"Notification {notification.id} sent to user {user.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending notification {notification.id} to user {user.user_id}: {e}")
            return False


# Create singleton instance
notification_service = NotificationService() 