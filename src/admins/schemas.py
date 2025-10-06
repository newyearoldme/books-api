from datetime import datetime

from pydantic import BaseModel, Field

from src.users.schemas import User


class UserAdminUpdate(BaseModel):
    username: str | None = None
    email: str | None = None
    password: str | None = None
    is_active: bool | None = None
    is_admin: bool | None = None
    is_banned: bool | None = None
    ban_reason: str | None = Field(None, max_length=500)


class UserBanRequest(BaseModel):
    ban_reason: str | None = Field(None, max_length=500)


class AdminUserResponse(User):
    is_banned: bool
    ban_reason: str | None = Field(None, max_length=500, examples=["Плохо себя вёл"])
    is_admin: bool
    banned_at: datetime | None = None
