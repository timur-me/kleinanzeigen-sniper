import asyncio
import os
import sys
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# ====== Настройки проекта ======
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config.settings import settings
from app.db.database import Base

from app.db.models import User, Item, SearchSettings, Notification

# ====== Настройки alembic ======
config = context.config

# Загружаем логирование, если нужно
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Назначаем модели для Alembic
target_metadata = Base.metadata

# Устанавливаем реальный URL базы данных
config.set_main_option("sqlalchemy.url", settings.database_url)

def run_migrations_offline():
    """Миграции в offline режиме (без подключения к БД)."""
    url = settings.database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # видеть изменения типа колонок
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    """Настройка миграций."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,  # видеть изменения типа колонок
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    """Миграции в online режиме."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

# Запуск миграций
if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
