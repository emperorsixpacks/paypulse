import logging
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload

from src.paypulse.core.settings import settings
from src.paypulse.models import *  # noqa: F401, F403
from src.paypulse.models.billing import Subscription
from src.paypulse.services.billing_service import BillingService
from src.paypulse.services.dunning_service import DunningService

logger = logging.getLogger(__name__)

BATCH_SIZE = 50


async def run_dunning_cycle():
    engine = create_async_engine(settings.get_database_url(), pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as db:
        dunning_service = DunningService(db)
        billing_service = BillingService(db)

        due = await dunning_service.get_due_retries(datetime.now(UTC))

        if not due:
            logger.info("dunning_worker: no due retries")
            await engine.dispose()
            return

        logger.info("dunning_worker: processing %d retries", len(due))
        success = 0
        failed = 0

        for attempt in due[:BATCH_SIZE]:
            try:
                sub = await db.get(
                    Subscription,
                    attempt.invoice.subscription_id,
                    options=[selectinload(Subscription.plan), selectinload(Subscription.customer)],
                )
                if sub is None:
                    continue
                r = await billing_service.charge_subscription(sub)
                if r.success:
                    success += 1
                else:
                    failed += 1
            except Exception:
                logger.exception("dunning_worker: error retrying %s", attempt.id)
                failed += 1

        await db.commit()
        logger.info("dunning_worker: done — %d success, %d failed", success, failed)

    await engine.dispose()
