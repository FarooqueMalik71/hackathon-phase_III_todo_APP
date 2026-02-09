---
description: "Task list for Unified Task Sync — Chatbot as Dashboard Controller"
---

# Tasks: Unified Task Sync — Chatbot as Dashboard Controller

**Input**: Design documents from `/specs/002-unified-task-sync/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Not requested in spec. Tests are excluded from this task list.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/`, `frontend/`
- Paths shown below match the existing project structure from plan.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Extract shared task service — the foundational refactor that all user stories depend on

- [x] T001 Create shared task service with async CRUD functions (list, create, get, update, delete, toggle) in backend/services/task_service.py — extract logic from backend/api/v1/tasks.py into standalone functions that accept (session, user_id, ...) parameters
- [x] T002 Refactor backend/api/v1/tasks.py REST endpoints to call task_service.py functions instead of inline SQLModel queries — endpoints become thin wrappers; verify all 6 endpoints still work via curl

**Checkpoint**: Shared task service exists. REST API still works identically. No chatbot changes yet.

---

## Phase 2: User Story 1 — Manage Tasks via Chat Using Unified API (Priority: P1) 🎯 MVP

**Goal**: Chatbot performs all task operations through the shared task service (same code path as REST API), eliminating the dual-write problem.

**Independent Test**: Send chat commands ("add task buy milk", "show my tasks", "complete task X", "delete task Y") and verify: (1) chatbot responds with confirmation, (2) GET /api/v1/tasks/ reflects the change, (3) no direct DB writes from chatbot path.

### Implementation for User Story 1

- [x] T003 [US1] Rewrite backend/src/services/task_integration_service.py — replace all sync direct-DB methods with async methods that call task_service.py functions. Remove create_sync_session() usage. Each method (add_task, list_tasks, complete_task, update_task, delete_task) must accept an async session parameter and delegate to task_service.py.
- [x] T004 [US1] Update backend/src/tools/task_tools.py — make all tool handlers async. Each handler must accept a db session and user_id, then call the rewritten TaskIntegrationService async methods. Remove any direct session creation.
- [x] T005 [US1] Update backend/src/tools/mcp_server.py — modify execute_tool() to support async tool handlers (use await). Pass db session and user_id through to tool handlers.
- [x] T006 [US1] Update backend/src/services/ai_agent_service.py — modify process_message() to pass async db session and authenticated user_id to MCP tool execution chain. Ensure tool results flow back correctly for follow-up AI response.
- [x] T007 [US1] Remove create_sync_session() function and SyncSessionLocal from backend/db/session.py — clean up the sync session code that is no longer needed after async rewrite.
- [x] T008 [US1] Verify all 5 chat task operations work end-to-end via curl: POST /api/{user_id}/chat with messages "add task test", "show my tasks", "complete task test", "update task test priority high", "delete task test". Confirm each uses the shared task_service.py path.

**Checkpoint**: Chatbot and dashboard now share the exact same CRUD code path. SC-005 satisfied.

---

## Phase 3: User Story 5 — Authenticated User Context (Priority: P5, moved up because US1 depends on auth for production correctness)

**Goal**: Chat endpoints use JWT auth instead of URL user_id parameter. Authenticated user identity flows through the entire chatbot tool chain.

**Independent Test**: Log in, open chat, send a task command, verify task is created under the correct user without any hardcoded user ID. Try without auth token — should get 401.

### Implementation for User Story 5

- [x] T009 [US5] Re-add Depends(get_current_user) to POST /chat endpoint in backend/src/api/v1/chat_endpoints.py — extract user_id from JWT token instead of URL path. Change route from /{user_id}/chat to /chat.
- [x] T010 [US5] Re-add Depends(get_current_user) to all conversation endpoints in backend/src/api/v1/conversation_endpoints.py — change routes from /{user_id}/conversations to /conversations. Add user ownership verification.
- [x] T011 [US5] Update frontend/lib/api/chatAPI.ts — remove hardcoded userId="user123". Read auth token from localStorage. Change base URL from /api/{userId} to /api. Ensure Authorization header is sent with every request.
- [x] T012 [US5] Update frontend/components/chat/ChatInterface.tsx — remove any hardcoded user_id references. Ensure sendMessage calls use the updated chatAPI that derives user from auth token.
- [x] T013 [US5] Update frontend/app/chat/page.tsx — add auth guard to redirect unauthenticated users to login page. Ensure conversation loading uses the updated API paths without user_id in URL.

