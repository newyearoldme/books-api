from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ReviewBase(BaseModel):
    text: str = Field(..., max_length=1000, examples=["Отличная книга!"])
    rating: int = Field(..., ge=1, le=5, examples=[2])


class ReviewCreate(ReviewBase):
    book_id: int = Field(..., examples=[1])


class ReviewUpdate(ReviewBase):
    pass


class Review(ReviewBase):
    id: int
    user_id: int
    book_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
