from sqlmodel import create_engine
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from core.config import settings

# Create engines based on database type
database_url = settings.DATABASE_URL

# Determine if we're using PostgreSQL or SQLite
is_postgres = database_url.startswith('postgresql://') or database_url.startswith('postgres://')

if is_postgres:
    # For PostgreSQL, use async driver
    if '+asyncpg' not in database_url:
        if database_url.startswith('postgresql://'):
            database_url = database_url.replace('postgresql://', 'postgresql+asyncpg://', 1)
        elif database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql+asyncpg://', 1)

    from sqlalchemy.ext.asyncio import create_async_engine
    async_engine = create_async_engine(
        database_url,
        echo=False,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=300,
    )

    sync_engine = create_engine(
        database_url.replace('+asyncpg', ''),  # Remove asyncpg driver for sync operations
        echo=False,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=300,
    )
else:
    # For SQLite, we need to handle this specially since async engines don't work with SQLite
    # We'll create a sync engine only and use it for both sync and async operations
    from sqlalchemy.pool import StaticPool

    sync_engine = create_engine(
        database_url,
        echo=False,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False}
    )

    # For SQLite, we'll create a separate async engine using the same URL
    # This is the key fix - using the async version of SQLite driver
    from sqlalchemy.ext.asyncio import create_async_engine as async_create_engine
    async_engine = async_create_engine(
        database_url.replace('sqlite:///', 'sqlite+aiosqlite:///'),
        echo=False,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False}
    )

# Create session makers
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    class_=AsyncSession
)

SyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
    expire_on_commit=False
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to provide async database session"""
    async with AsyncSessionLocal() as session:
        yield session


def get_sync_session():
    """Dependency to provide sync database session (for FastAPI Depends)"""
    with SyncSessionLocal() as session:
        yield session


