"""
Database migrations for AI chatbot feature
Creates Conversation and Message tables
"""
from sqlmodel import SQLModel, create_engine, Session
from ..models.conversation import Conversation
from ..models.message import Message
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/hackathon_todo")


def create_tables():
    """Create all database tables"""
    engine = create_engine(DATABASE_URL, echo=True)
    SQLModel.metadata.create_all(engine)
    print("✅ Database tables created successfully!")


def drop_tables():
    """Drop all database tables (use with caution!)"""
    engine = create_engine(DATABASE_URL, echo=True)
    SQLModel.metadata.drop_all(engine)
    print("⚠️  Database tables dropped!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "drop":
        drop_tables()
    else:
        create_tables()
