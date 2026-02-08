# MCP Tool Specifications: AI-Powered Todo Chatbot

## Overview
MCP (Model Context Protocol) tools for AI agent to interact with the todo management system.

## Tool: add_task
**Description**: Add a new task to the user's todo list
**Parameters**:
- user_id (string, required): The user identifier
- title (string, required): The task title
- description (string, optional): The task description

**Return**: Task object with id, title, description, and creation timestamp

## Tool: list_tasks
**Description**: Retrieve tasks for the user
**Parameters**:
- user_id (string, required): The user identifier
- status (string, optional): Filter by status (all, active, completed)

**Return**: Array of task objects with id, title, completion status, and timestamps

## Tool: update_task
**Description**: Update an existing task
**Parameters**:
- user_id (string, required): The user identifier
- task_id (string, required): The task identifier
- title (string, optional): The new task title
- description (string, optional): The new task description

**Return**: Updated task object

## Tool: complete_task
**Description**: Mark a task as completed
**Parameters**:
- user_id (string, required): The user identifier
- task_id (string, required): The task identifier

**Return**: Updated task object with completion status

## Tool: delete_task
**Description**: Delete a task from the user's list
**Parameters**:
- user_id (string, required): The user identifier
- task_id (string, required): The task identifier

**Return**: Boolean indicating success

## Security Considerations
- All tools must validate that the user owns the requested resources
- Tools must validate input parameters
- Tools must return structured JSON responses
- Tools must handle errors safely without exposing system details