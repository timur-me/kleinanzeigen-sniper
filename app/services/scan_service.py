import asyncio
from loguru import logger
from asyncio import Semaphore

from app.db.database import async_session
from app.db.repositories import SearchSettingsRepository, NotificationRepository
from app.services.item_service import ItemService
from app.kleinanzeigen.kleinanzeigen_client import KleinanzeigenClient
from app.db.models import SearchSettings
from app.config.settings import settings

class ScanService:
    """Service for scanning Kleinanzeigen for new items."""

    def __init__(self, max_concurrent_tasks: int = 5):
        self.kleinanzeigen_client = KleinanzeigenClient.get_instance()
        self.semaphore = Semaphore(max_concurrent_tasks)

    async def scan_for_new_items(self):
        """Main entrypoint to scan all active search settings."""
        async with async_session() as session:
            search_repo = SearchSettingsRepository(session)
            searches = await search_repo.get_active_searches()

        logger.info(f"🔍 Starting scan for {len(searches)} active search settings")

        tasks = [self._limited_process_search(search) for search in searches]
        await asyncio.gather(*tasks)

    async def _limited_process_search(self, search: SearchSettings):
        """Semaphore-limited wrapper to control concurrency."""
        async with self.semaphore:
            await self._process_search(search)

    async def _process_search(self, search: SearchSettings):
        logger.info(f"➡️ Processing search: {search.alias} for {search.user_id}")

        try:
            items = await self.kleinanzeigen_client.fetch_items(search)
            if not items:
                logger.info(f"❌ No items found for search: {search.item_name}")
                return

            logger.info(f"✅ Found {len(items)} items for search: {search.item_name}")

            async with async_session() as session:
                item_repo = ItemService(session)
                notif_repo = NotificationRepository(session)
                search_repo = SearchSettingsRepository(session)

                for klein_item in items:
                    if await notif_repo.exists(klein_item.id, search.user_id, search.id):
                        logger.debug(f"🟡 Skipped item {klein_item.title} {klein_item.id} (already scanned)")
                        continue

                    logger.info(f"🔔 Found new item {klein_item.title} {klein_item.id} for user {search.user_id}")

                    item = await item_repo.get_or_create_by_id(
                        klein_item.id,
                        klein_item.raw_data
                    )

                    await notif_repo.create_notification(
                        item_id=item.id,
                        user_id=search.user_id,
                        search_id=search.id,
                        is_sent=not search.was_used
                    )


                if not search.was_used:
                    search.mark_as_used()
                    await search_repo.save(search)
                    logger.debug(f"🔁 Marked search {search.id} - {search.item_name} in {search.location_name} as used")

        except Exception as e:
            logger.exception(f"💥 Error processing search {search.id}: {e}")



scan_service = ScanService(settings.KLEINANZEIGEN_CONCURRENT_REQUESTS_FOR_SCAN)
