from typing import Any, Generic, List, Optional, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

T = TypeVar("T")

class AsyncRepository(Generic[T]):
    """Базовый асинхронный репозиторий"""

    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model

    async def get_all(self) -> List[T]:
        result = await self.session.execute(select(self.model))
        return result.scalars().all()

    async def get_by_id(self, id_value: Any) -> Optional[T]:
        return await self.session.get(self.model, id_value)
    
    async def exists(self, id_value: Any) -> bool:
        return await self.session.get(self.model, id_value) is not None

    async def save(self, instance: T) -> T:
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance
    
    async def update(self, instance: T) -> T:
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def delete(self, id_value: Any) -> bool:
        obj = await self.get_by_id(id_value)
        if not obj:
            return False
        await self.session.delete(obj)
        await self.session.commit()
        return True