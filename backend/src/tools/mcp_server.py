"""
MCP Tool Server for AI chatbot
Provides tool definitions and execution framework.
Tool handlers receive (session, user_id, **tool_args).
"""
from typing import Dict, Any, Callable, List
from enum import Enum
import json


class ToolCategory(str, Enum):
    """Tool category enumeration"""
    TASK_MANAGEMENT = "task_management"
    SYSTEM = "system"


class MCPTool:
    """Represents a single MCP tool"""

    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        category: ToolCategory,
        handler: Callable
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.category = category
        self.handler = handler

    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to OpenAI function calling format"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }

    async def execute(self, session, user_id: str, **kwargs) -> Dict[str, Any]:
        """Execute the tool with session, user_id, and given parameters"""
        try:
            result = await self.handler(session=session, user_id=user_id, **kwargs)
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class MCPToolServer:
    """MCP Tool Server - manages and executes tools"""

    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}

    def register_tool(self, tool: MCPTool):
        """Register a tool with the server"""
        self.tools[tool.name] = tool

    def get_tool(self, name: str) -> MCPTool:
        """Get a tool by name"""
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found")
        return self.tools[name]

    def get_all_tools(self) -> List[Dict[str, Any]]:
        """Get all tools in OpenAI function calling format"""
        return [tool.to_dict() for tool in self.tools.values()]

    def get_tools_by_category(self, category: ToolCategory) -> List[MCPTool]:
        """Get tools filtered by category"""
        return [tool for tool in self.tools.values() if tool.category == category]

    async def execute_tool(self, name: str, session, user_id: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool by name with session, user_id, and parameters"""
        tool = self.get_tool(name)
        return await tool.execute(session=session, user_id=user_id, **kwargs)


# Global MCP tool server instance
mcp_server = MCPToolServer()


def get_mcp_server() -> MCPToolServer:
    """Get the global MCP tool server instance"""
    return mcp_server