**Checkpoint**: No hardcoded user IDs anywhere. Auth token provides user identity. SC-007 satisfied.

---

## Phase 4: User Story 2 — Real-Time Dashboard Sync (Priority: P2)

**Goal**: Changes made via chatbot appear in dashboard within 3 seconds without manual refresh, and vice versa.

**Independent Test**: Open dashboard and chat side by side. Add task via chat → dashboard updates within 3 seconds. Add task via dashboard → chatbot sees it on next query.

### Implementation for User Story 2

- [x] T014 [US2] Add 3-second polling interval to dashboard in frontend/app/dashboard/page.tsx — add useEffect with setInterval calling fetchTasks() every 3000ms. Pause polling when document.hidden is true (tab not visible). Clean up interval on unmount.
- [x] T015 [US2] Enhance frontend/lib/taskSync.ts — keep existing BroadcastChannel for instant cross-tab sync. Add window focus event listener to trigger immediate refresh when user switches back to dashboard tab. Export a startPolling/stopPolling utility.
- [x] T016 [US2] Verify sync: open two browser tabs (dashboard + chat). Add task via chat → confirm dashboard shows it within 3 seconds. Add task via dashboard → confirm chat "show my tasks" includes it.

**Checkpoint**: Dashboard and chatbot stay in sync within 3 seconds. SC-001 satisfied.

---

## Phase 5: User Story 3 — Integrated Chatbot Access from Dashboard (Priority: P3)

**Goal**: Users can access the chatbot directly from the dashboard via a visible floating button and/or navigation link.

**Independent Test**: Navigate to dashboard, locate chatbot entry point, click it, verify it opens chat. Test on mobile viewport to verify no overlap.

### Implementation for User Story 3

- [x] T017 [P] [US3] Verify floating chat button exists in frontend/app/dashboard/page.tsx — ensure the existing floating button (added in 001) has proper styling: fixed bottom-right, z-index above content, proper size (min 44px tap target), tooltip text. Fix if needed.
- [x] T018 [P] [US3] Verify "AI Assistant" navigation link exists in frontend/app/dashboard/components/ui/header-nav.tsx — ensure the link (added in 001) is visible in both desktop nav and mobile hamburger menu. Fix if needed.
- [x] T019 [US3] Verify "Back to Dashboard" link exists in frontend/app/chat/page.tsx — ensure clear navigation element to return to dashboard. Fix if needed.

**Checkpoint**: Chatbot is discoverable from dashboard. Users can navigate between both interfaces. FR-006 satisfied.

---

## Phase 6: User Story 4 — Professional Responsive UI (Priority: P4)

**Goal**: Polished, production-quality interface with proper loading states, empty states, error states, and responsive layout across all breakpoints.

**Independent Test**: View app across 4 breakpoints (375px, 768px, 1024px, 1440px). Verify no overflow, correct layout, readable text, proper interactive states, loading/empty/error states.

### Implementation for User Story 4

- [x] T020 [P] [US4] Add loading state to dashboard in frontend/app/dashboard/page.tsx — show skeleton or spinner while tasks are being fetched. Replace any flash of empty content.
- [x] T021 [P] [US4] Add empty state to dashboard — when user has zero tasks, display a friendly message with guidance ("No tasks yet. Create one using the form above or chat with AI Assistant"). Include an icon or illustration.
- [x] T022 [P] [US4] Add error state to dashboard — when task fetch fails, display a user-friendly error with a retry button instead of blank screen or console error.
- [x] T023 [P] [US4] Add error state to chat interface in frontend/components/chat/ChatInterface.tsx — when API call fails (network error, 500, timeout), show a user-friendly error message in the chat bubble area with retry option. Do not show raw error text.
- [x] T024 [US4] Make dashboard fully responsive in frontend/app/dashboard/page.tsx — verify layout at 375px, 768px, 1024px, 1440px. Fix any horizontal overflow. Ensure task cards stack properly on mobile. Minimum 44px tap targets for interactive elements.
- [x] T025 [US4] Make chat page fully responsive in frontend/app/chat/page.tsx and frontend/components/chat/ChatInterface.tsx — conversation sidebar should collapse/hide on mobile (<768px). Chat input area should span full width on mobile. Message bubbles should have appropriate max-width at each breakpoint.
- [x] T026 [US4] Add hover states to task cards on desktop — subtle visual response (shadow, background shift) when hovering over task items in the task list.

