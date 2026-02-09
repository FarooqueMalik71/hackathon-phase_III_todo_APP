# Quickstart: Unified Task Sync

**Feature**: 002-unified-task-sync
**Date**: 2026-02-08

## Prerequisites

- Python 3.11+
- Node.js 18+
- npm/pnpm
- Git

## Setup

### 1. Clone and switch branch

```bash
git checkout 002-unified-task-sync
```

### 2. Backend setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp ../.env.example .env
# Edit .env with your values:
#   DATABASE_URL=sqlite+aiosqlite:///./todo.db  (dev)
#   OPENROUTER_API_KEY=your_key_here
#   SECRET_KEY=your_secret_key
```

### 3. Frontend setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
# Ensure .env has:
#   NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4. Start development servers

**Terminal 1 — Backend:**
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

### 5. Access the app

- Dashboard: http://localhost:3000/dashboard
- Chat: http://localhost:3000/chat
- API docs: http://localhost:8000/docs

## Verification Steps

After implementation, verify these acceptance criteria:

### SC-001: Cross-interface sync
1. Open dashboard in Tab 1
2. Open chat in Tab 2
3. In chat, type: "add task test sync"
4. Verify task appears in dashboard within 3 seconds

### SC-002: All operations via chat
Test each command:
```
"add task buy groceries"
"show my tasks"
"complete task buy groceries"
"update task buy groceries priority high"
"delete task buy groceries"
```

### SC-005: No direct DB writes from chatbot
1. Verify `TaskIntegrationService` imports from `task_service.py`
2. Verify no `create_sync_session()` calls remain
3. Verify all task tools use async session via dependency injection

### SC-006: Frontend build
```bash
cd frontend
npx tsc --noEmit   # Zero TypeScript errors
npx next lint       # Zero lint errors
npm run build       # Successful build
```

### SC-007: User isolation
1. Log in as user A, add a task via chat
2. Log in as user B in a different browser
3. User B types "show my tasks" — should NOT see user A's tasks

## Architecture Overview

```
Dashboard ──► REST API ──► task_service.py ──► Database
                                  ▲
Chat ──► AI Agent ──► MCP Tools ──┘
```

Both paths converge at `task_service.py` — the single source of truth for task CRUD logic.

## Key Files

| File | Purpose |
|------|---------|
| `backend/services/task_service.py` | Shared task CRUD functions (NEW) |
| `backend/src/services/task_integration_service.py` | Chatbot task adapter (REWRITTEN) |
| `backend/src/tools/task_tools.py` | MCP tool handlers (MODIFIED) |
| `backend/src/api/v1/chat_endpoints.py` | Chat API with auth (MODIFIED) |
| `frontend/lib/api/chatAPI.ts` | Chat API client with auth (MODIFIED) |
| `frontend/lib/taskSync.ts` | Cross-tab + polling sync (MODIFIED) |
| `frontend/app/dashboard/page.tsx` | Dashboard with polling (MODIFIED) |

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| 401 on chat endpoints | Missing auth token | Ensure frontend sends `Authorization: Bearer <token>` from localStorage |
| Tasks not syncing | Polling not active | Check dashboard has `setInterval` with `fetchTasks()` |
| Chat shows wrong user's tasks | Hardcoded user_id | Verify chatAPI.ts reads user from auth token, not hardcoded value |
| `async` errors in tools | Sync/async mismatch | Ensure all tool handlers are `async def` and use `await` |
