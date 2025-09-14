#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path

current_dir = Path(__file__).parent
root_dir = current_dir.parent
sys.path.append(str(root_dir))

from src.shared.database import engine
from sqlalchemy import text

async def check_tables():
    async with engine.connect() as conn:
        # Проверьте таблицы в public схеме
        result = await conn.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        )
        tables = result.scalars().all()
        print("📋 Tables in public schema:", tables)
        
        # Попробуйте выбрать из users
        try:
            result = await conn.execute(text("SELECT * FROM public.users LIMIT 1"))
            users = result.fetchall()
            print("✅ Users table exists with data:", users)
        except Exception as e:
            print("❌ Error accessing users table:", e)

if __name__ == "__main__":
    asyncio.run(check_tables())
