#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path

# Добавляем корень в PYTHONPATH
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from src.shared.database import engine
from sqlalchemy import text

async def check_db():
    print("🔍 Checking database connection and tables...")
    
    try:
        async with engine.connect() as conn:
            # Проверяем подключение
            print("✅ Connected to database successfully!")
            
            # Проверяем таблицы в public схеме
            result = await conn.execute(
                text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            )
            tables = result.scalars().all()
            print(f"📋 Tables in public schema: {tables}")
            
            # Если есть users - пробуем выбрать данные
            if 'users' in tables:
                result = await conn.execute(text("SELECT COUNT(*) FROM public.users"))
                count = result.scalar()
                print(f"👥 Users table has {count} records")
            else:
                print("❌ Users table not found")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_db())
