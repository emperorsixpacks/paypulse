from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.paypulse.core.logger import get_logger
from src.paypulse.core.settings import settings

logger = get_logger(__name__)

_engine = create_async_engine(
    settings.get_database_url(),
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={"timeout": 10},
)
_async_session = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with _async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
