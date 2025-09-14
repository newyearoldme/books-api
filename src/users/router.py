from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from src.shared.database import get_db
from src.users.schemas import User, UserCreate, UserUpdate
from src.users.crud import user as user_crud
from src.auth.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=User)
async def create_user(user_data: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    existing_user = await user_crud.get_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    existing_email = await user_crud.get_by_email(db, user_data.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    return await user_crud.create(db, user_data)

@router.get("/me", response_model=User)
async def read_current_user(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user

@router.get("/", response_model=list[User])
async def read_users(db: Annotated[AsyncSession, Depends(get_db)], skip: int = 0, limit: int = 100):
    return await user_crud.get_all(db, skip, limit)

@router.get("/{user_id}", response_model=User)
async def read_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    db_user = await user_crud.get(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.get("/by_email/{email}", response_model=User)
async def read_user_by_email(email: str, db: Annotated[AsyncSession, Depends(get_db)]):
    db_user = await user_crud.get_by_email(db, email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.get("/by_username/{username}", response_model=User)
async def read_user_by_username(username: str, db: Annotated[AsyncSession, Depends(get_db)]):
    db_user = await user_crud.get_by_username(db, username)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=User)
async def update_user(user_id: int, user_data: UserUpdate, db: Annotated[AsyncSession, Depends(get_db)]):
    updated_user = await user_crud.update(db, user_id, user_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.delete("/{user_id}", response_model=User)
async def delete_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    deleted_user = await user_crud.delete(db, user_id)
    if not deleted_user:
        raise HTTPException(status_code=404, detail="User not found")
    return deleted_user
