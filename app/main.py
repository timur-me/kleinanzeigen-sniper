import asyncio
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from app.bot.routers import (
    help_router,
    start_router,
    keyboard_router,
    link_router,
    callback_router,
    # fsm_router, 
    search_create_router,
    settings_router
)
from app.db.database import engine
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
    
    # Start parsing worker
    logger.info("Starting parsing worker...")
    parsing_worker.start()
    
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
    
    # Stop parsing worker
    logger.info("Stopping parsing worker...")
    parsing_worker.stop()

    # Close database connections
    logger.info("Closing database connections...")
    
    # Close the SQLAlchemy engine which manages the connection pool
    await engine.dispose()
    logger.info("Database connections closed.")
    
    logger.info("Bot shutdown completed.")


async def scheduled_notifications(bot: Bot):
    """Send notifications about new items periodically."""
    while True:
        try:
            await send_item_notifications(bot)
        except Exception as e:
            logger.error(f"Error sending notifications: {e}")
        
        # Wait before next notification cycle
        await asyncio.sleep(settings.NOTIFICATION_INTERVAL)  # Run every minute


async def main():
    """Main function to run the bot."""
    # Import locally to avoid circular imports
    import app
    
    logger.info(f"Starting Kleinanzeigen Sniper v{app.__version__}")

    # Initialize KleinanzeigenClient singleton
    KleinanzeigenClient.get_instance()

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
        # fsm_router,
        callback_router,
        search_create_router,
        settings_router
    )
    
    # Set up event handlers
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Start notifications task with a 5-second delay
    async def delayed_notifications_start(bot: Bot):
        await asyncio.sleep(5)  # Wait for 5 seconds before starting
        await scheduled_notifications(bot)
    
    asyncio.create_task(delayed_notifications_start(bot))
    
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