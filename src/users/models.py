from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import mapped_column, Mapped, relationship
from src.shared.database import Base

if TYPE_CHECKING:
    from src.reviews.models import ReviewModel
    from src.books.models import FavoriteModel

class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    favorites: Mapped["FavoriteModel"] = relationship(back_populates="user", cascade="all, delete-orphan")
    reviews: Mapped[list["ReviewModel"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
        )
