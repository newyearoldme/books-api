from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, DateTime, func, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from src.shared.database import Base

if TYPE_CHECKING:
    from src.books.models import BookModel
    from src.users.models import UserModel

class ReviewModel(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(String(1000))
    rating: Mapped[int] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    book: Mapped["BookModel"] = relationship(back_populates="reviews", lazy="selectin")
    user: Mapped["UserModel"] = relationship(back_populates="reviews", lazy="selectin")
