from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.core.dependencies import get_db, get_project_from_api_key
from src.paypulse.models.merchant import Project
from src.paypulse.repositories.webhook_repository import WebhookRepository
from src.paypulse.schemas.webhook import WebhookCreate, WebhookResponse

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.get("", response_model=list[WebhookResponse])
async def list_webhooks(
    project: Project = Depends(get_project_from_api_key),
    db: AsyncSession = Depends(get_db),
):
    repo = WebhookRepository(db)
    endpoints = await repo.get_active_endpoints(project.id)
    return endpoints


@router.post("", response_model=WebhookResponse, status_code=status.HTTP_201_CREATED)
async def create_webhook(
    body: WebhookCreate,
    project: Project = Depends(get_project_from_api_key),
    db: AsyncSession = Depends(get_db),
):
    repo = WebhookRepository(db)
    endpoint = await repo.create_endpoint(project.id, body.url, body.events)
    return endpoint


@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(
    webhook_id: str,
    project: Project = Depends(get_project_from_api_key),
    db: AsyncSession = Depends(get_db),
):
    from uuid import UUID

    repo = WebhookRepository(db)
    endpoint = await repo.get(UUID(webhook_id))
    if endpoint is None or endpoint.project_id != project.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found")
    endpoint.is_active = False
    await db.flush()
