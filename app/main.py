import asyncio
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from app.bot.routers import main_router as handlers_router
from app.bot.routers import help_router

from app.bot.routers import (
    help_router,
    start_router,
    keyboard_router,
    link_router,
    callback_router,
    fsm_router, 
)
from app.bot.middlewares import UserAccessMiddleware
from app.bot.notifications import send_item_notifications
from app.config.settings import settings
from app.utils.logging import setup_logging
from app.workers.parsing_worker import parsing_worker
from app.kleinanzeigen.kleinanzeigen_client import KleinanzeigenClient

# Set up logging
logger = setup_logging()


async def on_startup(bot: Bot):
    """Execute actions on bot startup."""
    logger.info("Bot is starting up...")

    # TODO: REWORK THIS parsing worker.
    
    # # Start parsing worker
    # logger.info("Starting parsing worker...")
    # parsing_worker.start()
    
    # Set up commands
    await bot.set_my_commands([
        BotCommand(command="start", description="Start the bot"),
        BotCommand(command="help", description="Show help information"),
        BotCommand(command="searches", description="View your saved searches"),
        BotCommand(command="add", description="Add a new search"),
        BotCommand(command="cancel", description="Cancel current operation")
    ])
    
    logger.info("Bot startup completed.")


async def on_shutdown(bot: Bot):
    """Execute actions on bot shutdown."""
    logger.info("Bot is shutting down...")
    
    # # Stop parsing worker
    # logger.info("Stopping parsing worker...")
    # parsing_worker.stop()
    
    logger.info("Bot shutdown completed.")


async def scheduled_notifications(bot: Bot):
    """Send notifications about new items periodically."""
    while True:
        try:
            await send_item_notifications(bot)
        except Exception as e:
            logger.error(f"Error sending notifications: {e}")
        
        # Wait before next notification cycle
        await asyncio.sleep(60)  # Run every minute


async def main():
    """Main function to run the bot."""
    # Import locally to avoid circular imports
    import app
    
    logger.info(f"Starting Kleinanzeigen Sniper v{app.__version__}")

    # Initialize KleinanzeigenClient singleton
    KleinanzeigenClient.initialize(settings)

    # Initialize bot and dispatcher
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    ))
    dp = Dispatcher(storage=MemoryStorage())
    
    # Register middlewares
    dp.message.middleware(UserAccessMiddleware())
    
    # Register routers
    dp.include_routers(
        start_router,
        help_router,
        keyboard_router,
        link_router,
        fsm_router,
        callback_router
    )
    
    # Set up event handlers
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Start notifications task
    # asyncio.create_task(scheduled_notifications(bot))
    
    # Start polling
    logger.info("Starting polling...")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1) 