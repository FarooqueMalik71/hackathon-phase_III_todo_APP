"""
Conversation API endpoints for AI chatbot
Handles conversation history and retrieval.
User identity comes from JWT auth token, not URL path.
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

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../"))
from api.deps import get_current_user


router = APIRouter(prefix="/api", tags=["conversations"])


# Response Models
class MessageResponse(BaseModel):
    """Message response model"""
    id: int
    conversation_id: int
    role: str
    content: str
    created_at: datetime


class ConversationResponse(BaseModel):
    """Conversation response model"""
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0


# Auth-protected endpoints — user_id from JWT

@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    current_user: dict = Depends(get_current_user),
    limit: int = 50,
    session: Session = Depends(get_session),
):
    """List all conversations for the authenticated user"""
    user_id = current_user["user_id"]
    try:
        chat_service = ChatService(session)
        conversations = chat_service.get_user_conversations(user_id, limit)

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


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: int,
    current_user: dict = Depends(get_current_user),
    limit: int = 100,
    session: Session = Depends(get_session),
):
    """Get all messages for a conversation (authenticated user only)"""
    user_id = current_user["user_id"]
    try:
        chat_service = ChatService(session)
        conversation = chat_service.get_conversation(conversation_id, user_id)

        messages = chat_service.get_conversation_messages(conversation_id, limit)
        return [
            MessageResponse(
                id=msg.id,
                conversation_id=msg.conversation_id,
                role=msg.role,
                content=msg.content,
                created_at=msg.created_at
            )
            for msg in messages
        ]

    except ChatbotError as e:
        raise chatbot_exception_to_http(e)
    except Exception as e:
        chat_logger.log_error("get_messages_error", str(e), {
            "user_id": user_id, "conversation_id": conversation_id
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: int,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Delete a conversation and all its messages (authenticated user only)"""
    user_id = current_user["user_id"]
    try:
        chat_service = ChatService(session)
        chat_service.delete_conversation(conversation_id, user_id)
        chat_logger.log_chat_request(user_id, conversation_id, "Conversation deleted")
        return None

    except ChatbotError as e:
        raise chatbot_exception_to_http(e)
    except Exception as e:
        chat_logger.log_error("delete_conversation_error", str(e), {
            "user_id": user_id, "conversation_id": conversation_id
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


# Legacy routes for backwards compatibility (user_id in URL)

@router.get("/{user_id}/conversations", response_model=List[ConversationResponse])
async def list_conversations_legacy(
    user_id: str,
    limit: int = 50,
    session: Session = Depends(get_session),
):
    """Legacy: List conversations with user_id in URL"""
    try:
        chat_service = ChatService(session)
        conversations = chat_service.get_user_conversations(user_id, limit)
        response = []
        for conv in conversations:
            messages = chat_service.get_conversation_messages(conv.id, limit=1000)
            response.append(
                ConversationResponse(
                    id=conv.id, user_id=conv.user_id, created_at=conv.created_at,
                    updated_at=conv.updated_at, message_count=len(messages)
                )
            )
        return response
    except ChatbotError as e:
        raise chatbot_exception_to_http(e)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages_legacy(
    user_id: str, conversation_id: int, limit: int = 100,
    session: Session = Depends(get_session),
):
    """Legacy: Get messages with user_id in URL"""
    try:
        chat_service = ChatService(session)
        chat_service.get_conversation(conversation_id, user_id)
        messages = chat_service.get_conversation_messages(conversation_id, limit)
        return [
            MessageResponse(id=m.id, conversation_id=m.conversation_id, role=m.role, content=m.content, created_at=m.created_at)
            for m in messages
        ]
    except ChatbotError as e:
        raise chatbot_exception_to_http(e)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation_legacy(
    user_id: str, conversation_id: int,
    session: Session = Depends(get_session),
):
    """Legacy: Delete conversation with user_id in URL"""
    try:
        chat_service = ChatService(session)
        chat_service.delete_conversation(conversation_id, user_id)
        return None
    except ChatbotError as e:
        raise chatbot_exception_to_http(e)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
