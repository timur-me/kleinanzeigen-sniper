import asyncio
from datetime import datetime

from loguru import logger

from app.config.settings import settings
from app.models.models import Item, SearchSettings
from app.services.scraper import scraper
from app.services.storage import item_storage, search_settings_storage


class ParsingWorker:
    """Worker to periodically parse Kleinanzeigen.de for new items."""
    
    def __init__(self):
        self.interval = settings.REQUEST_INTERVAL
        self.running = False
        self.task = None
    
    async def process_search_settings(self, search_settings: SearchSettings):
        """Process a single search settings configuration."""
        logger.info(f"Processing search settings: {search_settings.item_name} in {search_settings.location}")
        
        # Fetch items from Kleinanzeigen
        items = await scraper.search(search_settings)
        
        # Process found items
        for item in items:
            # Check if item already exists
            existing_item = item_storage.get_by_id(item.id)
            
            if existing_item:
                # Already have this item, but update it with potentially new info
                logger.debug(f"Item {item.id} already exists, updating")
                
                # Preserve is_sent information
                item.is_sent = existing_item.is_sent
                
                # Update item
                item_storage.save(item)
            else:
                # New item found
                logger.info(f"New item found: {item.title} ({item.id})")
                
                # Save new item
                item_storage.save(item)
    
    async def run_once(self):
        """Run a single parsing cycle for all active search settings."""
        try:
            # Get all active search settings
            all_settings = search_settings_storage.get_all()
            active_settings = [s for s in all_settings if s.is_active]
            
            logger.info(f"Starting parsing cycle with {len(active_settings)} active search settings")
            
            # Process each search setting
            for settings in active_settings:
                await self.process_search_settings(settings)
            
            logger.info("Parsing cycle completed")
        
        except Exception as e:
            logger.error(f"Error in parsing cycle: {e}")
    
    async def run_forever(self):
        """Run the parsing worker in an infinite loop."""
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