from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Item
from app.db.repositories import ItemRepository


class ItemService:
    """Service for managing items."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def exists(self, item_id: str) -> bool:
        repo = ItemRepository(self.session)
        return await repo.exists(item_id)

    async def get_or_create_by_id(self, item_id: str, data: dict) -> Item:
        repo = ItemRepository(self.session)
        if await repo.exists(item_id):
            existing = await repo.get_by_id(item_id)
            existing.raw_data = data
            existing.last_updated = datetime.utcnow()
            return await repo.save(existing)

        new_item = Item(id=item_id, raw_data=data)
        return await repo.save(new_item)


