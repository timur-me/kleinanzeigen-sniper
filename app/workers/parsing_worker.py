import asyncio
from datetime import datetime

from loguru import logger

from app.config.settings import settings
from app.services.scan_service import scan_service


class ParsingWorker:
    """Worker to periodically parse Kleinanzeigen.de for new items."""
    
    def __init__(self):
        self.interval = settings.REQUEST_INTERVAL
        self.running = False
        self.task = None
    
    async def run_once(self):
        """Run a single parsing cycle."""
        try:
            logger.info("Starting parsing cycle")
            
            # Use scan service to fetch new items
            await scan_service.scan_for_new_items()
            
            logger.info("Parsing cycle completed")
        except Exception as e:
            logger.error(f"Error in parsing cycle: {e}")
    
    async def run_forever(self):
        """Run the parsing worker in an infinite loop."""
        await asyncio.sleep(3) # waiting for the bot to start
        self.running = True
        
        while self.running:
            start_time = datetime.now()
            
            await self.run_once()
            
            # Calculate elapsed time and sleep for the remainder of the interval
            elapsed = (datetime.now() - start_time).total_seconds()
            sleep_time = max(0, self.interval - elapsed)
            
            if sleep_time > 0:
                logger.debug(f"Sleeping for {sleep_time:.1f} seconds")
                await asyncio.sleep(sleep_time)
    
    def start(self):
        """Start the parsing worker."""
        if self.task is None or self.task.done():
            self.task = asyncio.create_task(self.run_forever())
            logger.info("Parsing worker started")
        else:
            logger.warning("Parsing worker already running")
    
    def stop(self):
        """Stop the parsing worker."""
        if self.task and not self.task.done():
            self.running = False
            logger.info("Parsing worker stopping...")
        else:
            logger.warning("Parsing worker not running")


# Singleton instance
parsing_worker = ParsingWorker() 