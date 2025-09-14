from pydantic import BaseModel, Field, ConfigDict, EmailStr
from datetime import datetime


class UserBase(BaseModel):
    username: str = Field(..., min_length=4, max_length=50, examples=["Вася Пупкин"])
    email: EmailStr = Field(..., examples=["user@example.com"])

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, examples=["my_greatest_password1234"])

class User(UserBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    username: str | None = Field(None, min_length=4, max_length=50, examples=["Вася Пупкин"])
    email: EmailStr | None = Field(None, examples=["user@example.com"])
    password: str | None = Field(None, min_length=6, examples=["my_greatest_password1234"])
