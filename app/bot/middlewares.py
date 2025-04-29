from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.db.database import async_session
from app.services import UserService


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
            user_service = UserService(session)
            await user_service.create_or_update_user(tg_user, is_admin=is_admin)

        return await handler(event, data)
