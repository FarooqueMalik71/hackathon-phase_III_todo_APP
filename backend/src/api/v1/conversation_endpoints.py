"""
Conversation API endpoints for AI chatbot
Handles conversation history and retrieval
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from sqlmodel import Session
from datetime import datetime

from ...database import get_session
from ...services.chat_service import ChatService
from ...core.errors import chatbot_exception_to_http, ChatbotError
from ...core.logging import chat_logger


router = APIRouter(prefix="/api", tags=["conversations"])


# Response Models
class MessageResponse(BaseModel):
    """Message response model"""
    id: int
    conversation_id: int
    role: str
    content: str
    created_at: datetime

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


class ConversationResponse(BaseModel):
    """Conversation response model"""
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "user123",
                "created_at": "2026-02-08T10:00:00Z",
                "updated_at": "2026-02-08T10:30:00Z",
                "message_count": 10
            }
        }


@router.get("/{user_id}/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    user_id: str,
    limit: int = 50,
    session: Session = Depends(get_session)
):
    """
    List all conversations for a user

    Args:
        user_id: User ID from path
        limit: Maximum number of conversations to return
        session: Database session

    Returns:
        List of conversations with metadata
    """
    try:
        # Get conversations
        chat_service = ChatService(session)
        conversations = chat_service.get_user_conversations(user_id, limit)

        # Build response with message counts
        response = []
        for conv in conversations:
            messages = chat_service.get_conversation_messages(conv.id, limit=1000)
            response.append(
                ConversationResponse(
                    id=conv.id,
                    user_id=conv.user_id,
                    created_at=conv.created_at,
                    updated_at=conv.updated_at,
                    message_count=len(messages)
                )
            )

        return response

    except ChatbotError as e:
        raise chatbot_exception_to_http(e)
    except Exception as e:
        chat_logger.log_error("list_conversations_error", str(e), {"user_id": user_id})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


@router.get("/{user_id}/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    user_id: str,
    conversation_id: int,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """
    Get all messages for a conversation

    Args:
        user_id: User ID from path
        conversation_id: Conversation ID from path
        limit: Maximum number of messages to return
        session: Database session

    Returns:
        List of messages in the conversation
    """
    try:
        # Get conversation to verify ownership
        chat_service = ChatService(session)
        conversation = chat_service.get_conversation(conversation_id, user_id)

        # Get messages
        messages = chat_service.get_conversation_messages(conversation_id, limit)

        # Build response
        response = [
            MessageResponse(
                id=msg.id,
                conversation_id=msg.conversation_id,
                role=msg.role,
                content=msg.content,
                created_at=msg.created_at
            )
            for msg in messages
        ]

        return response

    except ChatbotError as e:
        raise chatbot_exception_to_http(e)
    except Exception as e:
        chat_logger.log_error("get_messages_error", str(e), {
            "user_id": user_id,
            "conversation_id": conversation_id
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


@router.delete("/{user_id}/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    user_id: str,
    conversation_id: int,
    session: Session = Depends(get_session)
):
    """
    Delete a conversation and all its messages

    Args:
        user_id: User ID from path
        conversation_id: Conversation ID from path
        session: Database session

    Returns:
        204 No Content on success
    """
    try:
        # Delete conversation
        chat_service = ChatService(session)
        chat_service.delete_conversation(conversation_id, user_id)

        chat_logger.log_chat_request(user_id, conversation_id, "Conversation deleted")

        return None

    except ChatbotError as e:
        raise chatbot_exception_to_http(e)
    except Exception as e:
        chat_logger.log_error("delete_conversation_error", str(e), {
            "user_id": user_id,
            "conversation_id": conversation_id
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
