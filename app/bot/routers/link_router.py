from aiogram import F, Router
from aiogram.types import Message
from loguru import logger
import re

from app.bot.keyboards import (
    get_item_link_keyboard
)
from app.kleinanzeigen.kleinanzeigen_client import KleinanzeigenClient
from app.builders.message_builder import SingleItemMessageBuilder

link_router = Router()

@link_router.message(F.text.contains("kleinanzeigen.de"))
async def handle_kleinanzeigen_link(message: Message):
    """Handle messages containing Kleinanzeigen links."""
    # Extract item ID from URL
    url = message.text
    item_id_match = re.search(r'kleinanzeigen\.de/s-anzeige/[^/]+/(\d+)', url)
    
    if not item_id_match:
        await message.answer("Sorry, I couldn't extract the item ID from the URL.")
        return
    
    item_id = item_id_match.group(1)
    logger.info(f"Extracted item ID: {item_id} from URL: {url}")
    
    kleinanzeigen_client = KleinanzeigenClient.get_instance()

    item_data = await kleinanzeigen_client.fetch_one_item(item_id)

    if item_data is None:
        await message.answer("Sorry, I couldn't fetch the item details.")
        return

    message_builder = SingleItemMessageBuilder(item_data)
    
    # Create keyboard
    # TODO: Add setting field if person wants to have this button
    # keyboard = get_item_link_keyboard(item_data.ad_link)
    
    if message_builder.message_media:
        # Send media group
        await message.answer_media_group(media=message_builder.message_media)
        
        # # Send the keyboard separately
        # await message.answer(
        #     text="Click below to view the item:",
        #     reply_markup=keyboard
        # )
    else:
        # No images, send text only
        await message.answer(
            text=message_builder.message_text,
            # reply_markup=keyboard,
            parse_mode="Markdown"
        )
    
    logger.info(f"Successfully sent item details for ID: {item_id}")

