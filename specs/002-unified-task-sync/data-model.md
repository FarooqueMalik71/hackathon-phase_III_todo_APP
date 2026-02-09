# Data Model: Unified Task Sync

**Feature**: 002-unified-task-sync
**Date**: 2026-02-08

## Overview

This feature does NOT introduce new database tables or modify existing schemas. The architectural change is about **how data is accessed**, not what data exists. The core fix unifies the code path so both the dashboard and chatbot use the same service functions to query the same tables.

## Existing Entities (No Changes)

### Task

**Table**: `task`
**Location**: `backend/models/task.py`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | UUID | PK, default=uuid4 | Primary identifier |
| user_id | str | indexed, NOT NULL | Scopes all queries |
| title | str | min=1, max=255, NOT NULL | Task title |
| description | str | nullable | Optional description |
| completed | bool | default=False | Completion status |
| priority | enum (low/medium/high) | default=medium | Task priority |
| due_date | datetime | nullable | Optional due date |
| created_at | datetime | auto-set | Creation timestamp |
| updated_at | datetime | auto-set | Last modification timestamp |

**Pydantic Schemas** (existing):
- `TaskCreate`: title (required), description, priority, due_date
- `TaskRead`: all fields, id as UUID
- `TaskUpdate`: all fields optional

### Conversation

**Table**: `conversations`
**Location**: `backend/src/models/conversation.py`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | int | PK, auto-increment | Conversation identifier |
| user_id | str | indexed, NOT NULL | Owning user |
| created_at | datetime | auto-set | Creation time |
| updated_at | datetime | auto-set | Last activity |

**Relationships**: One-to-many with Message (cascade delete)

### Message

**Table**: `messages`
**Location**: `backend/src/models/message.py`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | int | PK, auto-increment | Message identifier |
| conversation_id | int | FK → conversations.id | Parent conversation |
| role | str | NOT NULL | "user" or "assistant" |
| content | str | max=2000, NOT NULL | Message text |
| created_at | datetime | auto-set | Timestamp |

**Relationships**: Many-to-one with Conversation

## Data Access Pattern Changes

### Before (Dual Path)

```
REST API Path:
  tasks.py endpoint → Depends(get_db) → AsyncSession → Task table

Chatbot Path:
  task_tools.py → TaskIntegrationService → create_sync_session() → SyncSession → Task table
```

Two separate sessions, two separate code paths, same table. Potential for inconsistent reads if transactions overlap.

### After (Unified Path)

```
Shared Service:
  task_service.py functions → AsyncSession (injected) → Task table

REST API Path:
  tasks.py endpoint → Depends(get_db) → task_service.create_task(session, user_id, data)

Chatbot Path:
  task_tools.py → Depends(get_db) → task_service.create_task(session, user_id, data)
```

Single set of functions, same async session provider, same table. Guarantees consistent behavior.

## Service Layer (New)

### TaskService Functions

**Location**: `backend/services/task_service.py` (new file)

```
async list_tasks(session, user_id, completed?, skip?, limit?) → List[Task]
async create_task(session, user_id, task_data: TaskCreate) → Task
async get_task(session, user_id, task_id: UUID) → Task | None
async update_task(session, user_id, task_id: UUID, task_data: TaskUpdate) → Task | None
async delete_task(session, user_id, task_id: UUID) → bool
async toggle_task(session, user_id, task_id: UUID) → Task | None
```

All functions:
- Accept `session: AsyncSession` as first parameter
- Accept `user_id: str` for ownership scoping
- Perform ownership verification before mutation
- Raise `HTTPException(404)` for not-found or ownership mismatch
- Handle commit/rollback within the session context

## Data Flow Diagram

```
┌─────────────────┐     ┌─────────────────┐
│   Dashboard UI  │     │   Chat UI       │
│   (Next.js)     │     │   (Next.js)     │
└────────┬────────┘     └────────┬────────┘
         │                       │
    REST API call          REST API call
    GET/POST/PUT/DELETE    POST /chat
    /api/v1/tasks/*
         │                       │
         ▼                       ▼
┌────────────────┐     ┌──────────────────┐
│  tasks.py      │     │ chat_endpoints.py│
│  (REST router) │     │ (Chat router)    │
└────────┬───────┘     └────────┬─────────┘
         │                      │
         │              ┌───────▼────────┐
         │              │ AIAgentService │
         │              │ → tool calls   │
         │              └───────┬────────┘
         │                      │
         │              ┌───────▼────────┐
         │              │ task_tools.py  │
         │              │ (MCP handlers) │
         │              └───────┬────────┘
         │                      │
         ▼                      ▼
┌─────────────────────────────────────────┐
│         task_service.py                 │
│  (shared CRUD functions)                │
│  list_tasks, create_task, get_task,     │
│  update_task, delete_task, toggle_task  │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│         AsyncSession (SQLModel)         │
│         via Depends(get_db)             │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│         Task Table (PostgreSQL)         │
│         Single Source of Truth          │
└─────────────────────────────────────────┘
```

## Migration Notes

- No database migrations needed
- No schema changes
- The `create_sync_session()` function in `db/session.py` can be removed after refactor
- The `SyncSessionLocal` and `sync_engine` can be removed if no other code depends on them
