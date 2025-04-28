from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from loguru import logger


from app.bot.keyboards import (
    get_main_menu,
)
from app.config.settings import settings
from app.models.models import User
from app.services.storage import user_storage


start_router = Router()


@start_router.message(CommandStart())
async def cmd_start(message: Message):
    """Handle /start command."""
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    
    # Check if user already exists
    existing_user = user_storage.get_by_id(user_id)
    
    if not existing_user:
        # Create new user
        is_admin = user_id in settings.ADMIN_USER_IDS
        
        user = User(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            is_admin=is_admin
        )
        
        user_storage.save(user)
        logger.info(f"New user registered: {user.full_name()} (ID: {user_id})")
    else:
        # Update existing user data
        existing_user.username = username
        existing_user.first_name = first_name
        existing_user.last_name = last_name
        user_storage.save(existing_user)
    
    # Welcome message
    await message.answer(
        f"Welcome to Kleinanzeigen Sniper, {first_name or username or 'there'}! 👋\n\n"
        f"This bot helps you monitor Kleinanzeigen.de for new listings matching your search criteria.\n\n"
        f"Use the menu below to get started or type /help for more information.",
        reply_markup=get_main_menu()
    )