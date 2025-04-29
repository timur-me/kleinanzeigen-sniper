from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
# from app.models import User
from app.db.models import User
from app.db.database import async_session
from app.db.repositories import UserRepository


class UserAccessMiddleware(BaseMiddleware):
    """Middleware to check user access and register new users in DB."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        tg_user = event.from_user
        if not tg_user:
            return await handler(event, data)

        user_id = tg_user.id
        is_admin = user_id in settings.ADMIN_USER_IDS
        text = getattr(event, "text", "")

        if text.startswith("/admin") and not is_admin:
            logger.warning(f"User {user_id} tried to access admin command: {text}")
            await event.answer("❌ You don't have permission to use this command.")
            return None

        async with async_session() as session:
            repo = UserRepository(session)
            db_user = await repo.get_by_id(user_id)

            if not db_user:
                db_user = User(
                    user_id=user_id,
                    username=tg_user.username,
                    first_name=tg_user.first_name,
                    last_name=tg_user.last_name,
                    is_admin=is_admin,
                )
                await repo.save(db_user)
                logger.info(f"New user registered: {db_user.full_name()} (ID: {user_id})")
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
                    logger.debug(f"Updated user data for {db_user.full_name()} (ID: {user_id})")

        return await handler(event, data)
