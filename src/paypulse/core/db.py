from collections.abc import AsyncGenerator

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.paypulse.core.logger import get_logger
from src.paypulse.core.settings import DatabaseConfig
from src.paypulse.types import InternaleServerError

logger = get_logger(__name__)

_config = DatabaseConfig()

_db_url = _config.get_uri()

_engine = create_async_engine(_db_url, echo=True)
_async_session = async_sessionmaker(
    _engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession]:
    logger.debug("Creating database session")

    async with _async_session() as session:
        try:
            logger.debug("Database session opened: %s", id(session))
            await session.begin()
            yield session
            if session.in_transaction():
                await session.commit()
        except ConnectionRefusedError as e:
            logger.error(
                "Database connection refused (session=%s)",
                id(session),
                exc_info=True,
            )
            if session.in_transaction():
                await session.rollback()
            raise InternaleServerError from e
        except SQLAlchemyError as e:
            logger.error(
                "SQLAlchemy error during session usage (session=%s)",
                id(session),
                exc_info=True,
            )
            if session.in_transaction():
                await session.rollback()
            raise InternaleServerError from e
        except GeneratorExit:
            if session.in_transaction():
                await session.commit()
            raise
        except BaseException as e:
            logger.debug(
                "Non-SQLAlchemy exception in session generator (type=%s, session=%s)",
                type(e).__name__,
                id(session),
            )
            if session.in_transaction():
                await session.rollback()
            raise
        finally:
            logger.debug(
                "Database session cleanup (session=%s, in_transaction=%s)",
                id(session),
                session.in_transaction(),
            )
