from sqlalchemy import select, and_
from app.db.models import Notification
from app.db.repository import AsyncRepository


class NotificationRepository(AsyncRepository[Notification]):
    def __init__(self, session):
        super().__init__(session, Notification)

    async def get_pending_notifications(self):
        result = await self.session.execute(
            select(self.model).where(self.model.is_sent == False)
        )
        return result.scalars().all()

    async def get_pending_notifications_for_user(self, user_id: int):
        result = await self.session.execute(
            select(self.model).where(
                and_(
                    self.model.is_sent == False,
                    self.model.user_id == user_id
                )
            )
        )
        return result.scalars().all()

    async def create_notification_if_not_exists(self, item_id: str, user_id: int, search_id: str) -> Notification | None:
        result = await self.session.execute(
            select(self.model).where(
                and_(
                    self.model.item_id == item_id,
                    self.model.user_id == user_id,
                    self.model.search_id == search_id
                )
            )
        )
        exists = result.scalar_one_or_none()
        if exists:
            return None

        new_notif = Notification(
            item_id=item_id,
            user_id=user_id,
            search_id=search_id,
            is_sent=False,
        )
        return await self.save(new_notif)
