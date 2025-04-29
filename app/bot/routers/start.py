from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from loguru import logger


from app.bot.keyboards import (
    get_main_menu,
)
from app.config.settings import settings
from app.db.models import User 
from app.db.repositories import UserRepository
from app.db.database import async_session

start_router = Router()


@start_router.message(CommandStart())
async def cmd_start(message: Message):
    """Handle /start command."""
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    # Welcome message
    await message.answer(
        f"Welcome to Kleinanzeigen Sniper, {first_name or username or 'there'}! 👋\n\n"
        f"This bot helps you monitor Kleinanzeigen.de for new listings matching your search criteria.\n\n"
        f"Use the menu below to get started or type /help for more information.",
        reply_markup=get_main_menu()
    )