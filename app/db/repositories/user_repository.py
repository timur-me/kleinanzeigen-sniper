from sqlalchemy import select

from app.db.models import User
from app.db.repository import AsyncRepository


class UserRepository(AsyncRepository[User]):
    def __init__(self, session):
        super().__init__(session, User)

    async def get_active_users(self):
        result = await self.session.execute(
            select(self.model).where(self.model.is_active == True)
        )
        return result.scalars().all()
