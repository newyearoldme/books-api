from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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
    model_config = ConfigDict(from_attributes=True)


class BookUpdate(BaseModel):
    title: str | None = Field(None, max_length=100, examples=["Война и мир"])
    author: str | None = Field(None, max_length=100, examples=["Лев Толстой"])
    pages: int | None = Field(None, gt=0, examples=[100, 250])
    rating: float | None = Field(None, ge=0.0, le=5.0, examples=[3.5])
