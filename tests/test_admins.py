import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_regular_user_cannot_create_book(
    async_client: AsyncClient, regular_token: str
):
    """Тест что обычный пользователь не может создавать книги"""
    book_data = {"title": "User Book", "author": "User", "pages": 100}
    response = await async_client.post(
        "/books/", json=book_data, headers={"Authorization": f"Bearer {regular_token}"}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_anonymous_cannot_create_book(async_client: AsyncClient):
    """Тест что анонимный пользователь не может создавать книги"""
    book_data = {"title": "Anonymous Book", "author": "Anon", "pages": 100}
    response = await async_client.post("/books/", json=book_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_admin_get_users_unauthorized(
    async_client: AsyncClient, regular_token: str
):
    """Тест что обычный пользователь не может получить список пользователей"""
    response = await async_client.get(
        "/users/", headers={"Authorization": f"Bearer {regular_token}"}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_deactivate_user(async_client: AsyncClient, admin_token: str):
    """Тест деактивации пользователя админом"""
    user_data = {
        "username": "todeactivate",
        "email": "deactivate@example.com",
        "password": "password123",
    }
    create_response = await async_client.post("/users/", json=user_data)
    user_id = create_response.json()["id"]

    response = await async_client.post(
        f"/admin/users/{user_id}/deactivate",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert not response.json()["is_active"]
    assert response.json()["username"] == "todeactivate"


@pytest.mark.asyncio
async def test_admin_activate_user(async_client: AsyncClient, admin_token: str):
    """Тест активации пользователя админом"""
    user_data = {
        "username": "toactivate",
        "email": "activate@example.com",
        "password": "password123",
        "is_active": False,
    }
    create_response = await async_client.post("/users/", json=user_data)
    user_id = create_response.json()["id"]

    response = await async_client.post(
        f"/admin/users/{user_id}/activate",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["is_active"]


@pytest.mark.asyncio
async def test_admin_cannot_deactivate_self(
    async_client: AsyncClient, admin_token: str
):
    """Тест что админ не может деактивировать себя"""
    me_response = await async_client.get(
        "/users/me", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert me_response.status_code == 200
    admin_id = me_response.json()["id"]

    response = await async_client.post(
        f"/admin/users/{admin_id}/deactivate",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_admin_cannot_ban_self(async_client: AsyncClient, admin_token: str):
    """Тест что админ не может забанить себя"""
    me_response = await async_client.get(
        "/users/me", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert me_response.status_code == 200
    admin_id = me_response.json()["id"]

    ban_self_data = {"ban_reason": "Test self ban"}
    ban_self_response = await async_client.post(
        f"/admin/users/{admin_id}/ban",
        json=ban_self_data,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert ban_self_response.status_code == 400


@pytest.mark.asyncio
async def test_deactivate_nonexistent_user(async_client: AsyncClient, admin_token: str):
    """Тест деактивации несуществующего пользователя"""
    response = await async_client.post(
        "/admin/users/99999/deactivate",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_ban_nonexistent_user(async_client: AsyncClient, admin_token: str):
    """Тест бана несуществующего пользователя"""
    response = await async_client.post(
        "/admin/users/999999/ban",
        json={"ban_reason": "Test"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_regular_user_cannot_access_admin_endpoints(
    async_client: AsyncClient, regular_token: str
):
    """Тест что обычный пользователь не может использовать админские эндпоинты"""
    endpoints = [
        "/users/",
        "/users/1",
        "/admin/users/1/deactivate",
        "/admin/users/1/activate",
    ]

    for endpoint in endpoints:
        if "deactivate" in endpoint or "activate" in endpoint:
            method = async_client.post
        else:
            method = async_client.get

        response = await method(
            endpoint, headers={"Authorization": f"Bearer {regular_token}"}
        )
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_unauthenticated_access_to_admin_endpoints(async_client: AsyncClient):
    """
    Тест что неавторизованные пользователи не могут использовать админские эндпоинты
    """
    endpoints = [
        "/users/",
        "/users/1",
        "/admin/users/1/deactivate",
        "/admin/users/1/activate",
    ]

    for endpoint in endpoints:
        if "deactivate" in endpoint or "activate" in endpoint:
            method = async_client.post
        else:
            method = async_client.get

        response = await method(endpoint)
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_ban_and_unban_user_flow(async_client: AsyncClient, admin_token: str):
    """
    Тест полного цикла: создание пользователя -> бан -> проверка -> разбан -> проверка
    """
    # 1. Создание пользователя
    user_data = {
        "username": "user_to_ban",
        "email": "user_to_ban@example.com",
        "password": "password",
    }
    create_response = await async_client.post("/users/", json=user_data)
    assert create_response.status_code == 200
    user_id = create_response.json()["id"]

    # 2. Бан пользователя
    ban_data = {"ban_reason": "Violation of community guidelines"}
    ban_response = await async_client.post(
        f"/admin/users/{user_id}/ban",
        json=ban_data,
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert ban_response.status_code == 200
    banned_user = ban_response.json()

    # 3. Проверка что пользователь забанен
    assert banned_user["is_banned"]
    assert banned_user["ban_reason"] == "Violation of community guidelines"
    assert banned_user["banned_at"] is not None

    # 4. Проверка что забаненный пользователь есть в списке забаненных
    banned_list_response = await async_client.get(
        "/admin/users/banned", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert banned_list_response.status_code == 200

    banned_users = banned_list_response.json()
    banned_user_ids = [user["id"] for user in banned_users]
    assert user_id in banned_user_ids

    # 5. Разбан пользователя
    unban_response = await async_client.post(
        f"/admin/users/{user_id}/unban",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert unban_response.status_code == 200
    unbanned_user = unban_response.json()

    # 6. Проверка что пользователь разбанен
    assert not unbanned_user["is_banned"]
    assert unbanned_user["ban_reason"] is None
    assert unbanned_user["banned_at"] is None

    # 7. Проверка что пользователя нет в списке забаненных
    banned_list_after_response = await async_client.get(
        "/admin/users/banned", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert banned_list_after_response.status_code == 200

    banned_users_after = banned_list_after_response.json()
    banned_user_ids_after = [user["id"] for user in banned_users_after]
    assert user_id not in banned_user_ids_after
