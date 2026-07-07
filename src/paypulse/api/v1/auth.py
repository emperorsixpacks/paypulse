from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.core.dependencies import get_db, get_current_merchant
from src.paypulse.models.merchant import Merchant
from src.paypulse.schemas.auth import (
    ApiKeyInfo,
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)
from src.paypulse.services.merchant_service import MerchantService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    service = MerchantService(db)
    try:
        result = await service.register(body.email, body.business_name, body.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    return RegisterResponse(
        id=result["merchant"].id,
        email=result["merchant"].email,
        business_name=result["merchant"].business_name,
        access_token=result["access_token"],
        api_keys=[
            ApiKeyInfo(
                id=k["record"].id,
                name=k["record"].name,
                key=k["key"],
                key_prefix=k["record"].key_prefix,
                is_live=k["is_live"],
            )
            for k in result["api_keys"]
        ],
        created_at=result["merchant"].created_at,
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    service = MerchantService(db)
    try:
        token = await service.login(body.email, body.password)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return TokenResponse(access_token=token)


@router.get("/me")
async def get_me(merchant: Merchant = Depends(get_current_merchant)):
    return {
        "id": str(merchant.id),
        "email": merchant.email,
        "business_name": merchant.business_name,
        "is_active": merchant.is_active,
        "is_verified": merchant.is_verified,
    }
