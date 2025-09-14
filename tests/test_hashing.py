import pytest

@pytest.mark.asyncio
async def test_password_hashing(async_client):
    """Тест что пароли хешируются правильно"""
    user_data = {
        "username": "securityuser",
        "email": "security@example.com",
        "password": "mysecretpassword"
    }
    response = await async_client.post("/users/", json=user_data)
    
    assert "password" not in response.json()
    assert "password_hash" not in response.json()
    
    auth_response = await async_client.post("/auth/login", json={
        "username": "securityuser",
        "password": "mysecretpassword"
    })
    assert auth_response.status_code == 200
