from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from src.auth.dependencies import get_current_user
from src.shared.exceptions import NotFoundException, AlreadyExistsException
from src.shared.database import get_db
from src.users.schemas import User
from src.favorites.schemas import Favorite, FavoriteWithBook, FavoriteStatus
from src.favorites.crud import favorite as favorite_crud
from src.books.crud import book as book_crud

router = APIRouter(prefix="/favorites", tags=["Favorites"])

@router.post(
    "/books/{book_id}", 
    response_model=Favorite,
    summary="Add book to favorites",
    responses={
        200: {"description": "The book has been added to favorites", "model": Favorite},
        400: {"description": "Book already in favorites"},
        401: {"description": "Not authenticated"},
        404: {"description": "Book not found with the specified ID"},
        422: {"description": "Invalid book ID format"},
        500: {"description": "Internal server error"}
    }
)
async def add_to_favorites(
    book_id: int, 
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)] 
    ):
    """
    ## Add a book to the current user's favorites list
    
    **Args**:
    - **book_id**: ID of the book to add to favorites
    - **current_user**: authenticated user from JWT token
    """
    book = await book_crud.get(db, book_id)
    if not book:
        raise NotFoundException(detail="Book not found", resource_type="book", resource_id=book_id)
    
    in_favorite = await favorite_crud.is_book_in_favorites(db, current_user.id, book_id)
    if not in_favorite:
        return await favorite_crud.add_to_favorites(db, current_user.id, book_id)

    raise AlreadyExistsException(detail="Book already in favorites", resource_type="book", field="favorite")

@router.delete(
    "/books/{book_id}", 
    summary="Remove book from favorites",
    responses={
        204: {"description": "Book removed from favorites successfully"},
        401: {"description": "Not authenticated"},
        404: {"description": "Book not found in favorites"},
        500: {"description": "Internal server error"}
    }
)
async def remove_from_favorites(
    book_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    ## Remove a book from the current user's favorites
    
    **Permissions:**
    - User must be authenticated
    - Book must be in user's favorites
    
    **Path parameters:**
    - **book_id**: ID of the book to remove from favorites
    """
    removed = await favorite_crud.remove_from_favorites(db, current_user.id, book_id)
    if not removed:
        raise NotFoundException(detail="Book not found in favorites", resource_type="book", resource_id=book_id)

@router.get(
    "/me",
    response_model=list[FavoriteWithBook],
    summary="Get user's favorites",
    responses={
        200: {"description": "Favorite books retrieved"},
        401: {"description": "Not authenticated"},
        500: {"description": "Internal server error"}
    }
)
async def get_favorites(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """
    ## Retrieve a paginated list of all user's favorites
    
    **Query parameters**:
    - **skip**: Number of records to skip (min 0)
    - **limit**: Number of records to return (1-100), default: 10

    <u>Note: user must be authenticated</u>
    """
    return await favorite_crud.get_user_favorites(db, current_user.id, skip, limit)

@router.get(
    "/books/{book_id}/status",
    response_model=FavoriteStatus,
    summary="Check favorite status",
    responses={
        200: {"description": "Favorite status retrieved"},
        401: {"description": "Not authenticated"},
        404: {"description": "Book not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_favorite_status(
    book_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    ## Check if book is in user's favorites

    **Path parameters:**
    - **book_id**: ID of the book to check

    <u>Note: user must be authenticated</u>
    """
    book = await book_crud.get(db, book_id)
    if not book:
        raise NotFoundException(detail="Book not found", resource_type="book", resource_id=book_id)
    
    is_favorite = await favorite_crud.is_book_in_favorites(db, current_user.id, book_id)
    return {"is_favorite": is_favorite}
