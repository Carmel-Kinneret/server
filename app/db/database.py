from pathlib import Path
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from dotenv import load_dotenv
import os

# Load .env from project root (4 levels up from this file)
repo_root = Path(__file__).resolve().parents[4]
load_dotenv(repo_root / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
# Ensure asyncpg driver for PostgreSQL
if DATABASE_URL.startswith("postgresql://") and "+asyncpg" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create the async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
)

# Create an async session maker
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that provides an async database session.
    Automatically closes the session when the request is finished.
    """
    async with AsyncSessionLocal() as session:
        yield session

# Compatibility alias for routers expecting get_async_session
get_async_session = get_db
