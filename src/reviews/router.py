from fastapi import APIRouter

from src.auth.dependencies import CurrentUserDep, OwnershipOrAdminDep
from src.books.crud import book as book_crud
from src.reviews.crud import review as review_crud
from src.reviews.schemas import Review, ReviewCreate
from src.shared.database import DatabaseDep
from src.shared.exceptions import ForbiddenException, NotFoundException
from src.shared.pagination import PaginationDep
from src.users.crud import user as user_crud

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post(
    "/",
    response_model=Review,
    response_description="Review successfuly created",
    summary="Create a new review",
    responses={
        200: {"description": "Review created successfully", "model": Review},
        400: {"description": "Invalid rating or validation error"},
        404: {"description": "Book not found"},
        422: {"description": "Request body parsing error"},
        500: {"description": "Internal server error"},
    },
)
async def create_review(
    review_data: ReviewCreate,
    db: DatabaseDep,
    user: CurrentUserDep,
):
    """
    ## Create a new review for a book

    **Requirements**:
    - User must be authenticated
    - Book must exist
    - Rating must be between 1 and 5

    <u>Note: users can only create reviews for themselves.</u>
    """
    book = await book_crud.get(db, review_data.book_id)
    if not book:
        raise NotFoundException(
            detail="Book not found",
            resource_type="book",
            resource_id=review_data.book_id,
        )

    review_dict = review_data.model_dump()
    review_dict["user_id"] = user.id

    return await review_crud.create(db, review_dict)


@router.get(
    "/",
    response_model=list[Review],
    summary="Get paginated list of reviews",
    responses={
        200: {"description": "List of reviews retrieved successfully"},
        400: {"description": "Invalid pagination parameters"},
        500: {"description": "Internal server error"},
    },
)
async def read_reviews(db: DatabaseDep, pagination: PaginationDep):
    """
    ## Retrieve a paginated list of all reviews in the system.


    **Query parameters**:
    - **skip**: Number of records to skip (min 0)
    - **limit**: Number of records to return (1-100), default: 10


    **Example**:
    - `GET /reviews/?skip=0&limit=20` - first page of 20 reviews
    - `GET /reviews/?skip=20&limit=20` - second page of 20 reviews
    """
    return await review_crud.get_all(db, pagination.skip, pagination.limit)


@router.get(
    "/book/{book_id}",
    response_model=list[Review],
    summary="Get reviews for a specific book",
    responses={
        200: {"description": "Book reviews retrieved successfully"},
        404: {"description": "Book not found"},
        500: {"description": "Internal server error"},
    },
)
async def read_reviews_by_book(book_id: int, db: DatabaseDep):
    """
    ## Retrieve all reviews for a specific book

    **Path parameters**:
    - **book_id**: ID of the book to get reviews for
    """
    book = await book_crud.get(db, book_id)
    if not book:
        raise NotFoundException(
            detail="Book not found", resource_type="book", resource_id=book_id
        )
    return await review_crud.get_by_book(db, book_id)


@router.get(
    "/user/{user_id}",
    response_model=list[Review],
    summary="Get reviews by a specific user",
    responses={
        200: {"description": "User reviews retrieved successfully"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"},
    },
)
async def read_reviews_by_user(user_id: int, db: DatabaseDep):
    """
    ## Retrieve all reviews created by a specific user

    **Path parameters:**
    - **user_id**: ID of the user to get reviews for
    """
    user = await user_crud.get(db, user_id)
    if not user:
        raise NotFoundException(
            detail="User not found", resource_type="user", resource_id=user_id
        )
    return await review_crud.get_by_user(db, user_id)


@router.get(
    "/{review_id}",
    response_model=Review,
    summary="Get review by ID",
    responses={
        200: {"description": "Review found successfully"},
        404: {"description": "Review not found"},
        500: {"description": "Internal server error"},
    },
)
async def read_review(review_id: int, db: DatabaseDep):
    """
    ## Retrieve a specific review by its ID

    **Path parameters:**
    - **review_id**: ID of the review to retrieve
    """
    review = await review_crud.get(db, review_id)
    if not review:
        raise NotFoundException(
            detail="Review not found", resource_type="review", resource_id=review_id
        )
    return review


@router.delete(
    "/{review_id}",
    response_model=Review,
    summary="Delete a review",
    responses={
        200: {"description": "Review deleted successfully"},
        403: {"description": "Permission denied - not your review"},
        404: {"description": "Review not found"},
        500: {"description": "Internal server error"},
    },
)
async def delete_review(
    review_id: int,
    db: DatabaseDep,
    current_user: OwnershipOrAdminDep,
):
    """
    ## Delete a review by its ID

    **Path parameters:**
    - **review_id**: ID of the review to delete

    <u>Note: Users can only delete their own reviews, admins can delete any review. 
    This action is permanent and cannot be undone.</u>
    """
    review = await review_crud.get(db, review_id)
    if not review:
        raise NotFoundException(
            detail="Review not found", resource_type="review", resource_id=review_id
        )

    return await review_crud.delete(db, review_id)


@router.put(
    "/{review_id}",
    response_model=Review,
    summary="Update a review",
    responses={
        200: {"description": "Review updated successfully"},
        403: {"description": "Permission denied - not your review"},
        404: {"description": "Review not found"},
        500: {"description": "Internal server error"},
    },
)
async def update_review(
    review_id: int,
    review_data: ReviewCreate,
    db: DatabaseDep,
    current_user: CurrentUserDep,
):
    """
    ## Update an existing review

    **Path parameters:**
    - *review_id*: ID of the review to update

    <u>Note: users can only update their own reviews.</u>
    """
    review = await review_crud.get(db, review_id)
    if not review:
        raise NotFoundException(
            detail="Review not found", resource_type="review", resource_id=review_id
        )

    if review.user_id != current_user.id:
        raise ForbiddenException(detail="Can only edit your own reviews")

    return await review_crud.update(db, review_id, review_data)


@router.get("/{book_id}/average_rating", response_model=float | None)
async def get_average_rating(book_id: int, db: DatabaseDep):
    """
    ## Calculate and return the average rating for a specific book

    **Path parameters:**
    - **book_id**: ID of the book to get average rating for

    <u>Note: returns `null` if the book has no ratings yet.</u>
    """
    book = await book_crud.get(db, book_id)
    if not book:
        raise NotFoundException(
            detail="Book not found", resource_type="book", resource_id=book_id
        )
    return await review_crud.get_average_rating(db, book_id)
