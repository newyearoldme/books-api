from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from src.shared.database import get_db
from src.users.crud import user as user_crud
from src.auth.schemas import LoginRequestSchema
from src.auth.utils import create_access_token


router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login")
async def login(login_data: LoginRequestSchema, db: Annotated[AsyncSession, Depends(get_db)]):
    user = await user_crud.authenticate(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username
    }
