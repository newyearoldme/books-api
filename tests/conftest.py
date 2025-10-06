import asyncio
import time

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.main import app
from src.shared.database import Base, get_db
from src.users.crud import user as user_crud
from src.users.schemas import UserCreate

# Тестовая in-memory БД
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="session")
async def event_loop():
    """Event loop для тестов"""
    try:
        policy = asyncio.get_event_loop_policy()
    except RuntimeError:
        loop = policy.new_event_loop()
        asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Двигатель тестовой БД"""
    engine = create_async_engine(
        TEST_DATABASE_URL, connect_args={"check_same_thread": False}
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine):
    """Тестовая сессия"""
    async with async_sessionmaker(
        bind=test_engine, expire_on_commit=False
    )() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def async_client(test_engine):
    """Асинхронный клиент для тестов с переопределенной БД"""
    TestingSessionLocal = async_sessionmaker(
        bind=test_engine, expire_on_commit=False, autoflush=False
    )

    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(autouse=True)
async def clean_tables(test_engine):
    """Автоочистка таблиц перед каждым тестом"""
    async with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())
    yield


@pytest_asyncio.fixture()
async def unique_timestamp():
    """Генерация уникального timestamp"""
    return int(time.time() * 1000)


@pytest_asyncio.fixture()
async def regular_user(async_client, unique_timestamp):
    """Фикстура тестового пользователя"""
    user_data = {
        "username": f"testuser_{unique_timestamp}",
        "email": f"test_{unique_timestamp}@example.com",
        "password": "password",
    }
    response = await async_client.post("/users/", json=user_data)
    return response.json()


@pytest_asyncio.fixture()
async def regular_token(async_client, regular_user):
    """Фикстура аутентификации тестового пользователя"""
    login_data = {"username": regular_user["username"], "password": "password"}
    response = await async_client.post("/auth/login", json=login_data)
    return response.json()["access_token"]


@pytest_asyncio.fixture()
async def admin_user(test_session, unique_timestamp):
    """Фикстура тестового админа"""
    user_data = UserCreate(
        username=f"admin_{unique_timestamp}",
        email=f"admin_{unique_timestamp}@example.com",
        password="adminpassword",
    )

    admin = await user_crud.create(test_session, user_data)
    admin.is_admin = True
    await test_session.commit()
    await test_session.refresh(admin)
    return admin


@pytest_asyncio.fixture()
async def admin_token(async_client, admin_user):
    """Фикстура аутентификации тестового админа"""
    login_data = {"username": admin_user.username, "password": "adminpassword"}
    response = await async_client.post("/auth/login", json=login_data)
    return response.json()["access_token"]


@pytest_asyncio.fixture()
async def test_book(async_client, admin_token, unique_timestamp):
    """Фикстура создания тестовой книги"""
    book_data = {
        "title": f"Test book {unique_timestamp}",
        "author": "Test author",
        "pages": 100,
    }
    response = await async_client.post(
        "/books/", json=book_data, headers={"Authorization": f"Bearer {admin_token}"}
    )
    return response.json()
