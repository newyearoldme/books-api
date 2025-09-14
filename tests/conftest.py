import asyncio
import pytest
import time
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker  

from src.main import app
from src.shared.database import Base, get_db

# Тестовая in-memory БД
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    """Event loop для тестов"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def test_engine():
    """Двигатель тестовой БД"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture(scope="function")
async def test_session(test_engine):
    """Тестовая сессия"""
    async with async_sessionmaker(
        bind=test_engine,
        expire_on_commit=False,
        autoflush=False
    )() as session:
        yield session

@pytest.fixture(scope="function")
async def async_client(test_engine):
    """Асинхронный клиент для тестов с переопределенной БД"""
    TestingSessionLocal = async_sessionmaker(
        bind=test_engine,
        expire_on_commit=False,
        autoflush=False
    )
    
    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        yield client
    
    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
async def clean_tables(test_engine):
    """Автоочистка таблиц перед каждым тестом"""
    async with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())
    yield

@pytest.fixture()
def unique_timestamp():
    """Генерация уникального timestamp"""
    return int(time.time() * 1000)

@pytest.fixture()
async def test_user(async_client, unique_timestamp):
    """Фикстура тестового пользователя"""
    user_data = {
        "username": f"testuser_{unique_timestamp}",
        "email": f"test_{unique_timestamp}@example.com",
        "password": "password"
    }
    response = await async_client.post("/users/", json=user_data)
    assert response.status_code == 200
    return response.json()

@pytest.fixture()
async def auth_token(async_client, test_user):
    """Фикстура аутентификации тестового пользователя"""
    login_data = {
        "username": test_user["username"],
        "password": "password"
    }
    response = await async_client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture()
async def test_book(async_client, auth_token, unique_timestamp):
    """Фикстура создания тестовой книги"""
    book_data = {
        "title": f"Test book {unique_timestamp}",
        "author": "Test author",
        "pages": 100
    }
    response = await async_client.post(
        "/books/", 
        json=book_data, 
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    return response.json()
