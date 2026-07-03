from collections.abc import AsyncGenerator

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.core.db import get_session
from src.paypulse.core.security import decode_access_token
from src.paypulse.models.merchant import Merchant
from src.paypulse.repositories.merchant_repository import ApiKeyRepository, MerchantRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with get_session() as session:
        yield session


async def get_current_merchant(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Merchant:
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    merchant_id = payload.get("sub")
    if merchant_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    repo = MerchantRepository(db)
    merchant, err = await repo.get(merchant_id)
    if err or merchant is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Merchant not found")

    return merchant


async def get_merchant_from_api_key(
    x_api_key: str = Header(...),
    db: AsyncSession = Depends(get_db),
) -> Merchant:
    repo = ApiKeyRepository(db)
    merchant = await repo.verify_key(x_api_key)
    if merchant is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    return merchant
