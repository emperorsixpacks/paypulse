from collections.abc import AsyncGenerator

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.core.db import get_session
from src.paypulse.core.security import decode_access_token
from src.paypulse.models.merchant import Merchant, Project
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
    merchant = await repo.get(merchant_id)
    if merchant is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Merchant not found")

    return merchant


async def get_project_from_api_key(
    x_api_key: str = Header(...),
    db: AsyncSession = Depends(get_db),
) -> Project:
    repo = ApiKeyRepository(db)
    project = await repo.verify_key(x_api_key)
    if project is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    return project


async def get_project_with_merchant(
    x_api_key: str = Header(...),
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Project:
    api_key_repo = ApiKeyRepository(db)
    project = await api_key_repo.verify_key(x_api_key)
    if project is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    merchant_id = payload.get("sub")
    if merchant_id is None or str(project.merchant_id) != merchant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized for this project")

    return project
