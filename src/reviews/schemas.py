# from typing import TYPE_CHECKING, Union
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


# if TYPE_CHECKING:
#     from src.books.schemas import Book
#     from src.users.schemas import User

class ReviewBase(BaseModel):
    text: str = Field(..., max_length=1000, examples=["Отличная книга!"])
    rating: int = Field(..., ge=1, le=5, examples=[2])

class ReviewCreate(ReviewBase):
    book_id: int = Field(..., examples=[1])

class Review(ReviewBase):
    id: int
    user_id: int
    book_id: int
    created_at: datetime

    # user: Union["User", None] = None
    # book: Union["Book", None] = None

    model_config = ConfigDict(from_attributes=True)
