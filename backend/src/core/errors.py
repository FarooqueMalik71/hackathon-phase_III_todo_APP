"""
Custom error classes and error handling for AI chatbot
"""
from fastapi import HTTPException, status
from typing import Any, Dict, Optional


class ChatbotError(Exception):
    """Base exception for chatbot errors"""

    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AIServiceError(ChatbotError):
    """AI service communication error"""

    def __init__(self, message: str = "AI service error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_503_SERVICE_UNAVAILABLE, details)


class InvalidMessageError(ChatbotError):
    """Invalid message format or content"""

    def __init__(self, message: str = "Invalid message", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, details)


class ConversationNotFoundError(ChatbotError):
    """Conversation not found"""

    def __init__(self, conversation_id: int):
        super().__init__(
            f"Conversation {conversation_id} not found",
            status.HTTP_404_NOT_FOUND,
            {"conversation_id": conversation_id}
        )


class ToolExecutionError(ChatbotError):
    """MCP tool execution error"""

    def __init__(self, tool_name: str, message: str, details: Optional[Dict[str, Any]] = None):
        error_details = {"tool_name": tool_name}
        if details:
            error_details.update(details)
        super().__init__(
            f"Tool execution failed: {tool_name} - {message}",
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_details
        )


class RateLimitExceededError(ChatbotError):
    """Rate limit exceeded"""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status.HTTP_429_TOO_MANY_REQUESTS)


class AuthenticationError(ChatbotError):
    """Authentication error"""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class AuthorizationError(ChatbotError):
    """Authorization error"""

    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


def chatbot_exception_to_http(error: ChatbotError) -> HTTPException:
    """Convert chatbot exception to FastAPI HTTPException"""
    return HTTPException(
        status_code=error.status_code,
        detail={
            "message": error.message,
            "details": error.details
        }
    )
