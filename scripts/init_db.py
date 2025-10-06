import asyncio
import sys
from pathlib import Path

current_dir = Path(__file__).parent
root_dir = current_dir.parent
sys.path.append(str(root_dir))

from src.shared.database import Base, engine


async def init_db():
    print("🔄 Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    print("✅ Database tables created successfully!")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_db())
