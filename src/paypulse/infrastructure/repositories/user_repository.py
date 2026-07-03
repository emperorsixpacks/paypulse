from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlmodel import select

from src.paypulse.infrastructure.repositories.base import BaseRepository
from src.paypulse.models.user import User
from src.paypulse.types import Error, error


class UserRepository(BaseRepository[User]):
    _model = User

    async def get_by_id(self, user_id: UUID) -> tuple[User | None, Error]:
        return await self.get(user_id)

    async def get_by_email(self, email: str) -> tuple[User | None, Error]:
        stmt = (
            select(User)
            .options(selectinload(User.memberships))
            .where(User.email == email)
        )
        result = await self.session.execute(stmt)
        user = result.scalars().first()
        return user, None

    async def create_user(self, user: User) -> tuple[User | None, Error]:
        existing, err = await self.get_by_email(user.email)
        if err and str(err) != "not found":
            return None, err
        if existing is not None:
            return None, error("User with this email already exists")
        return await self.create(user)

    async def list_users(self, limit: int = 50, offset: int = 0) -> tuple[list[User], Error]:
        try:
            stmt = select(User).offset(offset).limit(limit)
            result = await self.session.execute(stmt)
            return result.scalars().all(), None
        except Exception as e:
            return [], error(e)

    async def update_user(self, user_id: UUID, **kwargs) -> tuple[User | None, Error]:
        user, err = await self.get(user_id)
        if err:
            return None, err
        return await self.update(user, **kwargs)

    async def delete_user(self, user_id: UUID) -> Error:
        user, err = await self.get(user_id)
        if err:
            return err
        return await self.delete(user)
