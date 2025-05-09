from sqlalchemy import select

from app.db.models import UserSettings
from app.db.repository import AsyncRepository


class UserSettingsRepository(AsyncRepository[UserSettings]):
    def __init__(self, session):
        super().__init__(session, UserSettings)

    async def get_by_user_id(self, user_id: int) -> UserSettings | None:
        result = await self.session.execute(
            select(self.model).where(self.model.user_id == user_id)
        )
        return result.scalars().first()
