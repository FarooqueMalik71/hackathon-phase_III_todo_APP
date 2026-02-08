"""
Conversation model for AI chatbot
Represents a single chat session with metadata
"""
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List


class Conversation(SQLModel, table=True):
    """Conversation entity - represents a chat session"""

    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship to messages
    messages: List["Message"] = Relationship(back_populates="conversation")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "user123",
                "created_at": "2026-02-08T10:00:00Z",
                "updated_at": "2026-02-08T10:30:00Z"
            }
        }


# Import Message to resolve forward reference
from .message import Message

Conversation.model_rebuild()
