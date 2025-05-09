from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User, UserSettings
from app.db.repositories import UserRepository, UserSettingsRepository
from aiogram.types import User as TelegramUser

from loguru import logger


class UserService:
    """Service for managing users."""

    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_or_update_user(self, tg_user: TelegramUser, is_admin: bool=False):
        user_repo = UserRepository(self.session)
        user_settings_repo = UserSettingsRepository(self.session)
        db_user = await user_repo.get_by_id(tg_user.id)

        if not db_user:
            db_user = User(
                user_id=tg_user.id,
                username=tg_user.username,
                first_name=tg_user.first_name,
                last_name=tg_user.last_name,
                is_admin=is_admin,
            )
            user_settings = UserSettings(
                user_id=tg_user.id,
            )
            await user_repo.save(db_user)
            await user_settings_repo.save(user_settings)
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
                await user_repo.save(db_user)
                logger.debug(f"Updated user data for {db_user.full_name()} (ID: {tg_user.id})")

    async def get_user_settings(self, user_id: int) -> UserSettings | None:
        repo = UserSettingsRepository(self.session)
        return await repo.get_by_user_id(user_id)

    async def update_user_settings(self, settings: UserSettings):
        repo = UserSettingsRepository(self.session)
        await repo.update(settings)


