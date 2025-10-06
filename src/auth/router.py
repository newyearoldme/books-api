from fastapi import APIRouter

from src.auth.schemas import LoginRequestSchema
from src.auth.utils import create_access_token
from src.shared.database import DatabaseDep
from src.shared.exceptions import UnauthorizedException
from src.users.crud import user as user_crud

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    summary="User login",
    responses={
        200: {"description": "Successful login"},
        400: {"description": "Invalid credentials: incorrect username or password"},
        422: {"description": "Validation error"},
    },
)
async def login(login_data: LoginRequestSchema, db: DatabaseDep):
    """
    ## Authenticate user and return JWT access token.

    This endpoint validates user credentials and returns a JSON Web Token
    that should be included in subsequent requests in the Authorization header.

    **Request body:**
    - **username**: User's username (required)
    - **password**: User's password (required)

    **Response:**
    - **access_token**: JWT token for authenticated requests
    - **token_type**: Always "bearer"
    - **user_id**: ID of the authenticated user
    - **username**: Username of the authenticated user

    **Security:**
    - Passwords are hashed using bcrypt
    - JWT tokens expire after 30 minutes (by default)
    - Tokens must be included in Authorization header: `Bearer <token>`
    """
    user = await user_crud.authenticate(db, login_data.username, login_data.password)
    if not user:
        raise UnauthorizedException(detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
    }