**Checkpoint**: Professional UI with all states handled. SC-003, SC-004 satisfied.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Cleanup, build validation, and production readiness

- [x] T027 [P] Remove dead code and unused imports across backend files — scan backend/src/services/, backend/src/tools/, backend/db/ for unused imports, commented-out code, and orphaned functions from the pre-refactor implementation
- [x] T028 [P] Remove dead code and unused imports across frontend files — scan frontend/lib/, frontend/components/, frontend/app/ for unused imports, hardcoded values, and orphaned functions
- [x] T029 Fix all TypeScript errors — run npx tsc --noEmit in frontend/ and fix every reported error. Target: zero errors.
- [x] T030 Fix all lint errors — run npx next lint in frontend/ and fix every reported issue. Target: zero warnings, zero errors.
- [x] T031 Verify frontend production build — run npm run build in frontend/ and confirm successful build with zero errors. Fix any build failures.
- [x] T032 Verify backend starts cleanly — run uvicorn main:app in backend/ and confirm no import errors, no missing dependencies, all routes mount correctly.
- [x] T033 Run full end-to-end verification per quickstart.md — test SC-001 (sync), SC-002 (all operations), SC-005 (no direct DB), SC-006 (build), SC-007 (user isolation), SC-008 (< 15s response).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (US1 - Unified API)**: Depends on Phase 1 (shared task service must exist)
- **Phase 3 (US5 - Auth)**: Depends on Phase 2 (tool chain must be async before adding auth flow)
- **Phase 4 (US2 - Sync)**: Can start after Phase 1. Independent of Phase 2/3.
- **Phase 5 (US3 - Dashboard Entry)**: Independent — can run anytime. Mostly verification of existing work.
- **Phase 6 (US4 - Responsive UI)**: Independent — can run anytime after Phase 1.
- **Phase 7 (Polish)**: Depends on all other phases being complete.

### Critical Path

```
T001 → T002 → T003 → T004 → T005 → T006 → T007 → T008 (US1 complete)
                                                          → T009 → T010 → T011 → T012 → T013 (US5 complete)
```

### Parallel Opportunities

- Phase 4 (US2 - Sync): T014–T016 can run in parallel with Phase 2 or Phase 3
- Phase 5 (US3 - Entry): T017, T018 can run in parallel with anything
- Phase 6 (US4 - UI): T020, T021, T022, T023 can all run in parallel
- Phase 7: T027 and T028 can run in parallel

---

## Parallel Example: Phase 6

```bash
# Launch all independent UI tasks together:
Task: "Add loading state to dashboard"
Task: "Add empty state to dashboard"
Task: "Add error state to dashboard"
Task: "Add error state to chat interface"
# Then sequentially:
Task: "Make dashboard fully responsive"
Task: "Make chat page fully responsive"
```

---

## Implementation Strategy

### MVP First (Phase 1 + Phase 2 = US1 Only)

1. Complete Phase 1: Shared task service extraction
2. Complete Phase 2: Chatbot → unified API
3. **STOP and VALIDATE**: Test US1 independently — all chat operations use shared service
4. Deploy/demo if ready

### Incremental Delivery

1. Phase 1 + Phase 2 → Unified data path (MVP!)
2. + Phase 3 → Authenticated user context
3. + Phase 4 → Real-time sync
4. + Phase 5 → Dashboard chatbot entry
5. + Phase 6 → Professional responsive UI
6. + Phase 7 → Production-ready build

### Task Count Summary

| Phase | Story | Tasks | Parallel |
|-------|-------|-------|----------|
| Phase 1: Setup | — | 2 | 0 |
| Phase 2: US1 - Unified API | US1 (P1) | 6 | 0 |
| Phase 3: US5 - Auth | US5 (P5) | 5 | 0 |
| Phase 4: US2 - Sync | US2 (P2) | 3 | 0 |
| Phase 5: US3 - Entry | US3 (P3) | 3 | 2 |
| Phase 6: US4 - Responsive UI | US4 (P4) | 7 | 4 |
| Phase 7: Polish | — | 7 | 2 |
| **Total** | | **33** | **8** |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- US5 (Auth) is moved before US2 (Sync) because auth correctness is critical for data isolation
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- No test tasks included — spec does not request automated testing infrastructure
