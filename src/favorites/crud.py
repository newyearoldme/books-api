from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.favorites.models import FavoriteModel
from src.favorites.schemas import FavoriteCreate, FavoriteUpdate
from src.shared.crud_base import CRUDBase


class CRUDReview(CRUDBase[FavoriteModel, FavoriteCreate, FavoriteUpdate]):
    async def add_to_favorites(
        self, db: AsyncSession, user_id: int, book_id: int
    ) -> FavoriteModel:
        favorite = FavoriteModel(user_id=user_id, book_id=book_id)
        db.add(favorite)
        await db.commit()
        await db.refresh(favorite)
        return favorite

    async def get_user_favorites(
        self, db: AsyncSession, user_id: int, skip: int, limit: int
    ) -> list[FavoriteModel] | None:
        result = await db.execute(
            select(FavoriteModel)
            .options(selectinload(FavoriteModel.book))
            .where(FavoriteModel.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def remove_from_favorites(
        self, db: AsyncSession, user_id: int, book_id: int
    ) -> bool:
        result = await db.execute(
            delete(FavoriteModel).where(
                FavoriteModel.user_id == user_id, FavoriteModel.book_id == book_id
            )
        )
        await db.commit()
        return result.rowcount > 0

    async def is_book_in_favorites(
        self, db: AsyncSession, user_id: int, book_id: int
    ) -> bool:
        result = await db.execute(
            select(FavoriteModel).where(
                FavoriteModel.user_id == user_id, FavoriteModel.book_id == book_id
            )
        )
        return result.scalar_one_or_none() is not None


favorite = CRUDReview(FavoriteModel)
