import pytest

@pytest.mark.asyncio
async def test_add_to_favorites(async_client, auth_token, test_book):
    """Тест добавления книги в избранное"""
    response = await async_client.post(
        f"/favorites/books/{test_book['id']}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert response.json()["book_id"] == test_book["id"]

@pytest.mark.asyncio
async def test_add_duplicate_favorite(async_client, auth_token, test_book):
    """Тест добавления дубликата книги в избранное"""
    response1 = await async_client.post(
        f"/favorites/books/{test_book['id']}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response1.status_code == 200 

    response2 = await async_client.post(
        f"/favorites/books/{test_book['id']}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response2.status_code == 409

@pytest.mark.asyncio
async def test_remove_from_favorites(async_client, auth_token, test_book):
    """Тест удаления книги с избранного"""
    await async_client.post(
        f"/favorites/books/{test_book['id']}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    response = await async_client.delete(
        f"/favorites/books/{test_book['id']}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_favorites(async_client, auth_token, test_book):
    """Тест получения избранных пользователя"""
    await async_client.post(
        f"/favorites/books/{test_book['id']}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    response = await async_client.get(
        "/favorites/me",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["book"]["id"] == test_book["id"]

@pytest.mark.asyncio
async def test_favorite_status(async_client, auth_token, test_book):
    """Тест проверки книги в избранном"""
    response = await async_client.get(
        f"/favorites/books/{test_book['id']}/status",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert response.json()["is_favorite"] == False

    await async_client.post(
        f"/favorites/books/{test_book['id']}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    response = await async_client.get(
        f"/favorites/books/{test_book['id']}/status",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert response.json()["is_favorite"] == True

@pytest.mark.asyncio
async def test_add_to_favorites_nonexistent_book(async_client, auth_token):
    """Тест добавления несуществующей книги в избранное"""
    response = await async_client.post(
        "/favorites/books/9999",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_remove_nonexistent_favorite(async_client, auth_token):
    """Тест удаления с избранного несуществующей книги"""
    response = await async_client.delete(
        "/favorites/books/9999",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 404
