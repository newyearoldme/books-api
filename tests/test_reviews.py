import pytest

@pytest.mark.asyncio
async def test_create_review(async_client, test_user, auth_token, test_book):
    """Тест создания отзыва"""
    review_data = {
        "text": "Great book!",
        "rating": 5,
        "book_id": test_book["id"]
    }

    response = await async_client.post("/reviews/", json=review_data, headers={"Authorization": f"Bearer {auth_token}"})

    assert response.status_code == 200
    assert response.json()["text"] == "Great book!"
    assert response.json()["rating"] == 5
    assert response.json()["book_id"] == test_book["id"]
    assert response.json()["user_id"] == test_user["id"]

@pytest.mark.asyncio
async def test_get_review_by_book(async_client, test_user, auth_token, test_book):
    """Тест получения отзыва для книги"""        
    reviews_data = [
        {"text": "Good", "rating": 4, "book_id": test_book["id"]},
        {"text": "Great", "rating": 5, "book_id": test_book["id"]}
    ]

    for review_data in reviews_data:
        await async_client.post("/reviews/", json=review_data, headers={"Authorization": f"Bearer {auth_token}"})

    response = await async_client.get(f"/reviews/book/{test_book['id']}")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert all(review["book_id"] == test_book["id"] for review in response.json())
    assert all(review["user_id"] == test_user["id"] for review in response.json())

@pytest.mark.asyncio
async def test_get_reviews_by_user(async_client, test_user, auth_token, test_book):
    """Тест получения отзывов пользователя"""
    review_data = {"text": "Good", "rating": 4, "book_id": test_book["id"]}
    await async_client.post("/reviews/", json=review_data, headers={"Authorization": f"Bearer {auth_token}"})

    response = await async_client.get(f"/reviews/user/{test_user['id']}")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["user_id"] == test_user["id"]

@pytest.mark.asyncio
async def test_get_average_rating(async_client, auth_token, test_book):
    reviews_data = [
        {"text": "Average", "rating": 3, "book_id": test_book["id"]},
        {"text": "Good", "rating": 4, "book_id": test_book["id"]},
        {"text": "Excellent", "rating": 5, "book_id": test_book["id"]}
    ]

    for review_data in reviews_data:
        await async_client.post("/reviews/", json=review_data, headers={"Authorization": f"Bearer {auth_token}"})

    response = await async_client.get(f"/reviews/{test_book['id']}/average_rating")

    assert response.status_code == 200
    assert response.json() == 4.0   # (3 + 4 + 5) / 3 == 4

@pytest.mark.asyncio
async def test_create_review_nonexistent_book(async_client, auth_token):
    """Тест создания отзыва для несуществующей книги"""
    review_data = {"text": "Good", "rating": 4, "book_id": 9999}

    response = await async_client.post("/reviews/", json=review_data, headers={"Authorization": f"Bearer {auth_token}"})

    assert response.status_code == 404
    assert "book" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_get_reviews_nonexistent_book(async_client):
    """Тест получения отзывов несуществующей книги"""
    response = await async_client.get("/reviews/book/9999")

    assert response.status_code == 404
    assert "book" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_get_reviews_nonexistent_user(async_client):
    """Тест получения отзывов несуществующего пользователя"""
    response = await async_client.get("/reviews/user/9999")

    assert response.status_code == 404
    assert "user" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_update_own_review(async_client, auth_token, test_book):
    """Тест обновления своего отзыва"""    
    review_data = {"text": "Old text", "rating": 3, "book_id": test_book["id"]}
    review_response = await async_client.post("/reviews/", json=review_data, headers={"Authorization": f"Bearer {auth_token}"})
    review_id = review_response.json()["id"]
    
    update_data = {"text": "Updated text", "rating": 5, "book_id": test_book["id"]}
    response = await async_client.put(f"/reviews/{review_id}", json=update_data, headers={"Authorization": f"Bearer {auth_token}"})
    
    assert response.status_code == 200
    assert response.json()["text"] == "Updated text"
    assert response.json()["rating"] == 5
