"""
Chat API endpoints for AI chatbot
Handles chat requests and conversation management.
User identity comes from JWT auth token, not URL path.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from sqlmodel import Session

from ...database import get_session
from ...services.chat_service import ChatService
from ...services.ai_agent_service import AIAgentService
from ...core.errors import chatbot_exception_to_http, ChatbotError, InvalidMessageError
from ...core.logging import chat_logger

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../"))
from db.session import get_async_session
from api.deps import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
import time


router = APIRouter(prefix="/api", tags=["chat"])


# Request/Response Models
class ChatRequest(BaseModel):
    """Chat request model"""
    conversation_id: Optional[int] = Field(None, description="Conversation ID (null for new conversation)")
    message: str = Field(..., min_length=1, max_length=2000, description="User message")

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": None,
                "message": "Add a task to buy groceries tomorrow"
            }
        }


class ToolCall(BaseModel):
    """Tool call model"""
    tool: str
    arguments: Dict[str, Any]
    result: Dict[str, Any]


class ChatResponse(BaseModel):
    """Chat response model"""
    conversation_id: int
    response: str
    tool_calls: List[ToolCall] = []
    response_time: float


# Auth-protected chat endpoint — user_id from JWT, not URL
@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
    async_session: AsyncSession = Depends(get_async_session),
):
    """
    Process a chat message and return AI response.
    User identity is extracted from the JWT auth token.
    """
    user_id = current_user["user_id"]
    start_time = time.time()

    try:
        # Validate message
        if not request.message or len(request.message.strip()) == 0:
            raise InvalidMessageError("Message cannot be empty")

        # Initialize services
        chat_service = ChatService(session)
        ai_service = AIAgentService()

        # Get or create conversation
        if request.conversation_id:
            conversation = chat_service.get_conversation(request.conversation_id, user_id)
        else:
            conversation = chat_service.create_conversation(user_id)

        # Log request
        chat_logger.log_chat_request(user_id, conversation.id, request.message)

        # Save user message
        chat_service.add_message(conversation.id, "user", request.message)

        # Get conversation history
        history = chat_service.get_conversation_history(conversation.id, limit=20)

        # Process message with AI — pass async_session for tool execution
        ai_result = await ai_service.process_message(
            request.message,
            history,
            user_id,
            db_session=async_session,
        )

        # Save assistant response
        if ai_result["response"]:
            chat_service.add_message(conversation.id, "assistant", ai_result["response"])

        # Log response
        chat_logger.log_ai_response(
            user_id, conversation.id, ai_result["response"], ai_result["response_time"]
        )

        return ChatResponse(
            conversation_id=conversation.id,
            response=ai_result["response"],
            tool_calls=[ToolCall(**call) for call in ai_result["tool_calls"]],
            response_time=time.time() - start_time,
        )

    except ChatbotError as e:
        raise chatbot_exception_to_http(e)
    except Exception as e:
        chat_logger.log_error("chat_endpoint_error", str(e), {"user_id": user_id})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


# Backwards-compatible route for existing frontend (until frontend is updated)
@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat_legacy(
    user_id: str,
    request: ChatRequest,
    session: Session = Depends(get_session),
    async_session: AsyncSession = Depends(get_async_session),
):
    """
    Legacy chat endpoint with user_id in URL path.
    Kept for backwards compatibility during frontend migration.
    """
    start_time = time.time()

    try:
        if not request.message or len(request.message.strip()) == 0:
            raise InvalidMessageError("Message cannot be empty")

        chat_service = ChatService(session)
        ai_service = AIAgentService()

        if request.conversation_id:
            conversation = chat_service.get_conversation(request.conversation_id, user_id)
        else:
            conversation = chat_service.create_conversation(user_id)

        chat_logger.log_chat_request(user_id, conversation.id, request.message)
        chat_service.add_message(conversation.id, "user", request.message)
        history = chat_service.get_conversation_history(conversation.id, limit=20)

        ai_result = await ai_service.process_message(
            request.message, history, user_id, db_session=async_session
        )

        if ai_result["response"]:
            chat_service.add_message(conversation.id, "assistant", ai_result["response"])

        chat_logger.log_ai_response(
            user_id, conversation.id, ai_result["response"], ai_result["response_time"]
        )

        return ChatResponse(
            conversation_id=conversation.id,
            response=ai_result["response"],
            tool_calls=[ToolCall(**call) for call in ai_result["tool_calls"]],
            response_time=time.time() - start_time,
        )

    except ChatbotError as e:
        raise chatbot_exception_to_http(e)
    except Exception as e:
        chat_logger.log_error("chat_endpoint_error", str(e), {"user_id": user_id})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
