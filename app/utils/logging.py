import sys
from pathlib import Path

from loguru import logger

from app.config.settings import settings


def setup_logging():
    """Configure logging for the application."""
    
    # Remove default handlers
    logger.remove()
    
    # Configure console output with INFO level
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    # Configure file logging with DEBUG level
    log_file = settings.LOG_DIR / "kleinanzeigen_sniper.log"
    logger.add(
        log_file,
        rotation="10 MB",
        retention="7 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        encoding="utf-8"
    )
    
    return logger 