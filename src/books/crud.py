from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.books.models import BookModel
from src.books.schemas import BookCreate, BookUpdate
from src.shared.crud_base import CRUDBase


class CRUDBook(CRUDBase[BookModel, BookCreate, BookUpdate]):
    async def get_by_title_author(
        self, db: AsyncSession, title: str, author: str
    ) -> BookModel:
        result = await db.execute(
            select(self.model).where(
                self.model.title == title, self.model.author == author
            )
        )
        return result.scalar_one_or_none()

    async def get_top_rated(
        self, db: AsyncSession, skip: int, limit: int
    ) -> list[BookModel]:
        result = await db.execute(
            select(self.model)
            .order_by(self.model.rating.desc())
            .limit(limit)
            .offset(skip)
        )
        return result.scalars().all()


book = CRUDBook(BookModel)
