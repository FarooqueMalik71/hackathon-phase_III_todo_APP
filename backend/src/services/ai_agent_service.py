"""
AI Agent Service for AI chatbot
Handles natural language processing and AI agent integration via OpenRouter.
Passes async db session and user_id through to MCP tool execution.
"""
from typing import List, Dict, Any, Optional
import openai
import json
import time

from ..config.openrouter import get_openrouter_config
from ..core.errors import AIServiceError
from ..core.logging import chat_logger
from ..tools.mcp_server import get_mcp_server


class AIAgentService:
    """Service for AI agent interaction and tool selection"""

    def __init__(self):
        config = get_openrouter_config()
        self.client = openai.OpenAI(
            base_url=config.base_url,
            api_key=config.api_key,
        )
        self.model = config.model
        self.max_tokens = config.max_tokens
        self.temperature = config.temperature
        self.timeout = config.timeout
        self.mcp_server = get_mcp_server()

    def get_system_prompt(self) -> str:
        """Get the system prompt for the AI agent"""
        return """You are a helpful AI assistant for a todo list application.
You help users manage their tasks through natural language commands.

You can:
- Add new tasks
- Complete tasks
- List tasks
- Update task details
- Delete tasks
- Support both English and Roman Urdu inputs

When users ask you to do something with their tasks, use the available tools to execute the operations.
Be conversational, friendly, and helpful. Confirm actions and provide clear feedback."""

    async def process_message(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        user_id: str,
        db_session=None,
    ) -> Dict[str, Any]:
        """
        Process user message and generate AI response.

        Args:
            user_message: The user's message
            conversation_history: Previous conversation messages
            user_id: The user ID for tool execution context
            db_session: Async database session for tool operations

        Returns:
            Dictionary with response and tool calls
        """
        start_time = time.time()

        try:
            # Build messages for the AI
            messages = [
                {"role": "system", "content": self.get_system_prompt()}
            ]
            messages.extend(conversation_history)
            messages.append({"role": "user", "content": user_message})

            # Get available tools
            tools = self.mcp_server.get_all_tools()

            # Call OpenRouter API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools if tools else None,
                tool_choice="auto" if tools else None,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout
            )

            # Extract response
            message = response.choices[0].message
            response_text = message.content or ""
            tool_calls = []

            # Handle tool calls if present
            if message.tool_calls:
                # Add the assistant's tool-calling message to conversation
                messages.append(message.model_dump())

                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    # Execute tool with session and user_id (NOT passed as tool_args)
                    tool_result = await self.mcp_server.execute_tool(
                        tool_name,
                        session=db_session,
                        user_id=user_id,
                        **tool_args,
                    )

                    tool_calls.append({
                        "tool": tool_name,
                        "arguments": tool_args,
                        "result": tool_result
                    })

                    # Add tool result to conversation for follow-up
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(tool_result)
                    })

                    # Log tool execution
                    chat_logger.log_tool_execution(
                        tool_name,
                        user_id,
                        tool_result.get("success", False),
                        tool_result
                    )

                # Follow-up call to get user-friendly response after tool execution
                followup_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    timeout=self.timeout
                )
                response_text = followup_response.choices[0].message.content or ""

            # Calculate response time
            response_time = time.time() - start_time

            # Log performance
            chat_logger.log_performance(
                "ai_message_processing",
                response_time,
                {"user_id": user_id, "tool_calls": len(tool_calls)}
            )

            return {
                "response": response_text,
                "tool_calls": tool_calls,
                "response_time": response_time
            }

        except openai.APIError as e:
            chat_logger.log_error("openai_api_error", str(e), {"user_id": user_id})
            raise AIServiceError(f"AI service error: {str(e)}")
        except Exception as e:
            chat_logger.log_error("ai_agent_error", str(e), {"user_id": user_id})
            raise AIServiceError(f"Unexpected error: {str(e)}")

    def detect_language(self, text: str) -> str:
        """Detect if the input is English or Roman Urdu"""
        urdu_keywords = ["karo", "karna", "hai", "ka", "ko", "ke", "se", "mein", "aur"]
        text_lower = text.lower()
        urdu_count = sum(1 for word in urdu_keywords if word in text_lower)
        return "urdu" if urdu_count > 0 else "english"
