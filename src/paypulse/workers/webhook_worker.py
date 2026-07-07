import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.paypulse.core.settings import settings
from src.paypulse.models import *  # noqa: F401, F403
from src.paypulse.services.webhook_service import WebhookService

logger = logging.getLogger(__name__)


async def deliver_webhook(ctx: dict, delivery_id: str):
    engine = create_async_engine(settings.get_database_url(), pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as db:
        service = WebhookService(db)
        try:
            success = await service.deliver(UUID(delivery_id))
            if success:
                logger.info("webhook_worker: delivered %s", delivery_id)
            else:
                logger.warning("webhook_worker: failed to deliver %s", delivery_id)
            await db.commit()
        except Exception:
            logger.exception("webhook_worker: error delivering %s", delivery_id)
            await db.rollback()

    await engine.dispose()
