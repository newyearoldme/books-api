from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from src.shared.database import get_db
from src.users.schemas import User, UserCreate, UserUpdate
from src.users.crud import user as user_crud
from src.auth.dependencies import get_current_user
from src.shared.exceptions import AlreadyExistsException, NotFoundException

router = APIRouter(prefix="/users", tags=["Users"])

@router.post(
    "/", 
    response_model=User,
    summary="Register a new user",
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Username or email already exists"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)
async def create_user(user_data: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    """
    ## Create a new user account
    
    **Validation:**
    - Username must be unique
    - Email must be unique
    - Password is hashed before storage
    """
    existing_user = await user_crud.get_by_username(db, user_data.username)
    if existing_user:
        raise AlreadyExistsException(
            detail="Username already taken",
            resource_type="user",
            field="username",
            value=user_data.username
        )
        
    existing_email = await user_crud.get_by_email(db, user_data.email)
    if existing_email:
        raise AlreadyExistsException(
            detail="Email already registered", 
            resource_type="user", 
            field="email", 
            value=user_data.email
        )
    
    return await user_crud.create(db, user_data)

@router.get(
    "/me", 
    response_model=User,
    summary="Get current user profile",
    responses={
        200: {"description": "User profile retrieved successfully"},
        401: {"description": "Not authenticated"},
        500: {"description": "Internal server error"}
    }    
)
async def read_current_user(current_user: Annotated[User, Depends(get_current_user)]):
    """
    ## Retrieve the profile of the currently authenticated user
    
    **Authentication:**
    - Requires valid JWT token
    """
    return current_user

@router.get(
    "/", 
    response_model=list[User],
    summary="Get paginated list of users",
    responses={
        200: {"description": "List of users retrieved successfully"},
        400: {"description": "Invalid pagination parameters"},
        500: {"description": "Internal server error"}
    }    
)
async def read_users(
    db: Annotated[AsyncSession, Depends(get_db)], 
    skip: int = Query(default=0, ge=0, description="Number of users to skip (min 0)"), 
    limit: int = Query(default=10, ge=0, le=100, description="Number of users to return (1-100)")):
    """
    ## Retrieve a paginated list of all users in the system
    
    **Query parameters:**
    - **skip**: Number of records to skip (min 0)
    - **limit**: Number of records to return (1-100), default: 10
    """
    return await user_crud.get_all(db, skip, limit)

@router.get(
    "/{user_id}", 
    response_model=User,
    summary="Get user by ID",
    responses={
        200: {"description": "User found successfully"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"}
    }    
)
async def read_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    """
    ## Retrieve a user by their unique ID
    
    **Path parameters:**
    - **user_id**: ID of the user to retrieve
    """
    db_user = await user_crud.get(db, user_id)
    if not db_user:
        raise NotFoundException(detail="User not found", resource_type="user", resource_id=user_id)
    return db_user

@router.get(
    "/by_email/{email}", 
    response_model=User,
    summary="Get user by email",
    responses={
        200: {"description": "User found successfully"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"}
    }    
)
async def read_user_by_email(email: str, db: Annotated[AsyncSession, Depends(get_db)]):
    """
    ## Retrieve a user by their email address
    
    **Path parameters:**
    - **email**: Email address of the user to retrieve
    """
    db_user = await user_crud.get_by_email(db, email)
    if not db_user:
        raise NotFoundException(detail="User not found", resource_type="user", resource_id=email)
    return db_user

@router.get(
    "/by_username/{username}", 
    response_model=User,
    summary="Get user by username",
    responses={
        200: {"description": "User found successfully"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"}
    }    
)
async def read_user_by_username(username: str, db: Annotated[AsyncSession, Depends(get_db)]):
    """
    ## Retrieve a user by their username
    
    **Path parameters:**
    - *username*: Username of the user to retrieve
    """
    db_user = await user_crud.get_by_username(db, username)
    if not db_user:
        raise NotFoundException(detail="User not found", resource_type="user", resource_id=username)
    return db_user

@router.put(
    "/{user_id}", 
    response_model=User,
    summary="Update user by ID",
    responses={
        200: {"description": "User updated successfully"},
        403: {"description": "Permission denied"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"}
    }
)
async def update_user(user_id: int, user_data: UserUpdate, db: Annotated[AsyncSession, Depends(get_db)]):
    """
    ## Update a user's information
        
    **Path parameters:**
    - **user_id**: ID of the user to update

    <u>Note: users can only update their own profile.</u>
    """
    updated_user = await user_crud.update(db, user_id, user_data)
    if not updated_user:
        raise NotFoundException(detail="User not found", resource_type="user", resource_id=user_id)
    return updated_user

@router.delete(
    "/{user_id}", 
    response_model=User,
    summary="Delete user by ID",
    responses={
        200: {"description": "User deleted successfully"},
        403: {"description": "Permission denied"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"}
    }    
)
async def delete_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    """
    # Delete a user account.
    
    **Path parameters:**
    - **user_id**: ID of the user to delete

    <u> Note: users can only delete their own account. This action is permanent and cannot be undone.</u>
    """
    deleted_user = await user_crud.delete(db, user_id)
    if not deleted_user:
        raise NotFoundException(detail="User not found", resource_type="user", resource_id=user_id)
    return deleted_user
