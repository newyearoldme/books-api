import pytest

@pytest.mark.asyncio
async def test_create_user(async_client):
    """Тест создания пользователя"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "securepassword123"
    }
    response = await async_client.post("/users/", json=user_data)
    
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
    assert response.json()["email"] == "test@example.com"
    assert "password" not in response.json()
    assert "id" in response.json()

@pytest.mark.asyncio
async def test_create_duplicate_username(async_client):
    """Тест создания пользователя с существующим username"""
    user_data = {
        "username": "duplicate",
        "email": "test1@example.com",
        "password": "password123"
    }
    
    await async_client.post("/users/", json=user_data)
    
    duplicate_data = {
        "username": "duplicate",
        "email": "test2@example.com",
        "password": "password456"
    }
    response = await async_client.post("/users/", json=duplicate_data)
    
    assert response.status_code == 400
    assert "username" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_create_duplicate_email(async_client):
    """Тест создания пользователя с существующей email"""
    user_data = {
        "username": "testuser1",
        "email": "duplicate@example.com",
        "password": "password123"
    }
    
    await async_client.post("/users/", json=user_data)
    
    duplicate_data = {
        "username": "testuser2",
        "email": "duplicate@example.com",
        "password": "password456"
    }
    response = await async_client.post("/users/", json=duplicate_data)
    
    assert response.status_code == 400
    assert "email" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_get_user_by_id(async_client):
    """Тест получения пользователя по id"""
    user_data = {
        "username": "testuser",
        "email": "duplicate@example.com",
        "password": "password123"
    }

    create_response = await async_client.post("/users/", json=user_data)
    user_id = create_response.json()["id"]

    response = await async_client.get(f"/users/{user_id}")
    
    assert response.status_code == 200
    assert response.json()["id"] == user_id
    assert response.json()["username"] == "testuser"

@pytest.mark.asyncio
async def test_get_user_by_email(async_client):
    """Тест получения пользователя по электронной почте"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }

    create_response = await async_client.post("/users/", json=user_data)
    email = create_response.json()["email"]

    response = await async_client.get(f"/users/by_email/{email}")
    
    assert response.status_code == 200
    assert response.json()["email"] == email
    assert response.json()["username"] == "testuser"

@pytest.mark.asyncio
async def test_get_user_by_username(async_client):
    """Тест получения пользователя по username"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }

    create_response = await async_client.post("/users/", json=user_data)
    username = create_response.json()["username"]

    response = await async_client.get(f"/users/by_username/{username}")
    
    assert response.status_code == 200
    assert response.json()["username"] == username
    assert response.json()["username"] == "testuser"

@pytest.mark.asyncio
async def test_get_users(async_client):
    """Тест получения списка пользователей"""
    response = await async_client.get("/users/")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_update_user(async_client):
    """Тест обновления пользователя"""
    user_data = {
        "username": "olduser",
        "email": "old@example.com",
        "password": "oldpassword"
    }
    create_response = await async_client.post("/users/", json=user_data)
    user_id = create_response.json()["id"]
    
    update_data = {
        "username": "newuser",
        "email": "new@example.com"
    }
    response = await async_client.put(f"/users/{user_id}", json=update_data)
    
    assert response.status_code == 200
    assert response.json()["username"] == "newuser"
    assert response.json()["email"] == "new@example.com"

@pytest.mark.asyncio
async def test_update_user_password(async_client):
    """Тест обновления пароля пользователя"""
    user_data = {
        "username": "passworduser",
        "email": "password@example.com",
        "password": "oldpassword"
    }
    create_response = await async_client.post("/users/", json=user_data)
    user_id = create_response.json()["id"]
    
    update_data = {"password": "newpassword123"}
    response = await async_client.put(f"/users/{user_id}", json=update_data)
    
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_delete_user(async_client):
    """Тест удаления пользователя"""
    user_data = {
        "username": "todelete",
        "email": "delete@example.com",
        "password": "password123"
    }
    create_response = await async_client.post("/users/", json=user_data)
    user_id = create_response.json()["id"]
    
    response = await async_client.delete(f"/users/{user_id}")
    
    assert response.status_code == 200
    assert response.json()["username"] == "todelete"
    
    get_response = await async_client.get(f"/users/{user_id}")
    assert get_response.status_code == 404
