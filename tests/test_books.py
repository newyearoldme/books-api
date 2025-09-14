import pytest

@pytest.mark.asyncio
async def test_create_book(async_client):
    """Тест создания книги"""
    book_data = {"title": "Test Book", "author": "Test Author", "pages": 100, "rating": 4.5}

    response = await async_client.post("/books/", json=book_data)

    assert response.status_code == 200
    assert response.json()["title"] == "Test Book"
    assert response.json()["author"] == "Test Author"
    assert response.json()["pages"] == 100
    assert response.json()["rating"] == 4.5
    assert "id" in response.json()
    assert "created_at" in response.json()

@pytest.mark.asyncio
async def test_get_books_list(async_client):
    """Тест получения списка всех книг"""
    books_data = [
        {"title": "Test Book 1", "author": "Test Author 1", "pages": 100},
        {"title": "Test Book 2", "author": "Test Author 2", "pages": 200}
    ]

    for book_data in books_data:
        await async_client.post("/books/", json=book_data)

    response = await async_client.get("/books/")
    books = response.json()

    assert response.status_code == 200
    assert isinstance(books, list)
    assert len(books) == 2
    
    assert books[0]["title"] == "Test Book 1"
    assert books[0]["author"] == "Test Author 1"
    assert books[0]["pages"] == 100
    assert books[1]["title"] == "Test Book 2"
    assert books[1]["author"] == "Test Author 2"
    assert books[1]["pages"] == 200

@pytest.mark.asyncio
async def test_get_book_by_id(async_client):
    """Тест получения книги по id"""
    book_data = {"title": "Test Book", "author": "Author", "pages": 100}
    create_response = await async_client.post("/books/", json=book_data)
    book_id = create_response.json()["id"]

    response = await async_client.get(f"/books/{book_id}")

    assert response.status_code == 200
    assert response.json()["id"] == book_id

@pytest.mark.asyncio
async def test_get_nonexistent_book(async_client):
    """Тест получения несуществующей книги"""
    response = await async_client.get("/books/9999")

    assert response.status_code == 404
    assert "detail" in response.json()

@pytest.mark.asyncio
async def test_update_book(async_client):
    """Тест обновления данных книги"""
    book_data = {"title": "Old title", "author": "Old author", "pages": 100}
    create_response = await async_client.post("/books/", json=book_data)
    book_id = create_response.json()["id"]

    response = await async_client.get("/books/")

    update_data = {"title": "New Title", "author": "New author", "rating": 5.0}
    response = await async_client.put(f"/books/{book_id}", json=update_data)

    assert response.status_code == 200
    assert response.json()["title"] == "New Title"
    assert response.json()["author"] == "New author"
    assert response.json()["rating"] == 5.0
    assert response.json()["id"] == book_id

@pytest.mark.asyncio
async def test_update_nonexistent_book(async_client):
    """Тест обновления несуществующей книги"""
    update_data = {"title": "New Title"}
    response = await async_client.put("/books/9999", json=update_data)
    
    assert response.status_code == 404
    assert "detail" in response.json()

@pytest.mark.asyncio
async def test_delete_book(async_client):
    """Тест удаления книги"""
    book_data = {"title": "To Delete", "author": "Author", "pages": 100}
    create_response = await async_client.post("/books/", json=book_data)
    book_id = create_response.json()["id"]
    
    response = await async_client.delete(f"/books/{book_id}")
    
    assert response.status_code == 200
    assert response.json()["title"] == "To Delete"
    
    get_response = await async_client.get(f"/books/{book_id}")
    assert get_response.status_code == 404

@pytest.mark.asyncio
async def test_delete_nonexistent_book(async_client):
    """Тест удаления несуществующей книги"""
    response = await async_client.delete("/books/9999")
    
    assert response.status_code == 404
    assert "detail" in response.json()

@pytest.mark.asyncio
async def test_get_top_rated_books(async_client):
    """Тест получения топовых книг по рейтингу"""
    books_data = [
        {"title": "Book 1", "author": "Author 1", "pages": 100, "rating": 4.0},
        {"title": "Book 2", "author": "Author 2", "pages": 200, "rating": 4.5},
        {"title": "Book 3", "author": "Author 3", "pages": 300, "rating": 3.5},
        {"title": "Book 4", "author": "Author 4", "pages": 400},
        {"title": "Book 5", "author": "Author 5", "pages": 500, "rating": 5.0},
    ]
    
    for book_data in books_data:
        await async_client.post("/books/", json=book_data)
    
    response = await async_client.get("/books/top_rated?limit=2")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 2
    
    books = response.json()
    assert books[0]["rating"] == 5.0
    assert books[1]["rating"] == 4.5
    
    book_titles = [book["title"] for book in books]
    assert "Book 4" not in book_titles

@pytest.mark.asyncio
async def test_get_top_rated_with_default_limit(async_client):
    """Тест получения топовых книг с лимитом по умолчанию"""
    for i in range(15):
        book_data = {
            "title": f"Book {i}",
            "author": f"Author {i}", 
            "pages": 100 + i,
            "rating": 3.0 + i * 0.1
        }
        await async_client.post("/books/", json=book_data)
    
    response = await async_client.get("/books/top_rated")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 10
    
    books = response.json()
    for i in range(len(books) - 1):
        assert books[i]["rating"] >= books[i + 1]["rating"]

@pytest.mark.asyncio
async def test_get_top_rated_with_zero_ratings(async_client):
    """Тест когда все книги имеют рейтинг 0.0"""
    books_data = [
        {"title": "Book 1", "author": "Author 1", "pages": 100},
        {"title": "Book 2", "author": "Author 2", "pages": 200},
        {"title": "Book 3", "author": "Author 3", "pages": 300},
    ]
    
    for book_data in books_data:
        await async_client.post("/books/", json=book_data)
    
    response = await async_client.get("/books/top_rated")
    
    assert response.status_code == 200
    assert len(response.json()) == 3
    assert all(book["rating"] == 0.0 for book in response.json())

@pytest.mark.asyncio
async def test_get_top_rated_with_custom_limit(async_client):
    """Тест получения топовых книг с кастомным лимитом"""
    for i in range(5):
        book_data = {
            "title": f"Book {i}",
            "author": f"Author {i}",
            "pages": 100 + i,
            "rating": 4.0 + i * 0.1
        }
        await async_client.post("/books/", json=book_data)
    
    response = await async_client.get("/books/top_rated?limit=3")
    
    assert response.status_code == 200
    assert len(response.json()) == 3
