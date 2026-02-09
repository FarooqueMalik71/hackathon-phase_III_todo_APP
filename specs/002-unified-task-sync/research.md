# Phase 0 Research: Unified Task Sync

**Feature**: 002-unified-task-sync
**Date**: 2026-02-08
**Status**: Complete

## Research Questions

### RQ-1: How should the chatbot invoke the task API without making HTTP calls to itself?

**Finding**: The FastAPI backend runs both the task REST endpoints (`backend/api/v1/tasks.py`) and the chatbot endpoints (`backend/src/api/v1/chat_endpoints.py`) in the same Uvicorn process. The task endpoints use async SQLModel sessions via `Depends(get_db)` and call SQLModel queries directly.

**Approach**: Extract the core CRUD logic from `tasks.py` into a shared service module (`backend/services/task_service.py`). Both the REST endpoints and the chatbot's `TaskIntegrationService` import and call the same functions. This satisfies AC-003 ("chatbot tool layer MUST call the task API — internal service layer invocation through the same route handlers").

**Current code path (BROKEN)**:
```
Dashboard → REST API (tasks.py) → async SQLModel session → Database
Chatbot → TaskIntegrationService → create_sync_session() → Database (SEPARATE PATH)
```

**Target code path (UNIFIED)**:
```
Dashboard → REST API (tasks.py) → TaskService → async session → Database
Chatbot → MCP tools → TaskService → async session → Database (SAME PATH)
```

### RQ-2: What sync mechanism satisfies the 3-second requirement without WebSocket/SSE?

**Finding**: The spec explicitly excludes WebSocket/SSE from scope. Two mechanisms are available:

1. **BroadcastChannel API** (already implemented in `frontend/lib/taskSync.ts`): Provides instant cross-tab sync within the same browser. When chatbot modifies a task, `notifyTaskChange()` broadcasts to all tabs.

2. **Polling**: Dashboard periodically calls `GET /api/v1/tasks/` to refresh the task list. At 3-second intervals, this satisfies SC-001.

**Approach**: Keep BroadcastChannel for immediate same-browser sync. Add polling at 3-second intervals as the primary mechanism. Polling is paused when the tab is not visible (`document.hidden`) to reduce unnecessary requests.

**Browser Support**: BroadcastChannel is supported in all modern browsers (Chrome 54+, Firefox 38+, Safari 15.4+, Edge 79+). The `document.visibilityState` API is universally supported.

### RQ-3: How does the current auth system work, and how should user_id flow through the chatbot chain?

**Finding**: The auth system uses a simplified JWT approach (hackathon):

- `backend/src/middleware/auth.py`: `get_current_user()` extracts `credentials.credentials` from the `Authorization: Bearer <token>` header. In the current simplified implementation, the token value IS the user_id.
- `backend/api/v1/tasks.py`: All endpoints use `current_user: str = Depends(get_current_user)` to scope queries.
- `frontend/lib/api.ts`: Reads `localStorage.getItem('auth-token')` and sets `Authorization: Bearer <token>`.

**Current chatbot auth (BROKEN)**:
```
Frontend sends: POST /{user_id}/chat  (user_id in URL, no auth check)
Backend reads: user_id from URL path parameter
Tools receive: user_id passed as argument
```

**Target chatbot auth (FIXED)**:
```
Frontend sends: POST /chat  (user_id from auth token, not URL)
Backend reads: user_id = Depends(get_current_user)  (from JWT)
Tools receive: user_id injected from authenticated context
```

### RQ-4: What existing task CRUD functions can be reused?

**Finding**: `backend/api/v1/tasks.py` contains 6 endpoint functions with inline SQLModel queries:

| Endpoint | SQLModel Query Pattern |
|----------|----------------------|
| `list_tasks` | `session.exec(select(Task).where(Task.user_id == user_id).offset().limit())` |
| `create_task` | `Task(**task_data.dict(), user_id=user_id)` → `session.add()` → `session.commit()` |
| `get_task` | `session.get(Task, task_id)` with user_id ownership check |
| `update_task` | `session.get()` → update fields → `session.commit()` |
| `delete_task` | `session.get()` → `session.delete()` → `session.commit()` |
| `toggle_task` | `session.get()` → flip `completed` → `session.commit()` |

**Approach**: Extract these into standalone async functions in `backend/services/task_service.py` that accept `(session, user_id, ...)` parameters. The REST endpoints become thin wrappers calling these functions. The chatbot tools also call these functions.

### RQ-5: What is the current responsive state of the UI?

**Finding**: The dashboard uses Tailwind responsive classes (`sm:`, `md:`, `lg:`) in some places but the chat page has minimal responsive styling. Key gaps:

- Chat sidebar (conversation list) doesn't collapse on mobile
- Chat input area doesn't adapt to narrow viewports
- Dashboard floating button may overlap content on small screens
- Task list cards need responsive adjustments for mobile

**Approach**: Use Tailwind's responsive breakpoints aligned with the spec requirements:
- `sm:` (640px) → covers mobile 375px with base styles
- `md:` (768px) → tablet breakpoint
- `lg:` (1024px) → laptop breakpoint
- `xl:` (1440px) → desktop breakpoint

### RQ-6: What are the existing TypeScript/build issues?

**Finding**: The frontend uses `next-env.d.ts` and `tsconfig.json` with strict mode. Potential issues include:
- `dangerouslySetInnerHTML` usage in ChatInterface (type safety)
- Hardcoded `"user123"` in chatAPI.ts constructor
- Missing error type annotations in catch blocks
- Potential unused imports from previous iterations

**Approach**: Run `npx tsc --noEmit` and `npx next lint` to identify all issues. Fix systematically as the final cleanup step.

## Technology Decisions Summary

| Decision | Choice | Alternative Rejected | Reason |
|----------|--------|---------------------|--------|
| Chatbot→Task routing | Service-layer import | HTTP self-call | Same process, no overhead, no circular dependency |
| Dashboard sync | Polling (3s) + BroadcastChannel | WebSocket/SSE | Out of scope per spec; polling meets 3s requirement |
| Auth flow | JWT `Depends(get_current_user)` | URL parameter user_id | Security: URL param allows unauthorized access |
| Session management | Async throughout | Mixed sync/async | Eliminates session mismatch; matches FastAPI patterns |
| Responsive strategy | Tailwind responsive classes | CSS media queries | Already using Tailwind; consistent with codebase |

## Open Questions

None. All research questions resolved with clear approaches.
