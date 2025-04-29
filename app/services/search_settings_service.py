from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import SearchSettings
from app.db.repositories import SearchSettingsRepository

from loguru import logger


class SearchSettingsService:
    """Service for managing search settings."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, search_settings: SearchSettings) -> SearchSettings:
        repo = SearchSettingsRepository(self.session)
        search_settings = await repo.save(search_settings)

        return search_settings
    
    async def get_by_user_id(self, user_id: int) -> list[SearchSettings]:
        repo = SearchSettingsRepository(self.session)
        search_settings = await repo.get_by_user_id(user_id)

        return search_settings

    async def get_by_id(self, search_id: str) -> SearchSettings:
        repo = SearchSettingsRepository(self.session)
        search_settings = await repo.get_by_id(search_id)

        return search_settings

    async def delete(self, search_id: str) -> bool:
        repo = SearchSettingsRepository(self.session)
        result = await repo.delete(search_id)

        return result

    async def toggle(self, search_id: str) -> bool:
        repo = SearchSettingsRepository(self.session)
        search_settings = await repo.get_by_id(search_id)
        search_settings.is_active = not search_settings.is_active
        await repo.update(search_settings)

        return search_settings.is_active
