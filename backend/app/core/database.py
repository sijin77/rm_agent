"""
Асинхронное подключение к SQLite через aiosqlite
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.models.base import Base

# Отключаем логирование SQLAlchemy для экономии токенов
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.dialects').setLevel(logging.WARNING)

# Создаем async движок для SQLite
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # Отключаем SQL логи для экономии токенов
    poolclass=StaticPool,
    connect_args={
        "check_same_thread": False,  # Для SQLite
    },
)

# Фабрика сессий
AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession,
    expire_on_commit=False
)


async def create_tables():
    """Создание всех таблиц"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """Dependency для получения сессии БД"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
