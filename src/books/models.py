from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.database import Base

if TYPE_CHECKING:
    from src.favorites.models import FavoriteModel
    from src.reviews.models import ReviewModel


class BookModel(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), index=True)
    author: Mapped[str] = mapped_column(String(100), index=True)
    pages: Mapped[int] = mapped_column()
    rating: Mapped[float | None] = mapped_column(default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    favorited_by: Mapped["FavoriteModel"] = relationship(
        back_populates="book", cascade="all, delete-orphan"
    )
    reviews: Mapped[list["ReviewModel"]] = relationship(
        back_populates="book", cascade="all, delete-orphan", lazy="selectin"
    )
