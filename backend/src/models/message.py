"""
Message model for AI chatbot
Individual chat message within a conversation
"""
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, Literal
from enum import Enum


class MessageRole(str, Enum):
    """Message role enumeration"""
    USER = "user"
    ASSISTANT = "assistant"


class Message(SQLModel, table=True):
    """Message entity - represents a single chat message"""

    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", nullable=False, index=True)
    role: str = Field(nullable=False)
    content: str = Field(max_length=2000, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship to conversation
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "conversation_id": 1,
                "role": "user",
                "content": "Add a task to buy groceries",
                "created_at": "2026-02-08T10:00:00Z"
            }
        }


# Import Conversation to resolve forward reference
from .conversation import Conversation

Message.model_rebuild()
