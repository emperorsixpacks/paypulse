import uuid
from datetime import UTC, datetime
from typing import Any, ClassVar, Self

from pydantic import ConfigDict
from sqlalchemy import DateTime
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import Select
from sqlmodel import Field, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.paypulse.types import Error, error

__default_protected_fields__ = ["id", "created_at", "updated_at", "deleted_at"]


async def exec_stmt[T](
    session: AsyncSession,
    stmt: Select,
    *,
    one: bool = False,
) -> T | None | list[T]:
    result = await session.execute(stmt)
    scalars = result.scalars()
    if one:
        return scalars.first()
    return scalars.all()


def utc_now() -> datetime:
    return datetime.now(UTC)


class DatabaseMixin:
    async def create(self, session: AsyncSession) -> tuple[Self | None, Error]:
        err = await self.save(session)
        if err:
            return None, err
        return self, None

    async def save(self, session: AsyncSession) -> Error:
        try:
            async with session.begin_nested():
                session.add(self)
                await session.flush()
            await session.refresh(self)
            return None
        except IntegrityError as e:
            return error(e)
        except SQLAlchemyError as e:
            return error(e)

    async def update(self: "Base", session: AsyncSession, **kwargs) -> tuple[Self | None, Error]:
        protected_fields = self._get_protected_fields()
        if self._is_protected():
            return None, error("protected model can't update")
        for key, value in kwargs.items():
            if key.lower() in __default_protected_fields__:
                return None, error(f"updating protected field: {key}")
            if isinstance(protected_fields, list) and (key in protected_fields):
                return None, error(f"updating protected field: {key}")
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now(UTC)
        err = await self.save(session)
        if err:
            return None, err
        return self, None

    async def delete(self: "Base", session: AsyncSession) -> Error:
        if self.deleted_at is not None:
            return error("item does not exist")
        self.deleted_at = utc_now()
        err = await self.save(session)
        return err

    @classmethod
    async def find_all(
        cls,
        session: AsyncSession,
        deletion: str | None = None,
        **kwargs,
    ) -> list["Self"]:
        stmt = select(cls).filter_by(**kwargs)
        if deletion == "active":
            stmt = stmt.where(cls.deleted_at.is_(None))
        elif deletion == "deleted":
            stmt = stmt.where(cls.deleted_at.is_not(None))
        return await exec_stmt(session, stmt)

    @classmethod
    async def find_one(
        cls,
        session: AsyncSession,
        filters: dict = {},
        deletion: str | None = None,
        load: list[str] | None = None,
    ) -> tuple[Self | None, Exception | None]:
        stmt = select(cls).filter_by(**filters)
        if deletion == "active":
            if hasattr(cls, "deleted_at"):
                stmt = stmt.where(cls.deleted_at.is_(None))
        elif deletion == "deleted":
            if hasattr(cls, "deleted_at"):
                stmt = stmt.where(cls.deleted_at.is_not(None))
        if load:
            for rel_name in load:
                if hasattr(cls, rel_name):
                    stmt = stmt.options(selectinload(getattr(cls, rel_name)))
        result = await session.execute(stmt)
        obj = result.scalar_one_or_none()
        if obj is None:
            return None, error("not found")
        return obj, None

    @classmethod
    async def get(
        cls,
        session: AsyncSession,
        _id: str | uuid.UUID,
        deletion: str | None = "active",
        load: list[str] | None = None,
    ) -> tuple[Self | None, Exception | None]:
        return await cls.find_one(
            session=session,
            filters={"id": _id},
            deletion=deletion,
            load=load,
        )


class Base(SQLModel, DatabaseMixin):
    __protected_fields__: ClassVar[str | list[str]] = None
    model_config = ConfigDict(use_enum_values=True, validate_assignment=True, populate_by_name=True)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)

    created_at: datetime = Field(
        default_factory=utc_now,
        sa_type=DateTime(timezone=True),
        nullable=False,
    )

    updated_at: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),
    )

    deleted_at: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),
    )

    def _get_protected_fields(self) -> str | list[str]:
        return self.__protected_fields__

    def _is_protected(self) -> bool:
        protected_fields = self._get_protected_fields()
        return isinstance(protected_fields, str) and (protected_fields.lower() == "all")
