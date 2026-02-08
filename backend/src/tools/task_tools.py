"""
MCP Task Tools for AI chatbot
Provides task management tools for the AI agent
"""
from typing import Dict, Any, Optional
from .mcp_server import MCPTool, ToolCategory, mcp_server
from ..services.task_integration_service import TaskIntegrationService


# Initialize task integration service
task_service = TaskIntegrationService()


# Tool Handlers
async def add_task_handler(
    user_id: str,
    title: str,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None
) -> Dict[str, Any]:
    """Handler for add_task tool"""
    return task_service.add_task(user_id, title, description, priority, due_date)


async def complete_task_handler(user_id: str, task_id: str) -> Dict[str, Any]:
    """Handler for complete_task tool"""
    return task_service.complete_task(user_id, task_id)


async def list_tasks_handler(
    user_id: str,
    completed: Optional[bool] = None,
    limit: int = 20
) -> Dict[str, Any]:
    """Handler for list_tasks tool"""
    return task_service.list_tasks(user_id, completed, limit)


async def update_task_handler(
    user_id: str,
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None
) -> Dict[str, Any]:
    """Handler for update_task tool"""
    return task_service.update_task(user_id, task_id, title, description, priority, due_date)


async def delete_task_handler(user_id: str, task_id: str) -> Dict[str, Any]:
    """Handler for delete_task tool"""
    return task_service.delete_task(user_id, task_id)


# Tool Definitions
add_task_tool = MCPTool(
    name="add_task",
    description="Add a new todo task for the user. Use this when the user wants to create or add a task.",
    parameters={
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "The title or name of the task (required)"
            },
            "description": {
                "type": "string",
                "description": "Detailed description of the task (optional)"
            },
            "priority": {
                "type": "string",
                "enum": ["low", "medium", "high"],
                "description": "Priority level of the task (optional, default: medium)"
            },
            "due_date": {
                "type": "string",
                "description": "Due date in ISO format, e.g., '2026-02-10T10:00:00Z' (optional)"
            }
        },
        "required": ["title"]
    },
    category=ToolCategory.TASK_MANAGEMENT,
    handler=add_task_handler
)

complete_task_tool = MCPTool(
    name="complete_task",
    description="Mark a task as completed. Use this when the user wants to complete or mark a task as done.",
    parameters={
        "type": "object",
        "properties": {
            "task_id": {
                "type": "string",
                "description": "The ID of the task to complete (required)"
            }
        },
        "required": ["task_id"]
    },
    category=ToolCategory.TASK_MANAGEMENT,
    handler=complete_task_handler
)

list_tasks_tool = MCPTool(
    name="list_tasks",
    description="List all tasks for the user. Use this when the user wants to see their tasks or check what tasks they have.",
    parameters={
        "type": "object",
        "properties": {
            "completed": {
                "type": "boolean",
                "description": "Filter by completion status: true for completed tasks, false for incomplete tasks, null for all (optional)"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of tasks to return (optional, default: 20)"
            }
        },
        "required": []
    },
    category=ToolCategory.TASK_MANAGEMENT,
    handler=list_tasks_handler
)

update_task_tool = MCPTool(
    name="update_task",
    description="Update an existing task. Use this when the user wants to modify or change task details.",
    parameters={
        "type": "object",
        "properties": {
            "task_id": {
                "type": "string",
                "description": "The ID of the task to update (required)"
            },
            "title": {
                "type": "string",
                "description": "New title for the task (optional)"
            },
            "description": {
                "type": "string",
                "description": "New description for the task (optional)"
            },
            "priority": {
                "type": "string",
                "enum": ["low", "medium", "high"],
                "description": "New priority level (optional)"
            },
            "due_date": {
                "type": "string",
                "description": "New due date in ISO format (optional)"
            }
        },
        "required": ["task_id"]
    },
    category=ToolCategory.TASK_MANAGEMENT,
    handler=update_task_handler
)

delete_task_tool = MCPTool(
    name="delete_task",
    description="Delete a task permanently. Use this when the user wants to remove or delete a task.",
    parameters={
        "type": "object",
        "properties": {
            "task_id": {
                "type": "string",
                "description": "The ID of the task to delete (required)"
            }
        },
        "required": ["task_id"]
    },
    category=ToolCategory.TASK_MANAGEMENT,
    handler=delete_task_handler
)


# Register all tools with the MCP server
def register_task_tools():
    """Register all task management tools with the MCP server"""
    mcp_server.register_tool(add_task_tool)
    mcp_server.register_tool(complete_task_tool)
    mcp_server.register_tool(list_tasks_tool)
    mcp_server.register_tool(update_task_tool)
    mcp_server.register_tool(delete_task_tool)


# Auto-register tools when module is imported
register_task_tools()
