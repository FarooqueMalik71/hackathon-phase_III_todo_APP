# API Contract: Chat API

**Feature**: 002-unified-task-sync
**Date**: 2026-02-08
**Base URL**: `/api`

## Authentication

All endpoints require a valid JWT token in the `Authorization` header.

```
Authorization: Bearer <token>
```

**Change from 001**: The `{user_id}` URL path parameter is removed. User identity comes exclusively from the JWT token via `Depends(get_current_user)`.

## Endpoints

### Send Chat Message

**Before (001)**:
```
POST /api/{user_id}/chat
```

**After (002)**:
```
POST /api/chat
```

**Request Body** (`ChatRequest`):
```json
{
  "message": "add task buy groceries",
  "conversation_id": 1
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| message | string | Yes | User's natural language message |
| conversation_id | int | No | Existing conversation ID; null creates new conversation |

**Response**: `200 OK` (`ChatResponse`)
```json
{
  "response": "I've added 'buy groceries' to your task list!",
  "conversation_id": 1,
  "tool_calls": [
    {
      "tool": "add_task",
      "arguments": {"title": "buy groceries", "priority": "medium"},
      "result": {"success": true, "task_id": "550e8400-..."}
    }
  ],
  "response_time": 2.3
}
```

| Field | Type | Description |
|-------|------|-------------|
| response | string | AI-generated conversational response |
| conversation_id | int | Conversation ID (new or existing) |
| tool_calls | array | List of tools the AI invoked, with arguments and results |
| response_time | float | Time in seconds for AI processing |

**Tool Call Object**:
```json
{
  "tool": "add_task",
  "arguments": {"title": "...", "priority": "..."},
  "result": {"success": true, "task_id": "...", "message": "..."}
}
```

**Errors**: `401 Unauthorized`, `422 Validation Error`, `500 AI Service Error`

---

### List Conversations

**Before (001)**:
```
GET /api/{user_id}/conversations
```

**After (002)**:
```
GET /api/conversations
```

**Query Parameters**:
| Param | Type | Required | Default |
|-------|------|----------|---------|
| limit | int | No | 20 |

**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "user_id": "user123",
    "created_at": "2026-02-08T10:00:00",
    "updated_at": "2026-02-08T10:30:00"
  }
]
```

**Errors**: `401 Unauthorized`

---

### Get Conversation Messages

**Before (001)**:
```
GET /api/{user_id}/conversations/{conversation_id}/messages
```

**After (002)**:
```
GET /api/conversations/{conversation_id}/messages
```

**Path Parameters**: `conversation_id` (int)

**Query Parameters**:
| Param | Type | Required | Default |
|-------|------|----------|---------|
| limit | int | No | 50 |

**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "conversation_id": 1,
    "role": "user",
    "content": "add task buy groceries",
    "created_at": "2026-02-08T10:00:00"
  },
  {
    "id": 2,
    "conversation_id": 1,
    "role": "assistant",
    "content": "I've added 'buy groceries' to your task list!",
    "created_at": "2026-02-08T10:00:02"
  }
]
```

**Errors**: `401 Unauthorized`, `404 Not Found` (conversation doesn't exist or belongs to another user)

---

### Delete Conversation

**Before (001)**:
```
DELETE /api/{user_id}/conversations/{conversation_id}
```

**After (002)**:
```
DELETE /api/conversations/{conversation_id}
```

**Path Parameters**: `conversation_id` (int)

**Response**: `200 OK`
```json
{"message": "Conversation deleted successfully"}
```

**Errors**: `401 Unauthorized`, `404 Not Found`

## Frontend API Client Changes

### chatAPI.ts Updates

```typescript
// BEFORE (001):
const BASE = `${API_URL}/api/${userId}`;
// Calls: GET  /api/user123/conversations
// Calls: POST /api/user123/chat

// AFTER (002):
const BASE = `${API_URL}/api`;
// Calls: GET  /api/conversations
// Calls: POST /api/chat
// Auth token from localStorage provides user identity
```

## MCP Tool Contracts

Tools invoked by the AI agent during chat. Each tool maps to a `task_service.py` function.

### add_task
```json
{
  "name": "add_task",
  "parameters": {
    "title": {"type": "string", "required": true},
    "description": {"type": "string"},
    "priority": {"type": "string", "enum": ["low", "medium", "high"]},
    "due_date": {"type": "string", "format": "date-time"}
  }
}
```
**Returns**: `{"success": true, "task_id": "...", "message": "Task 'X' added"}`

### list_tasks
```json
{
  "name": "list_tasks",
  "parameters": {
    "completed": {"type": "boolean"}
  }
}
```
**Returns**: `{"success": true, "tasks": [...], "count": N}`

### complete_task
```json
{
  "name": "complete_task",
  "parameters": {
    "task_id": {"type": "string", "required": true}
  }
}
```
**Returns**: `{"success": true, "message": "Task 'X' marked as completed"}`

### update_task
```json
{
  "name": "update_task",
  "parameters": {
    "task_id": {"type": "string", "required": true},
    "title": {"type": "string"},
    "description": {"type": "string"},
    "priority": {"type": "string", "enum": ["low", "medium", "high"]},
    "due_date": {"type": "string", "format": "date-time"}
  }
}
```
**Returns**: `{"success": true, "message": "Task 'X' updated"}`

### delete_task
```json
{
  "name": "delete_task",
  "parameters": {
    "task_id": {"type": "string", "required": true}
  }
}
```
**Returns**: `{"success": true, "message": "Task 'X' deleted"}`

## Error Response Format

All error responses follow this structure:
```json
{
  "detail": "Human-readable error message"
}
```

For validation errors (422):
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```
