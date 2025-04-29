from aiogram import Bot
from loguru import logger

from app.db.models import Item, User
from app.services.notification_service import notification_service
from app.kleinanzeigen.models import KleinanzeigenItem
from app.builders.message_builder import SingleKleinanzeigenItemMessageBuilder


async def send_item_notifications(bot: Bot):
    """Send notifications about new items to users.
    
    This is a wrapper around notification_service.send_pending_notifications
    that can be called from main.py.
    """
    try:
        logger.info("Sending item notifications")
        await notification_service.send_pending_notifications(bot)
        logger.info("Notifications sent successfully")
    except Exception as e:
        logger.error(f"Error sending notifications: {e}")


async def send_item_notification(bot: Bot, user: User, item: Item):
    """Send notification about a single item to a user."""

    kleinanzeigen_item = KleinanzeigenItem(item.raw_data)
    message_builder = SingleKleinanzeigenItemMessageBuilder(kleinanzeigen_item)
    message_builder.build()

    try:
        if kleinanzeigen_item.pictures:
            media = message_builder.message_media
            
            # Send media group
            await bot.send_media_group(chat_id=user.user_id, media=media)
        else:
            # No images, send text only
            await bot.send_message(
                chat_id=user.user_id,
                text=message_builder.message_text,
                parse_mode="Markdown"
            )
        
        logger.debug(f"Notification sent to user {user.user_id} for item {item.id}")
        
    except Exception as e:
        logger.error(f"Failed to send notification to user {user.user_id}: {e}")
        # Don't mark as sent if there was an error
        return False
    
    return True 