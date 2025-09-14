from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from src.shared.database import get_db
from src.reviews.schemas import Review, ReviewCreate
from src.reviews.crud import review as review_crud
from src.books.crud import book as book_crud
from src.users.crud import user as user_crud
from src.users.schemas import User
from src.auth.dependencies import get_current_user

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.post("/", response_model=Review)
async def create_review(
    review_data: ReviewCreate, 
    db: Annotated[AsyncSession, Depends(get_db)], 
    current_user: Annotated[User, Depends(get_current_user)]
    ):
    book = await book_crud.get(db, review_data.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if not 1 <= review_data.rating <= 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    review_dict = review_data.model_dump()
    review_dict["user_id"] = current_user.id
    
    return await review_crud.create(db, review_dict)

@router.get("/", response_model=list[Review])
async def read_reviews(db: Annotated[AsyncSession, Depends(get_db)], skip: int = 0, limit: int = 100):
    return await review_crud.get_all(db, skip, limit)

@router.get("/book/{book_id}", response_model=list[Review])
async def read_reviews_by_book(book_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    book = await book_crud.get(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return await review_crud.get_by_book(db, book_id)

@router.get("/user/{user_id}", response_model=list[Review])
async def read_reviews_by_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    user = await user_crud.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await review_crud.get_by_user(db, user_id)

@router.get("/{review_id}", response_model=Review)
async def read_review(review_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    review = await review_crud.get(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review

@router.delete("/{review_id}", response_model=Review)
async def delete_review(
    review_id: int, 
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
    ):
    review = await review_crud.get(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    if review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can only delete your own reviews")

    return await review_crud.delete(db, review_id)

@router.put("/{review_id}", response_model=Review)
async def update_review(
    review_id: int,
    review_data: ReviewCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    review = await review_crud.get(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    if review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can only edit your own reviews")
    
    return await review_crud.update(db, review_id, review_data)

@router.get("/{book_id}/average_rating", response_model=float | None)
async def get_average_rating(book_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    book = await book_crud.get(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return await review_crud.get_average_rating(db, book_id)
