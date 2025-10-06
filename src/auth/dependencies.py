from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from src.auth.utils import verify_token
from src.shared.database import DatabaseDep
from src.shared.exceptions import (
    ForbiddenException,
    UnauthorizedException,
    ValidationException,
)
from src.users.crud import user as user_crud
from src.users.schemas import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DatabaseDep,
):
    payload = verify_token(token)
    if not payload:
        raise UnauthorizedException("Invalid token format")

    user_id: int = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException("Missing user ID in token")

    user = await user_crud.get(db, user_id)
    if user is None:
        raise UnauthorizedException("User not found")

    if not user.is_active:
        raise ValidationException("Account is deactivated")

    if user.is_banned:
        raise ValidationException("Account is banned")

    return user


async def require_admin(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.is_admin:
        raise ForbiddenException("Admin access required")
    return current_user


async def require_ownership_or_admin(
    user_id: int, current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    if current_user.id != user_id and not current_user.is_admin:
        raise ForbiddenException("Access denied")
    return current_user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
AdminDep = Annotated[User, Depends(require_admin)]
OwnershipOrAdminDep = Annotated[User, Depends(require_ownership_or_admin)]
