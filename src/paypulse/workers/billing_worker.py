import logging
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload

from src.paypulse.core.settings import settings
from src.paypulse.models import *  # noqa: F401, F403
from src.paypulse.models.billing import Subscription
from src.paypulse.models.enums import SubscriptionStatus
from src.paypulse.services.billing_service import BillingService

logger = logging.getLogger(__name__)

BATCH_SIZE = 50


async def run_billing_cycle():
    engine = create_async_engine(settings.get_database_url(), pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as db:
        billing_service = BillingService(db)

        stmt = (
            select(Subscription)
            .options(selectinload(Subscription.plan), selectinload(Subscription.customer))
            .where(
                Subscription.status == SubscriptionStatus.ACTIVE,
                Subscription.current_period_end <= datetime.now(UTC),
            )
            .limit(BATCH_SIZE)
        )
        result = await db.execute(stmt)
        subscriptions = list(result.scalars().all())

        if not subscriptions:
            logger.info("billing_worker: no due subscriptions")
            await engine.dispose()
            return

        logger.info("billing_worker: processing %d subscriptions", len(subscriptions))
        success = 0
        failed = 0

        for sub in subscriptions:
            try:
                r = await billing_service.charge_subscription(sub)
                if r.success:
                    success += 1
                elif not r.skipped:
                    failed += 1
            except Exception:
                logger.exception("billing_worker: error charging sub %s", sub.id)
                failed += 1

        await db.commit()
        logger.info("billing_worker: done — %d success, %d failed", success, failed)

    await engine.dispose()
