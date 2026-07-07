from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.core.dependencies import get_db, get_project_with_merchant
from src.paypulse.models.merchant import Project
from src.paypulse.schemas.webhook import WebhookCreate, WebhookResponse
from src.paypulse.services.webhook_service import WebhookService

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.get("", response_model=list[WebhookResponse])
async def list_webhooks(
    project: Project = Depends(get_project_with_merchant),
    db: AsyncSession = Depends(get_db),
):
    service = WebhookService(db)
    endpoints = await service.list_endpoints(project.id)
    return endpoints


@router.post("", response_model=WebhookResponse, status_code=status.HTTP_201_CREATED)
async def create_webhook(
    body: WebhookCreate,
    project: Project = Depends(get_project_with_merchant),
    db: AsyncSession = Depends(get_db),
):
    service = WebhookService(db)
    endpoint = await service.register_endpoint(project.id, body.url, body.events)
    return endpoint


@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(
    webhook_id: str,
    project: Project = Depends(get_project_with_merchant),
    db: AsyncSession = Depends(get_db),
):
    from uuid import UUID
    service = WebhookService(db)
    deleted = await service.delete_endpoint(UUID(webhook_id), project.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found")
