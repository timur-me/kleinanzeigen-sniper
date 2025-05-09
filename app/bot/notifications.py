from aiogram import Bot
from loguru import logger

from app.services.notification_service import notification_service


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