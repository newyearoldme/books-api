from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from src.shared.database import get_db
from src.books.schemas import Book, BookCreate, BookUpdate
from src.books.crud import book as book_crud

router = APIRouter(prefix="/books", tags=["Books"])

@router.post("/", response_model=Book)
async def create_book(book_data: BookCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    return await book_crud.create(db, book_data)

@router.get("/", response_model=list[Book])
async def read_books(db: Annotated[AsyncSession, Depends(get_db)], skip: int = 0, limit: int = 100):
    return await book_crud.get_all(db, skip, limit)

@router.get("/{book_id}", response_model=Book)
async def read_book(book_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    db_book = await book_crud.get(db, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

@router.get("/top_rated", response_model=list[Book])
async def get_top_books(db: Annotated[AsyncSession, Depends(get_db)], limit: int = 10):
    return await book_crud.get_top_rated(db, limit)

@router.put("/{book_id}", response_model=Book)
async def update_book(book_id: int, book_data: BookUpdate, db: Annotated[AsyncSession, Depends(get_db)]):
    updated_book = await book_crud.update(db, book_id, book_data)
    if not updated_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return updated_book

@router.delete("/{book_id}", response_model=Book)
async def delete_book(book_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    deleted_book = await book_crud.delete(db, book_id)
    if not deleted_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return deleted_book
