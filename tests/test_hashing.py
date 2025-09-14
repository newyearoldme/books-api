import pytest
from httpx import ASGITransport, AsyncClient
from src.main import app

@pytest.mark.asyncio
async def test_password_hashing():
    """Тест что пароли хешируются правильно"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        user_data = {
            "username": "securityuser",
            "email": "security@example.com",
            "password": "mysecretpassword"
        }
        response = await ac.post("/users/", json=user_data)
        
        assert "password" not in response.json()
        assert "password_hash" not in response.json()
        
        auth_response = await ac.post("/auth/login", json={
            "username": "securityuser",
            "password": "mysecretpassword"
        })
        assert auth_response.status_code == 200
