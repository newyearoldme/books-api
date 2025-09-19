from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.auth.router import router as auth_router
from src.shared.exceptions import global_exception_handler
from src.favorites.router import router as favorite_router
from src.books.router import router as book_router
from src.reviews.router import router as review_router
from src.users.router import router as user_router

app = FastAPI(
    title="Books API",
    description="An API for book managment with authentication",
    version="1.0.0"
    )

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(Exception, global_exception_handler)

routers = [
    auth_router,
    book_router,
    favorite_router,
    review_router,
    user_router
]

for router in routers:
    app.include_router(router)

