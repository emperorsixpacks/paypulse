from sqlalchemy.exc import SQLAlchemyError
from sqlmodel.ext.asyncio.session import AsyncSession

from src.paypulse.types import Error, error

type T = object


class BaseRepository[T]:
    _model: T | None = None

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @classmethod
    def _get_model(cls) -> T:
        if cls._model is None:
            raise RuntimeError(f"{cls.__name__} has no model configured. Set _model on the subclass.")
        return cls._model

    async def rollback(self) -> Error:
        try:
            await self.session.rollback()
            return None
        except SQLAlchemyError as e:
            return error(e)

    async def save(self, instance: T):
        return await instance.save(self.session)

    async def get(
        self,
        _id: str,
        deletion: str | None = "active",
        load: list[str] | None = None,
    ) -> tuple[T | None, Exception | None]:
        model = self._get_model()
        try:
            return await model.get(self.session, _id=_id, deletion=deletion, load=load)
        except SQLAlchemyError as e:
            return None, e

    async def find_one(
        self,
        deletion: str | None = None,
        load: list[str] | None = None,
        **filters,
    ) -> tuple[T | None, Exception | None]:
        model = self._get_model()
        return await model.find_one(
            session=self.session,
            filters=filters,
            deletion=deletion,
            load=load,
        )

    async def find_all(
        self,
        deletion: str | None = None,
        **kwargs,
    ) -> list[T]:
        return await self._get_model().find_all(self.session, deletion, **kwargs)

    async def create(self, instance: T) -> tuple[T | None, Error]:
        return await instance.create(self.session)

    async def update(self, instance: T, **kwargs) -> tuple[T | None, Error]:
        return await instance.update(self.session, **kwargs)

    async def delete(self, instance: T) -> Error:
        return await instance.delete(self.session)
