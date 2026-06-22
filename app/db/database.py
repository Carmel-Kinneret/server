from pathlib import Path
import os
from dotenv import load_dotenv
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Load environment variables from the project's .env (located at server/.env)
repo_root = Path(__file__).resolve().parents[2]
load_dotenv(repo_root / ".env")

# Retrieve DATABASE_URL from env
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set in environment variables")

# Ensure asyncpg driver for PostgreSQL URLs
if DATABASE_URL.startswith("postgresql://") and "+asyncpg" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create the async SQLAlchemy engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # set to True for query logging
    future=True,
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async DB session and ensures cleanup."""
    async with AsyncSessionLocal() as session:
        yield session

# Compatibility alias (some modules may import get_db)
get_db = get_async_session
