from collections.abc import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import settings
from src.core.constants import Environment

async_engine = create_async_engine(
    settings.db.async_url,
    echo=settings.server.environment == Environment.LOCAL,
)
async_session_factory = async_sessionmaker(async_engine, expire_on_commit=False)

sync_engine = create_engine(settings.db.sync_url)
sync_session_factory = sessionmaker(bind=sync_engine)


async def dispose_engine() -> None:
    await async_engine.dispose()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
