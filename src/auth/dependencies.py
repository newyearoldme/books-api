from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from src.shared.exceptions import UnauthorizedException
from src.shared.database import get_db
from src.users.crud import user as user_crud
from src.auth.utils import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[AsyncSession, Depends(get_db)]):
    payload = verify_token(token)
    if not payload:
        raise UnauthorizedException("Invalid token format")
    
    user_id: int = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException("Missing user ID in token")
    
    user = await user_crud.get(db, user_id)
    if user is None:
        raise UnauthorizedException("User not found")
      
    return user
