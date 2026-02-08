"""
Chat Service for AI chatbot
Handles conversation flow and history management
"""
from typing import List, Optional, Tuple
from sqlmodel import Session, select
from datetime import datetime

from ..models.conversation import Conversation
from ..models.message import Message, MessageRole
from ..core.errors import ConversationNotFoundError
from ..core.logging import chat_logger


class ChatService:
    """Service for managing chat conversations and messages"""

    def __init__(self, session: Session):
        self.session = session

    def create_conversation(self, user_id: str) -> Conversation:
        """Create a new conversation for a user"""
        conversation = Conversation(
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)

        chat_logger.log_chat_request(user_id, conversation.id, "New conversation created")
        return conversation

    def get_conversation(self, conversation_id: int, user_id: str) -> Conversation:
        """Get a conversation by ID, ensuring it belongs to the user"""
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        conversation = self.session.exec(statement).first()

        if not conversation:
            raise ConversationNotFoundError(conversation_id)

        return conversation

    def get_user_conversations(self, user_id: str, limit: int = 50) -> List[Conversation]:
        """Get all conversations for a user"""
        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
        )
        conversations = self.session.exec(statement).all()
        return list(conversations)

    def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str
    ) -> Message:
        """Add a message to a conversation"""
        # Validate role
        if role not in [MessageRole.USER.value, MessageRole.ASSISTANT.value]:
            raise ValueError(f"Invalid role: {role}")

        # Validate content length
        if len(content) > 2000:
            raise ValueError("Message content exceeds maximum length of 2000 characters")

        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            created_at=datetime.utcnow()
        )
        self.session.add(message)

        # Update conversation timestamp
        conversation = self.session.get(Conversation, conversation_id)
        if conversation:
            conversation.updated_at = datetime.utcnow()
            self.session.add(conversation)

        self.session.commit()
        self.session.refresh(message)

        return message

    def get_conversation_messages(
        self,
        conversation_id: int,
        limit: int = 100
    ) -> List[Message]:
        """Get all messages for a conversation"""
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
        )
        messages = self.session.exec(statement).all()
        return list(messages)

    def get_conversation_history(
        self,
        conversation_id: int,
        limit: int = 20
    ) -> List[dict]:
        """
        Get conversation history in OpenAI format
        Returns list of {role, content} dicts
        """
        messages = self.get_conversation_messages(conversation_id, limit)
        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

    def delete_conversation(self, conversation_id: int, user_id: str) -> bool:
        """Delete a conversation and all its messages"""
        conversation = self.get_conversation(conversation_id, user_id)

        # Delete all messages first
        statement = select(Message).where(Message.conversation_id == conversation_id)
        messages = self.session.exec(statement).all()
        for message in messages:
            self.session.delete(message)

        # Delete conversation
        self.session.delete(conversation)
        self.session.commit()

        return True
