from pydantic import BaseModel, ConfigDict
from datetime import datetime
from src.books.schemas import Book

class FavoriteBase(BaseModel):
    book_id: int

class FavoriteCreate(FavoriteBase):
    pass

class FavoriteUpdate(FavoriteBase):
    pass

class Favorite(FavoriteBase):
    id: int
    user_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class FavoriteWithBook(Favorite):
    book: Book
    
    model_config = ConfigDict(from_attributes=True)

class FavoriteStatus(BaseModel):
    is_favorite: bool
