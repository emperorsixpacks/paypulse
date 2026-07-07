import secrets
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.models.webhook import WebhookDelivery, WebhookEndpoint
from src.paypulse.repositories.base import BaseRepository


class WebhookRepository(BaseRepository[WebhookEndpoint]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, WebhookEndpoint)

    async def create_endpoint(self, project_id: UUID, url: str, events: list[str]) -> WebhookEndpoint:
        endpoint = WebhookEndpoint(
            project_id=project_id,
            url=url,
            secret=f"whsec_{secrets.token_urlsafe(32)}",
            events=events,
        )
        self.session.add(endpoint)
        await self.session.flush()
        await self.session.refresh(endpoint)
        return endpoint

    async def get_active_endpoints(self, project_id: UUID) -> list[WebhookEndpoint]:
        stmt = select(WebhookEndpoint).where(
            WebhookEndpoint.project_id == project_id,
            WebhookEndpoint.is_active == True,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_endpoints_for_event(self, project_id: UUID, event_type: str) -> list[WebhookEndpoint]:
        endpoints = await self.get_active_endpoints(project_id)
        return [ep for ep in endpoints if event_type in ep.events]

    async def create_delivery(self, data: dict) -> WebhookDelivery:
        delivery = WebhookDelivery(**data)
        self.session.add(delivery)
        await self.session.flush()
        await self.session.refresh(delivery)
        return delivery

    async def get_due_deliveries(self, as_of: datetime) -> list[WebhookDelivery]:
        stmt = select(WebhookDelivery).where(
            WebhookDelivery.next_retry_at <= as_of,
            WebhookDelivery.next_retry_at.isnot(None),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
