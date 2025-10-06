from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.database import Base

if TYPE_CHECKING:
    from src.books.models import FavoriteModel
    from src.reviews.models import ReviewModel


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    banned_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    ban_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)

    favorites: Mapped["FavoriteModel"] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    reviews: Mapped[list["ReviewModel"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )
