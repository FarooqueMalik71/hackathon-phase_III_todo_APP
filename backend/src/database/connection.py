"""
Database connection pool configuration
Provides database session management
"""
from sqlmodel import create_engine, Session
from typing import Generator
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/hackathon_todo")

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL logging in development
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=10,  # Maximum number of connections in the pool
    max_overflow=20,  # Maximum overflow connections beyond pool_size
    pool_recycle=3600,  # Recycle connections after 1 hour
)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency for getting database session
    Used with FastAPI's Depends()
    """
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()


def get_db_session() -> Session:
    """
    Get a new database session
    Use this for standalone operations outside FastAPI
    """
    return Session(engine)
