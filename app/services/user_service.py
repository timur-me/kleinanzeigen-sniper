from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.db.repositories import UserRepository
from aiogram.types import User as TelegramUser

from loguru import logger


class UserService:
    """Service for managing users."""

    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_or_update_user(self, tg_user: TelegramUser, is_admin: bool=False):
        repo = UserRepository(self.session)
        db_user = await repo.get_by_id(tg_user.id)

        if not db_user:
            db_user = User(
                user_id=tg_user.id,
                username=tg_user.username,
                first_name=tg_user.first_name,
                last_name=tg_user.last_name,
                is_admin=is_admin,
            )
            await repo.save(db_user)
            logger.info(f"New user registered: {db_user.full_name()} (ID: {tg_user.id})")
        else:
            has_changes = False
            if db_user.username != tg_user.username:
                db_user.username = tg_user.username
                has_changes = True
            if db_user.first_name != tg_user.first_name:
                db_user.first_name = tg_user.first_name
                has_changes = True
            if db_user.last_name != tg_user.last_name:
                db_user.last_name = tg_user.last_name
                has_changes = True
            if has_changes:
                await repo.save(db_user)
                logger.debug(f"Updated user data for {db_user.full_name()} (ID: {tg_user.id})")
