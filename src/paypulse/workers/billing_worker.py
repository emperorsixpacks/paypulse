import asyncio
import logging
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.paypulse.core.settings import settings
from src.paypulse.models import *  # noqa: F401, F403
from src.paypulse.services.billing_service import BillingService
from src.paypulse.services.subscription_service import SubscriptionService

logger = logging.getLogger(__name__)

BATCH_SIZE = 50


async def run_billing_cycle():
    engine = create_async_engine(settings.get_database_url(), pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as db:
        sub_service = SubscriptionService(db)
        billing_service = BillingService(db)

        from src.paypulse.models.enums import SubscriptionStatus
        from sqlalchemy import select
        from src.paypulse.models.billing import Subscription
        from sqlalchemy.orm import selectinload

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
        success_count = 0
        fail_count = 0

        for sub in subscriptions:
            try:
                result = await billing_service.charge_subscription(sub)
                if result.success:
                    success_count += 1
                elif result.skipped:
                    logger.info("billing_worker: skipped sub %s — %s", sub.id, result.reason)
                else:
                    fail_count += 1
            except Exception:
                logger.exception("billing_worker: error charging sub %s", sub.id)
                fail_count += 1

        await db.commit()
        logger.info("billing_worker: done — %d success, %d failed", success_count, fail_count)

    await engine.dispose()
