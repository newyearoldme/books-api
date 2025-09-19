from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from src.shared.database import get_db
from src.shared.exceptions import AlreadyExistsException, NotFoundException
from src.books.schemas import Book, BookCreate, BookUpdate
from src.books.crud import book as book_crud

router = APIRouter(prefix="/books", tags=["Books"])

@router.post(
    "/",
    response_model=Book,
    response_description="Book successfuly created",
    summary="Create a new book",
    responses={
        201: {"description": "Book created successfully", "model": Book},
        400: {"description": "Invalid input data"},
        409: {"description": "Book already exists"},
        500: {"description": "Internal server error"}
    }
)
async def create_book(book_data: BookCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    """
    ## Create a new book in the system

    **Data parameters**:
    - **title**: book title (required)
    - **author**: book author (required) 
    - **pages**: number of pages (required)
    - **rating**: optional rating (0.0-5.0)
    """
    existing_book = await book_crud.get_by_title_author(db, book_data.title, book_data.author)
    if existing_book:
        raise AlreadyExistsException(
            detail="Book already exists", 
            resource_type="book", 
            field="title_author",
            value=f"{book_data.title} by {book_data.author}"    
        )

    return await book_crud.create(db, book_data)

@router.get(
    "/", 
    response_model=list[Book],
    summary="Gets paginated list of books",
    responses={
        200: {"description": "List of books retrieved successfully"},
        400: {"description": "Invalid pagination parameters"},
        500: {"description": "Internal server error"}
    }
)
async def read_books(
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(default=0, ge=0, description="Number of records to skip (min 0)"), 
    limit: int = Query(default=10, ge=0, le=100, description="Number of records to return (1-100)")
):
    """
    ## Retrieve a paginated list of all books in the system
    
    **Query parameters**:
    - **skip**: Number of records to skip (min 0)
    - **limit**: Number of records to return (1-100), default: 10

    **Example**:
    - `GET /books/?skip=0&limit=20` - first page of 20 books
    - `GET /books/?skip=20&limit=20` - second page of 20 books
    """
    return await book_crud.get_all(db, skip, limit)

@router.get(
    "/top_rated", 
    response_model=list[Book],
    summary="Get top rated books",
    responses={
        200: {"description": "Top rated books retrieved successfully"},
        500: {"description": "Internal server error"}
    }
)
async def get_top_books(
    db: Annotated[AsyncSession, Depends(get_db)], 
    limit: int = Query(default=10, ge=1, le=50, description="Number of top books to return (1-50)")
):
    """
    ## Retrieve the highest rated books in descending order
        
    **Query parameters**:
    - **limit**: number of top books to return (1-50), default: 10

    <u>Note: books without ratings are excluded from the results. Results are sorted by rating descending.</u>
    """
    return await book_crud.get_top_rated(db, limit)

@router.get(
    "/{book_id}", 
    response_model=Book,
    summary="Get book by ID",
    responses={
        200: {"description": "Book found successfully", "model": Book},
        404: {"description": "Book not found with the specified ID"},
        422: {"description": "Invalid book ID format"},
        500: {"description": "Internal server error"}
    }
)
async def read_book(book_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    """
    ## Retrieve a specific book by its unique identifier
    
    **Path parameters**:
    - **book_id**: unique integer ID of the book
    """
    db_book = await book_crud.get(db, book_id)
    if not db_book:
        raise NotFoundException(detail="Book not found", resource_type="book", resource_id=book_id)
    return db_book

@router.put(
    "/{book_id}", 
    response_model=Book,
    summary="Update book by ID",
    responses={
        200: {"description": "Book updated successfully", "model": Book},
        404: {"description": "Book not found with the specified ID"},
        400: {"description": "Invalid update data"},
        422: {"description": "Invalid request body or book ID"},
        500: {"description": "Internal server error"}
    }
)
async def update_book(book_id: int, book_data: BookUpdate, db: Annotated[AsyncSession, Depends(get_db)]):
    """
    ## Update an existing book's information
    
    **Path parameters**:
    - **book_id**: Unique integer ID of the book to update
    
    <u>Note: Only provided fields will be updated (partial update).</u>
    """
    updated_book = await book_crud.update(db, book_id, book_data)
    if not updated_book:
        raise NotFoundException(detail="Book not found", resource_type="book", resource_id=book_id)
    return updated_book

@router.delete(
    "/{book_id}", 
    response_model=Book,
    summary="Delete book by ID",
    responses={
        200: {"description": "Book deleted successfully", "model": Book},
        404: {"description": "Book not found with the specified ID"},
        422: {"description": "Invalid book ID format"},
        500: {"description": "Internal server error"}
    }
)
async def delete_book(book_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    """
    ## Delete a book from the system
    
    **Path parameters**:
    - **book_id**: Unique integer ID of the book to delete
    
    <u>Note: This action is permanent and cannot be undone.</u>
    """
    deleted_book = await book_crud.delete(db, book_id)
    if not deleted_book:
        raise NotFoundException(detail="Book not found", resource_type="book", resource_id=book_id)
    return deleted_book
