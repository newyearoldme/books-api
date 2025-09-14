# from typing import TYPE_CHECKING
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


# if TYPE_CHECKING:
#     from src.review.models import Review

class BookBase(BaseModel):
    title: str = Field(..., max_length=100, examples=["Война и мир"])
    author: str = Field(..., max_length=100, examples=["Лев Толстой"])
    pages: int = Field(..., gt=0, examples=[100, 250])
    rating: float | None = Field(None, ge=0.0, le=5.0, examples=[3.5])

class BookCreate(BookBase):
    pass
    
class Book(BookBase):
    id: int
    created_at: datetime
    # reviews: list["Review"] = []
    model_config = ConfigDict(from_attributes=True)

class BookUpdate(BaseModel):
    title: str | None = Field(None, max_length=100, examples=["Война и мир"])
    author: str | None = Field(None, max_length=100, examples=["Лев Толстой"])
    pages: int | None = Field(None, gt=0, examples=[100, 250])
    rating: float | None = Field(None, ge=0.0, le=5.0, examples=[3.5])
