from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.reviews.models import ReviewModel
from src.reviews.schemas import ReviewCreate
from src.shared.crud_base import CRUDBase


class CRUDReviews(CRUDBase[ReviewModel, ReviewCreate, ReviewCreate]): # Update = Create  
    async def create(self, db: AsyncSession, obj_in: int) -> ReviewModel:
        if isinstance(obj_in, dict):
            db_obj = ReviewModel(**obj_in)
        else:
            db_obj = ReviewModel(**obj_in.model_dump())
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get_by_book(self, db: AsyncSession, book_id: int) -> list[ReviewModel]:
        result = await db.execute(select(self.model).where(self.model.book_id == book_id))
        return result.scalars().all()
    
    async def get_by_user(self, db: AsyncSession, user_id: int) -> list[ReviewModel]:
        result = await db.execute(select(self.model).where(self.model.user_id == user_id))
        return result.scalars().all()

    async def get_average_rating(self, db: AsyncSession, book_id: int) -> float | None:
        result = await db.execute(
            select(func.avg(self.model.rating))
            .where(self.model.book_id == book_id)
        )
        return result.scalar()

review = CRUDReviews(ReviewModel)
