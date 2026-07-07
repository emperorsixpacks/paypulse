from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.core.dependencies import get_db, get_current_merchant
from src.paypulse.models.merchant import Merchant
from src.paypulse.schemas.merchant import ApiKeyCreate, ApiKeyCreatedResponse, ApiKeyResponse, ProjectCreate, ProjectResponse
from src.paypulse.services.merchant_service import MerchantService

router = APIRouter(prefix="/merchants", tags=["merchants"])


@router.get("/me")
async def get_merchant_profile(merchant: Merchant = Depends(get_current_merchant)):
    return {
        "id": str(merchant.id),
        "email": merchant.email,
        "business_name": merchant.business_name,
        "is_active": merchant.is_active,
        "is_verified": merchant.is_verified,
    }


@router.get("/projects")
async def list_projects(
    merchant: Merchant = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    service = MerchantService(db)
    projects = await service.list_projects(merchant.id)
    return [ProjectResponse.model_validate(p) for p in projects]


@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    body: ProjectCreate,
    merchant: Merchant = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    service = MerchantService(db)
    project = await service.create_project(merchant.id, body.name)
    return project


@router.get("/api-keys")
async def list_api_keys(
    merchant: Merchant = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    service = MerchantService(db)
    keys = await service.list_api_keys(merchant.id)
    return [
        ApiKeyResponse(
            id=k.id,
            name=k.name,
            key_prefix=k.key_prefix,
            is_active=k.is_active,
            created_at=k.created_at,
        )
        for k in keys
    ]


@router.post("/api-keys", response_model=ApiKeyCreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    body: ApiKeyCreate,
    merchant: Merchant = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    service = MerchantService(db)
    projects = await service.list_projects(merchant.id)
    if not projects:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Create a project first")

    key_record, full_key = await service.generate_api_key(projects[0].id, body.name, body.is_live)

    return ApiKeyCreatedResponse(
        id=key_record.id,
        name=key_record.name,
        key=full_key,
        key_prefix=key_record.key_prefix,
        is_active=key_record.is_active,
        created_at=key_record.created_at,
    )


@router.delete("/api-keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    key_id: UUID,
    merchant: Merchant = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    service = MerchantService(db)
    revoked = await service.revoke_api_key(key_id)
    if not revoked:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")
