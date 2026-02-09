# API Contract: Task API

**Feature**: 002-unified-task-sync
**Date**: 2026-02-08
**Base URL**: `/api/v1`

## Authentication

All endpoints require a valid JWT token in the `Authorization` header.

```
Authorization: Bearer <token>
```

The backend extracts `user_id` from the token via `Depends(get_current_user)`. All queries are scoped to this user_id. No endpoint returns cross-user data.

## Endpoints

### List Tasks

```
GET /api/v1/tasks/
```

**Query Parameters**:
| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| completed | bool | No | null | Filter by completion status |
| skip | int | No | 0 | Pagination offset |
| limit | int | No | 100 | Max results |

**Response**: `200 OK`
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "user123",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "priority": "medium",
    "due_date": "2026-02-10T00:00:00",
    "created_at": "2026-02-08T10:00:00",
    "updated_at": "2026-02-08T10:00:00"
  }
]
```

**Errors**: `401 Unauthorized` (missing/invalid token)

---

### Create Task

```
POST /api/v1/tasks/
```

**Request Body** (`TaskCreate`):
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "priority": "medium",
  "due_date": "2026-02-10T00:00:00"
}
```

| Field | Type | Required | Default | Validation |
|-------|------|----------|---------|------------|
| title | string | Yes | — | min 1, max 255 chars |
| description | string | No | null | — |
| priority | enum | No | "medium" | "low", "medium", "high" |
| due_date | datetime | No | null | ISO 8601 format |

**Response**: `200 OK` → `TaskRead` object (same shape as list item)

**Errors**: `401 Unauthorized`, `422 Validation Error`

---

### Get Task

```
GET /api/v1/tasks/{task_id}
```

**Path Parameters**: `task_id` (UUID)

**Response**: `200 OK` → `TaskRead` object

**Errors**: `401 Unauthorized`, `404 Not Found` (task doesn't exist or belongs to another user)

---

### Update Task

```
PUT /api/v1/tasks/{task_id}
```

**Path Parameters**: `task_id` (UUID)

**Request Body** (`TaskUpdate`):
```json
{
  "title": "Buy groceries updated",
  "description": "Milk, eggs, bread, butter",
  "priority": "high",
  "due_date": "2026-02-12T00:00:00"
}
```

All fields optional. Only provided fields are updated. `updated_at` is auto-refreshed.

**Response**: `200 OK` → Updated `TaskRead` object

**Errors**: `401 Unauthorized`, `404 Not Found`, `422 Validation Error`

---

### Delete Task

```
DELETE /api/v1/tasks/{task_id}
```

**Path Parameters**: `task_id` (UUID)

**Response**: `204 No Content`

**Errors**: `401 Unauthorized`, `404 Not Found`

---

### Toggle Completion

```
PATCH /api/v1/tasks/{task_id}/toggle
```

**Path Parameters**: `task_id` (UUID)

**Response**: `200 OK` → Updated `TaskRead` object (with `completed` flipped)

**Errors**: `401 Unauthorized`, `404 Not Found`

## Shared Service Layer (New in 002)

The task service functions called by BOTH REST endpoints and chatbot tools:

```python
# backend/services/task_service.py
async def list_tasks(session, user_id, completed=None, skip=0, limit=100) -> list[Task]
async def create_task(session, user_id, task_data: TaskCreate) -> Task
async def get_task(session, user_id, task_id: UUID) -> Task
async def update_task(session, user_id, task_id: UUID, task_data: TaskUpdate) -> Task
async def delete_task(session, user_id, task_id: UUID) -> None
async def toggle_task(session, user_id, task_id: UUID) -> Task
```

All functions raise `HTTPException(404)` if task not found or ownership mismatch.

## Error Taxonomy

| Status | Meaning | When |
|--------|---------|------|
| 200 | Success | GET, POST, PUT, PATCH |
| 204 | No Content | DELETE success |
| 401 | Unauthorized | Missing or invalid auth token |
| 404 | Not Found | Task ID doesn't exist or belongs to another user |
| 422 | Validation Error | Invalid request body |
| 500 | Internal Error | Unexpected server failure |
