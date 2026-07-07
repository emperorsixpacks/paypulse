import hashlib
import hmac
import secrets
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.repositories.webhook_repository import WebhookRepository


class WebhookService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = WebhookRepository(db)

    async def register_endpoint(self, project_id: UUID, url: str, events: list[str]):
        return await self.repo.create_endpoint(project_id, url, events)

    async def list_endpoints(self, project_id: UUID):
        return await self.repo.get_active_endpoints(project_id)

    async def delete_endpoint(self, endpoint_id: UUID, project_id: UUID):
        endpoint = await self.repo.get(endpoint_id)
        if endpoint is None or endpoint.project_id != project_id:
            return False
        endpoint.is_active = False
        await self.db.flush()
        return True

    async def queue_delivery(self, project_id: UUID, event_type: str, payload: dict):
        endpoints = await self.repo.get_endpoints_for_event(project_id, event_type)
        for endpoint in endpoints:
            await self.repo.create_delivery({
                "endpoint_id": endpoint.id,
                "event_type": event_type,
                "payload": payload,
                "status": "PENDING",
                "attempt_count": 0,
            })

    async def deliver(self, delivery_id: UUID):
        delivery = await self.repo.get(delivery_id)
        if delivery is None:
            return False

        endpoint = await self.repo.get(delivery.endpoint_id)
        if endpoint is None:
            return False

        import json
        payload_bytes = json.dumps(delivery.payload, default=str).encode()
        signature = self._sign(payload_bytes, endpoint.secret)

        # TODO: Actual HTTP POST with 10s timeout
        # response = httpx.post(endpoint.url, content=payload_bytes, headers={...}, timeout=10)

        delivery.status = "DELIVERED"
        delivery.attempt_count += 1
        await self.db.flush()
        return True

    def _sign(self, payload: bytes, secret: str) -> str:
        digest = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        return f"sha256={digest}"
