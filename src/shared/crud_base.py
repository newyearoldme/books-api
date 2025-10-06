from typing import Generic, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")
CreateShcemaType = TypeVar("CreateShcemaType", bound=BaseModel)
UpdateShcemaType = TypeVar("UpdateShcemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateShcemaType, UpdateShcemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def create(self, db: AsyncSession, obj_in: CreateShcemaType) -> ModelType:
        db_obj = self.model(**obj_in.model_dump())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get(self, db: AsyncSession, id: int) -> ModelType | None:
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_all(self, db: AsyncSession, skip: int, limit: int) -> list[ModelType]:
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return result.scalars().all()

    async def update(
        self, db: AsyncSession, id: int, obj_in: UpdateShcemaType
    ) -> ModelType | None:
        update_data = obj_in.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get(db, id)

        await db.execute(
            update(self.model).where(self.model.id == id).values(**update_data)
        )

        await db.commit()
        return await self.get(db, id)

    async def delete(self, db: AsyncSession, id: int) -> ModelType | None:
        db_obj = await self.get(db, id)
        if db_obj:
            await db.delete(db_obj)
            await db.commit()
        return db_obj
