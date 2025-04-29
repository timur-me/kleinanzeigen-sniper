from sqlalchemy import select
from app.db.models import SearchSettings
from app.db.repository import AsyncRepository


class SearchSettingsRepository(AsyncRepository[SearchSettings]):
    def __init__(self, session):
        super().__init__(session, SearchSettings)

    async def get_by_user_id(self, user_id: int):
        result = await self.session.execute(
            select(self.model).where(self.model.user_id == user_id)
        )
        return result.scalars().all()

    async def get_active_searches(self):
        result = await self.session.execute(
            select(self.model).where(self.model.is_active == True)
        )
        return result.scalars().all()
