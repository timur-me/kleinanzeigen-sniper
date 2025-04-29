from loguru import logger

from app.kleinanzeigen.kleinanzeigen_client import KleinanzeigenClient
from app.models.models import SearchSettings
from app.services.repositories import (
    ItemRepository, 
    NotificationRepository, 
    SearchSettingsRepository,
    item_repository,
    notification_repository,
    search_settings_repository
)


class ScanService:
    """Service for scanning Kleinanzeigen for new items."""
    
    def __init__(
        self,
        item_repo: ItemRepository = item_repository,
        notification_repo: NotificationRepository = notification_repository,
        search_repo: SearchSettingsRepository = search_settings_repository
    ):
        self.item_repo = item_repo
        self.notification_repo = notification_repo
        self.search_repo = search_repo
        self.kleinanzeigen_client = KleinanzeigenClient.get_instance()
    
    async def scan_for_new_items(self):
        """Scan for new items for all active search settings."""
        import time
        import asyncio
        start_time = time.time()
        
        searches = self.search_repo.get_active_searches()
        logger.debug(f"Getting active searches took {time.time() - start_time:.3f} seconds")
        
        logger.info(f"Scanning for new items with {len(searches)} active search settings")
        
        total_start = time.time()
        # Use asyncio.gather to process searches concurrently
        await asyncio.gather(*[self.process_search(search) for search in searches])
        logger.debug(f"Total scan_for_new_items execution took {time.time() - total_start:.3f} seconds")
    
    async def process_search(self, search: SearchSettings):
        """Process a single search settings and create notifications for new items."""
        import time
        start_time = time.time()
        
        logger.info(f"Processing search: {search.item_name} in {search.location_name}")
        
        try:
            # Fetch items from Kleinanzeigen
            fetch_start = time.time()
            items = await self.kleinanzeigen_client.fetch_items(search)
            logger.debug(f"Fetching items took {time.time() - fetch_start:.3f} seconds")
            
            if not items:
                logger.info(f"No items found for search: {search.item_name}")
                return
            
            logger.info(f"Found {len(items)} items for search: {search.item_name}")
            
            # Process each item
            process_start = time.time()
            for kleinanzeigen_item in items:
                item_start = time.time()
                raw_data = kleinanzeigen_item.raw_data 
                
                # Save or update the item
                db_start = time.time()
                item = self.item_repo.get_or_create_by_kleinanzeigen_id(
                    kleinanzeigen_item.id,
                    raw_data
                )
                logger.debug(f"Database get_or_create took {time.time() - db_start:.3f} seconds")
                
                notif_start = time.time()
                self.notification_repo.create_notification_if_not_exists(
                        item_id=item.id,
                        user_id=search.user_id,
                        search_id=search.id,
                        sent=not search.was_used
                )
                logger.debug(f"Creating notification took {time.time() - notif_start:.3f} seconds")
                
                if search.was_used:
                    logger.debug(f"Processed item: {item.id} for user: {search.user_id}")
                
                logger.debug(f"Processing single item took {time.time() - item_start:.3f} seconds")

            logger.debug(f"Processing all items took {time.time() - process_start:.3f} seconds")

            if not search.was_used:
                update_start = time.time()
                search.mark_as_used()
                self.search_repo.save(search)
                logger.debug(f"Updating search status took {time.time() - update_start:.3f} seconds")
            
            logger.debug(f"Total process_search execution took {time.time() - start_time:.3f} seconds")
        
        except Exception as e:
            logger.error(f"Error processing search {search.id}: {e}")


# Create singleton instance
scan_service = ScanService() 