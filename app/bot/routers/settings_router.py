from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import F

from app.db.database import async_session

from app.services import UserService


settings_router = Router()


@settings_router.message(Command("settings"))
@settings_router.message(F.text == "⚙️ Settings")
async def cmd_settings(message: Message):
    """Handle /settings command."""
    async with async_session() as session:
        user_service = UserService(session)
        user_settings = await user_service.get_user_settings(message.from_user.id)

    message_text = \
f"""*⚙️ Your Default Search Settings*:

📍 *Location:* `{user_settings.default_location_name}` (+ {user_settings.default_location_radius_km} km)
💶 *Price range:* `{user_settings.default_lowest_price}` – `{user_settings.default_highest_price}` EUR  

📢 *Ad type:* _{user_settings.default_ad_type.name.lower() if user_settings.default_ad_type else '(all)' }_
👤 *Poster type:* _{user_settings.default_poster_type.name.lower() if user_settings.default_poster_type else '(all)' }_ 
🖼️ *Picture required:* {"✅ Yes" if user_settings.default_is_picture_required else "❌ No"}
"""
    
    await message.answer(message_text, parse_mode="Markdown")
