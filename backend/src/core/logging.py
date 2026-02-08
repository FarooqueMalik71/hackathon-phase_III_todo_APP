"""
Logging configuration for AI chatbot
Provides structured logging for chat interactions
"""
import logging
import sys
from datetime import datetime
from typing import Any, Dict
import json


class ChatLogger:
    """Custom logger for chat interactions"""

    def __init__(self, name: str = "ai_chatbot"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)

        # Add handler to logger
        if not self.logger.handlers:
            self.logger.addHandler(handler)

    def log_chat_request(self, user_id: str, conversation_id: int, message: str):
        """Log incoming chat request"""
        self.logger.info(
            f"CHAT_REQUEST - User: {user_id}, Conversation: {conversation_id}, Message: {message[:100]}..."
        )

    def log_ai_response(self, user_id: str, conversation_id: int, response: str, response_time: float):
        """Log AI response"""
        self.logger.info(
            f"AI_RESPONSE - User: {user_id}, Conversation: {conversation_id}, "
            f"Response Time: {response_time:.2f}s, Response: {response[:100]}..."
        )

    def log_tool_execution(self, tool_name: str, user_id: str, success: bool, details: Dict[str, Any] = None):
        """Log MCP tool execution"""
        status = "SUCCESS" if success else "FAILED"
        details_str = json.dumps(details) if details else "{}"
        self.logger.info(
            f"TOOL_EXECUTION - Tool: {tool_name}, User: {user_id}, Status: {status}, Details: {details_str}"
        )

    def log_error(self, error_type: str, error_message: str, context: Dict[str, Any] = None):
        """Log error with context"""
        context_str = json.dumps(context) if context else "{}"
        self.logger.error(
            f"ERROR - Type: {error_type}, Message: {error_message}, Context: {context_str}"
        )

    def log_performance(self, operation: str, duration: float, metadata: Dict[str, Any] = None):
        """Log performance metrics"""
        metadata_str = json.dumps(metadata) if metadata else "{}"
        self.logger.info(
            f"PERFORMANCE - Operation: {operation}, Duration: {duration:.2f}s, Metadata: {metadata_str}"
        )


# Global logger instance
chat_logger = ChatLogger()
