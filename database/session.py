"""
ReconIQ Enterprise — Database Session
"""
from typing import AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from apps.api.config import get_settings

settings = get_settings()

# Ensure URL is configured for asyncpg
async_db_url = settings.database_url
if async_db_url.startswith("postgres://"):
    async_db_url = async_db_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif async_db_url.startswith("postgresql://"):
    async_db_url = async_db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# Async Engine
engine = create_async_engine(
    async_db_url,
    echo=False,
    future=True,
    pool_size=20,
    max_overflow=10,
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database sessions."""
    async with AsyncSessionLocal() as session:
        yield session

# Sync Engine (for Alembic or blocking scripts)
sync_db_url = settings.database_url.replace("+asyncpg", "").replace("+aiosqlite", "")
if sync_db_url.startswith("postgres://"):
    sync_db_url = sync_db_url.replace("postgres://", "postgresql://", 1)

sync_engine = create_engine(sync_db_url, echo=False)
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
