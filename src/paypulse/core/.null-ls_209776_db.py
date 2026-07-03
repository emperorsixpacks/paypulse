from collections.abc import AsyncGenerator

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.infrastructure.settings import ENVIRONMENT
from src.types import InternaleServerError

from paypulse.core.logger import get_logger

logger = get_logger(__name__)

_config = load_config()
_db_url = _config.database.get_uri()

_is_production = _config.app.environment == ENVIRONMENT.PRODUCTION
_engine = create_async_engine(_db_url, echo=not _is_production)
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
