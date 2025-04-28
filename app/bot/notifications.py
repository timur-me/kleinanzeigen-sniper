from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import InputMediaPhoto
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
    keyboard.add(InlineKeyboardButton("Open in Kleinanzeigen", url=item.url))
    
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
        f"🔍 *New Item Found!*\n\n"
        f"*{item.title}*\n\n"
        f"{price_str}"
        f"{location_str}"
        f"📝 Description: {description}"
    )
    
    try:
        # If there are images, send them as a carousel
        if item.image_urls:
            # Create media group for carousel
            media_group = []
            
            # Add first image with caption
            for i, image_url in enumerate(item.image_urls[:10]):  # Limit to 10 images
                if i == 0:
                    # First image with caption
                    media_group.attach(InputMediaPhoto(
                        type="photo",
                        media=image_url,
                        caption=message_text,
                        parse_mode="Markdown"
                    ))
                else:
                    # Additional images without caption
                    media_group.attach(InputMediaPhoto(media=image_url))
            
            # Send media group
            await bot.send_media_group(chat_id=user.user_id, media=media_group)
            
            # Send the keyboard separately
            await bot.send_message(
                chat_id=user.user_id,
                text="Click below to view the item:",
                reply_markup=keyboard
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