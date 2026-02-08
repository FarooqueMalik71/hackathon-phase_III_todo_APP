"""
Core package for AI chatbot
Exports logging and error handling utilities
"""
from .logging import chat_logger, ChatLogger
from .errors import (
    ChatbotError,
    AIServiceError,
    InvalidMessageError,
    ConversationNotFoundError,
    ToolExecutionError,
    RateLimitExceededError,
    AuthenticationError,
    AuthorizationError,
    chatbot_exception_to_http
)

__all__ = [
    "chat_logger",
    "ChatLogger",
    "ChatbotError",
    "AIServiceError",
    "InvalidMessageError",
    "ConversationNotFoundError",
    "ToolExecutionError",
    "RateLimitExceededError",
    "AuthenticationError",
    "AuthorizationError",
    "chatbot_exception_to_http"
]
