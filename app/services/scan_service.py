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
        searches = self.search_repo.get_active_searches()
        
        logger.info(f"Scanning for new items with {len(searches)} active search settings")
        
        for search in searches:
            await self.process_search(search)
    
    async def process_search(self, search: SearchSettings):
        """Process a single search settings and create notifications for new items."""
        logger.info(f"Processing search: {search.item_name} in {search.location_name}")
        
        try:
            # Fetch items from Kleinanzeigen
            items = await self.kleinanzeigen_client.fetch_items(search)
            
            if not items:
                logger.info(f"No items found for search: {search.item_name}")
                return
            
            logger.info(f"Found {len(items)} items for search: {search.item_name}")
            
            # Process each item
            for kleinanzeigen_item in items:
                raw_data = kleinanzeigen_item.raw_data 
                
                # Save or update the item
                item = self.item_repo.get_or_create_by_kleinanzeigen_id(
                    kleinanzeigen_item.id,
                    raw_data
                )
                
                self.notification_repo.create_notification_if_not_exists(
                        item_id=item.id,
                        user_id=search.user_id,
                        search_id=search.id,
                        sent=not search.was_used
                )
                
                if search.was_used:
                    logger.debug(f"Processed item: {item.id} for user: {search.user_id}")

            if not search.was_used:
                search.mark_as_used()
                self.search_repo.save(search)
        
        except Exception as e:
            logger.error(f"Error processing search {search.id}: {e}")


# Create singleton instance
scan_service = ScanService() 