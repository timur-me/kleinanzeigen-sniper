from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger

from app.models.models import Item, User
from app.services.storage import item_storage, user_storage


async def send_item_notifications(bot: Bot):
    """Send notifications about new items to users."""
    # Get all users
    users = user_storage.get_all()
    
    for user in users:
        if not user.is_active:
            continue
        
        # Get unsent items for this user
        unsent_items = item_storage.get_unsent_for_user(user.user_id)
        
        if not unsent_items:
            continue
        
        logger.info(f"Sending {len(unsent_items)} new item notifications to user {user.user_id}")
        
        # Send each item
        for item in unsent_items:
            await send_item_notification(bot, user, item)
            
            # Mark as sent
            item.mark_as_sent(user.user_id)
            item_storage.save(item)


async def send_item_notification(bot: Bot, user: User, item: Item):
    """Send notification about a single item to a user."""
    # Create keyboard for the item
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("View on Kleinanzeigen", url=item.url))
    
    # Format price nicely if available
    price_str = f"💰 Price: {item.price}\n" if item.price else ""
    
    # Format location nicely if available
    location_str = f"📍 Location: {item.location}\n" if item.location else ""
    
    # Format description (truncate if too long)
    description = item.description or "No description available"
    if len(description) > 300:
        description = description[:297] + "..."
    
    # Prepare message text
    message_text = (
        f"🆕 *New Item Found!*\n\n"
        f"*{item.title}*\n\n"
        f"{price_str}"
        f"{location_str}"
        f"📝 Description: {description}"
    )
    
    try:
        # If there are images, send the first one with the message
        if item.image_urls:
            await bot.send_photo(
                chat_id=user.user_id,
                photo=item.image_urls[0],
                caption=message_text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
            # Send additional images if any (max 3 more)
            for image_url in item.image_urls[1:4]:
                await bot.send_photo(
                    chat_id=user.user_id,
                    photo=image_url
                )
        else:
            # No images, send text only
            await bot.send_message(
                chat_id=user.user_id,
                text=message_text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        
        logger.debug(f"Notification sent to user {user.user_id} for item {item.id}")
        
    except Exception as e:
        logger.error(f"Failed to send notification to user {user.user_id}: {e}")
        # Don't mark as sent if there was an error
        return False
    
    return True 