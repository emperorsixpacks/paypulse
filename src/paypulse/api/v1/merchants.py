from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.core.dependencies import get_db, get_current_merchant
from src.paypulse.models.merchant import Merchant
from src.paypulse.repositories.merchant_repository import ApiKeyRepository, ProjectRepository
from src.paypulse.schemas.merchant import ApiKeyCreate, ApiKeyCreatedResponse, ApiKeyResponse, ProjectCreate, ProjectResponse

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
    repo = ProjectRepository(db)
    projects = await repo.get_by_merchant(merchant.id)
    return [ProjectResponse.model_validate(p) for p in projects]


@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    body: ProjectCreate,
    merchant: Merchant = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    repo = ProjectRepository(db)
    project = await repo.create({"merchant_id": merchant.id, "name": body.name})
    return project


@router.get("/api-keys")
async def list_api_keys(
    merchant: Merchant = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    project_repo = ProjectRepository(db)
    projects = await project_repo.get_by_merchant(merchant.id)

    api_key_repo = ApiKeyRepository(db)
    keys = []
    for project in projects:
        project_with_keys = await project_repo.get_with_api_key(project.id)
        if project_with_keys and project_with_keys.api_key:
            k = project_with_keys.api_key
            keys.append(ApiKeyResponse(
                id=k.id,
                name=k.name,
                key_prefix=k.key_prefix,
                is_active=k.is_active,
                created_at=k.created_at,
            ))
    return keys


@router.post("/api-keys", response_model=ApiKeyCreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    body: ApiKeyCreate,
    merchant: Merchant = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    project_repo = ProjectRepository(db)
    projects = await project_repo.get_by_merchant(merchant.id)
    if not projects:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Create a project first")

    project = projects[0]
    api_key_repo = ApiKeyRepository(db)
    key_record, full_key = await api_key_repo.create_for_project(project.id, body.name, body.is_live)

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
    repo = ApiKeyRepository(db)
    revoked = await repo.revoke(key_id)
    if not revoked:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")
