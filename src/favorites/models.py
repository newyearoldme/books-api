from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import DateTime, func, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from src.shared.database import Base

if TYPE_CHECKING:
    from src.users.models import UserModel
    from src.books.models import BookModel

class FavoriteModel(Base):
    __tablename__ = "favorites"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    user: Mapped["UserModel"] = relationship(back_populates="favorites")
    book: Mapped["BookModel"] = relationship(back_populates="favorited_by")
