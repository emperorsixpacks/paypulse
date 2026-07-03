from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.core.dependencies import get_db, get_current_merchant
from src.paypulse.core.security import create_access_token, hash_password, verify_password
from src.paypulse.models.merchant import ApiKey, Merchant, Project
from src.paypulse.repositories.merchant_repository import ApiKeyRepository, MerchantRepository, ProjectRepository
from src.paypulse.schemas.auth import (
    ApiKeyInfo,
    LoginRequest,
    MerchantResponse,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    repo = MerchantRepository(db)
    existing = await repo.get_by_email(body.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    merchant = await repo.create({
        "email": body.email,
        "business_name": body.business_name,
        "hashed_password": hash_password(body.password),
    })

    project_repo = ProjectRepository(db)
    project = await project_repo.create({
        "merchant_id": merchant.id,
        "name": f"{body.business_name} - Default",
    })

    api_key_repo = ApiKeyRepository(db)
    live_key_record, live_key = await api_key_repo.create_for_project(project.id, "Live", is_live=True)
    test_key_record, test_key = await api_key_repo.create_for_project(project.id, "Test", is_live=False)

    token = create_access_token({"sub": str(merchant.id)})

    return RegisterResponse(
        id=merchant.id,
        email=merchant.email,
        business_name=merchant.business_name,
        access_token=token,
        api_keys=[
            ApiKeyInfo(id=live_key_record.id, name="Live", key=live_key, key_prefix=live_key_record.key_prefix, is_live=True),
            ApiKeyInfo(id=test_key_record.id, name="Test", key=test_key, key_prefix=test_key_record.key_prefix, is_live=False),
        ],
        created_at=merchant.created_at,
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    repo = MerchantRepository(db)
    merchant = await repo.get_by_email(body.email)
    if merchant is None or not verify_password(body.password, merchant.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token({"sub": str(merchant.id)})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=MerchantResponse)
async def get_me(merchant: Merchant = Depends(get_current_merchant)):
    return merchant
