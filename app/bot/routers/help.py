from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

help_router = Router()

@help_router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command."""
    help_text = (
        "📚 *Kleinanzeigen Sniper Help* 📚\n\n"
        "*Commands:*\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/searches - View your saved searches\n"
        "/add - Add a new search\n"
        "/cancel - Cancel current operation\n\n"
        
        "*How to use:*\n"
        "1. Add a search with an item name, location, and radius\n"
        "2. The bot will periodically check for new listings\n"
        "3. When new items are found, you'll receive notifications\n"
        "4. Manage your searches at any time\n\n"
        
        "*Tips:*\n"
        "• Be specific with item names for better results\n"
        "• Set a reasonable radius based on how far you're willing to travel\n"
        "• You can have multiple active searches at once"
    )
    
    await message.answer(help_text, parse_mode="Markdown")
