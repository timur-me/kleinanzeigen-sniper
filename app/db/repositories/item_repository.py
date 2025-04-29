from sqlalchemy import select
from app.db.models import Item
from app.db.repository import AsyncRepository
from datetime import datetime


class ItemRepository(AsyncRepository[Item]):
    def __init__(self, session):
        super().__init__(session, Item)

    async def get_or_create_by_kleinanzeigen_id(self, item_id: str, data: dict) -> Item:
        existing = await self.get_by_id(item_id)
        if existing:
            existing.raw_data = data
            existing.last_updated = datetime.utcnow()
            return await self.save(existing)

        new_item = Item(id=item_id, raw_data=data)
        return await self.save(new_item)
