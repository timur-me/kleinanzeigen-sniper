from sqlalchemy import select
from app.db.models import Item
from app.db.repository import AsyncRepository
from datetime import datetime


class ItemRepository(AsyncRepository[Item]):
    def __init__(self, session):
        super().__init__(session, Item)

