from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.paypulse.core.security import create_access_token, generate_api_key, hash_password, verify_password
from src.paypulse.models.merchant import Merchant
from src.paypulse.repositories.merchant_repository import ApiKeyRepository, MerchantRepository, ProjectRepository


class MerchantService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.merchant_repo = MerchantRepository(db)
        self.project_repo = ProjectRepository(db)
        self.api_key_repo = ApiKeyRepository(db)

    async def register(self, email: str, business_name: str, password: str) -> dict:
        existing = await self.merchant_repo.get_by_email(email)
        if existing:
            raise ValueError("Email already registered")

        merchant = await self.merchant_repo.create({
            "email": email,
            "business_name": business_name,
            "hashed_password": hash_password(password),
        })

        project = await self.project_repo.create({
            "merchant_id": merchant.id,
            "name": f"{business_name} - Default",
        })

        live_record, live_key = await self.api_key_repo.create_for_project(project.id, "Live", is_live=True)
        test_record, test_key = await self.api_key_repo.create_for_project(project.id, "Test", is_live=False)

        token = create_access_token({"sub": str(merchant.id)})

        return {
            "merchant": merchant,
            "access_token": token,
            "api_keys": [
                {"record": live_record, "key": live_key, "is_live": True},
                {"record": test_record, "key": test_key, "is_live": False},
            ],
        }

    async def login(self, email: str, password: str) -> str:
        merchant = await self.merchant_repo.get_by_email(email)
        if merchant is None or not verify_password(password, merchant.hashed_password):
            raise ValueError("Invalid credentials")
        return create_access_token({"sub": str(merchant.id)})

    async def get_by_id(self, merchant_id: UUID) -> Merchant | None:
        return await self.merchant_repo.get(merchant_id)

    async def list_projects(self, merchant_id: UUID):
        return await self.project_repo.get_by_merchant(merchant_id)

    async def create_project(self, merchant_id: UUID, name: str):
        return await self.project_repo.create({"merchant_id": merchant_id, "name": name})

    async def list_api_keys(self, merchant_id: UUID):
        projects = await self.project_repo.get_by_merchant(merchant_id)
        keys = []
        for project in projects:
            project_with_keys = await self.project_repo.get_with_api_key(project.id)
            if project_with_keys and project_with_keys.api_key:
                keys.append(project_with_keys.api_key)
        return keys

    async def generate_api_key(self, project_id: UUID, name: str, is_live: bool) -> tuple:
        return await self.api_key_repo.create_for_project(project_id, name, is_live)

    async def revoke_api_key(self, key_id: UUID) -> bool:
        return await self.api_key_repo.revoke(key_id)
