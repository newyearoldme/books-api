from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from src.books.models import BookModel
from src.books.schemas import BookCreate, BookUpdate
from src.shared.crud_base import CRUDBase


class CRUDBook(CRUDBase[BookModel, BookCreate, BookUpdate]):
    async def get_by_title_author(self, db: AsyncSession, title: str, author: str) -> BookModel:
        result = await db.execute(select(self.model).where(self.model.title == title, self.model.author == author))
        return result.scalar_one_or_none()
        
    async def get_top_rated(self, db: AsyncSession, limit: int) -> list[BookModel]:
        result = await db.execute(
            select(self.model)
            .order_by(self.model.rating.desc())
            .limit(limit)
        )
        return result.scalars().all()

    # async def get_with_reviews(self, db: AsyncSession, book_id: int) -> BookModel | None:
    #     result = await db.execute(
    #         select(self.model)
    #         .where(self.model.id == book_id)
    #         .options(selectinload(self.model.reviews))
    #     )
    #     return result.scalar_one_or_none()

book = CRUDBook(BookModel)
