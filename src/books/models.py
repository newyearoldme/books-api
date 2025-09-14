from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import mapped_column, Mapped, relationship
from src.shared.database import Base

if TYPE_CHECKING:
    from src.reviews.models import ReviewModel

class BookModel(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    author: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    pages: Mapped[int] = mapped_column(nullable=False)
    rating: Mapped[float | None] = mapped_column(default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    reviews: Mapped[list["ReviewModel"]] = relationship(
        back_populates="book",
        cascade="all, delete-orphan",
        lazy="selectin"
        )

