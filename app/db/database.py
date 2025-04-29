from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config.settings import settings

# Создаём движок базы данных
engine = create_async_engine(
    settings.database_url,
    echo=False,
)

# Создаём сессию
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Базовый класс для всех моделей
Base = declarative_base()
