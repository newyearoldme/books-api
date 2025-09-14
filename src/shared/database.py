from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from src.shared.config import settings


class Base(DeclarativeBase):
    pass

if settings.DB_TYPE == "sqlite":
    engine = create_async_engine(
        settings.DB_URL,
        connect_args={"check_same_thread": False},
        echo=True
    )
else:
    engine = create_async_engine(
        settings.DB_URL,
        pool_size=20,
        max_overflow=10,
    )

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
