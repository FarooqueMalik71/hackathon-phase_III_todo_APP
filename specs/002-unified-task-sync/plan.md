# Implementation Plan: Unified Task Sync — Chatbot as Dashboard Controller

**Branch**: `002-unified-task-sync` | **Date**: 2026-02-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-unified-task-sync/spec.md`

## Summary

Unify the chatbot and dashboard data paths so that ALL task operations (create, read, update, delete, toggle) flow through a single API layer (`/api/v1/tasks`). The chatbot's `TaskIntegrationService` currently writes directly to the database via its own SQLModel sessions, bypassing the REST API. This plan refactors the chatbot tool layer to call the existing task API service functions internally (same-process invocation), adds polling-based dashboard sync, integrates the chatbot entry point on the dashboard, implements responsive UI polish, and ensures authenticated user context flows through the entire chain.

## Technical Context

**Language/Version**: Python 3.11 (backend), TypeScript 5.9 / Node.js 18+ (frontend)
**Primary Dependencies**: FastAPI 0.104.1, SQLModel 0.0.16, Next.js 16.1.6, React 18.2, Tailwind CSS 3.4, OpenAI SDK (OpenRouter), Axios 1.6
**Storage**: SQLite (dev) / PostgreSQL via Neon (prod), single database for tasks + conversations
**Testing**: pytest, pytest-asyncio (backend); manual verification (frontend)
**Target Platform**: Linux server (HuggingFace Spaces backend), Vercel (frontend)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: Chat-to-dashboard sync within 3 seconds; task operations via chat < 15 seconds end-to-end
**Constraints**: No WebSocket/SSE (out of scope); BroadcastChannel for cross-tab, polling for cross-device; single-user data isolation
**Scale/Scope**: Single-user sessions, ~100s of tasks per user, hackathon-scale

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Supremacy of Specs | PASS | Spec at `specs/002-unified-task-sync/spec.md` approved with 16/16 quality checks |
| II. No Manual Coding | PASS | All code via Claude Code |
| III. Agent Boundaries | PASS | Plan phase only — no implementation in this artifact |
| IV. Phase-Gated Execution | PASS | Spec complete → Plan (this phase) → Tasks → Implementation |
| V. Monorepo & Structure | PASS | Single repo, `frontend/` + `backend/` structure maintained |
| VI. Security & Auth | PASS | Plan routes user_id from JWT through all layers; no cross-user data |
| VII. Traceability | PASS | Spec → Plan → Tasks → Code chain maintained |
| VIII. Failure Handling | PASS | No missing specs or conflicting requirements detected |
| IX. Optimization Goal | PASS | Prioritizes correctness and architectural integrity over speed |
| X. Final Authority | PASS | Constitution > Spec > CLAUDE.md hierarchy respected |

## Project Structure

### Documentation (this feature)

```text
specs/002-unified-task-sync/
├── plan.md              # This file
├── research.md          # Phase 0: Architecture research and decisions
├── data-model.md        # Phase 1: Data model documentation
├── quickstart.md        # Phase 1: Developer quickstart guide
├── contracts/           # Phase 1: API contracts
│   ├── task-api.md      # Task API contract (existing, documented)
│   └── chat-api.md      # Chat API contract (existing, documented)
└── tasks.md             # Phase 2: Task breakdown (created by /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── main.py                          # FastAPI app entry, mounts routers
├── api/v1/
│   ├── tasks.py                     # Phase II task CRUD endpoints (EXISTING - source of truth)
│   └── auth.py                      # Auth endpoints (EXISTING)
├── models/
│   └── task.py                      # Task SQLModel (EXISTING)
├── core/
│   ├── config.py                    # Environment config (EXISTING)
│   └── security.py                  # JWT utilities (EXISTING)
├── db/
│   └── session.py                   # Database sessions (MODIFY - remove sync session)
├── src/
│   ├── api/v1/
│   │   ├── chat_endpoints.py        # Chat endpoints (MODIFY - add auth)
│   │   └── conversation_endpoints.py # Conversation endpoints (MODIFY - add auth)
│   ├── services/
│   │   ├── task_integration_service.py  # (REWRITE - call task API service layer)
│   │   ├── ai_agent_service.py          # AI agent (MODIFY - pass user_id from auth)
│   │   └── chat_service.py              # Chat service (EXISTING)
│   ├── tools/
│   │   ├── task_tools.py            # MCP tools (MODIFY - accept user_id from auth context)
│   │   └── mcp_server.py            # MCP server (EXISTING)
│   ├── middleware/
│   │   └── auth.py                  # Auth middleware (EXISTING)
│   └── models/
│       ├── conversation.py          # Conversation model (EXISTING)
│       └── message.py               # Message model (EXISTING)
└── requirements.txt

frontend/
├── app/
│   ├── chat/
│   │   └── page.tsx                 # Chat page (MODIFY - responsive, auth)
│   ├── dashboard/
│   │   ├── page.tsx                 # Dashboard (MODIFY - polling sync, floating button)
│   │   └── components/
│   │       └── ui/
│   │           ├── header-nav.tsx   # Navigation (EXISTING - has AI link)
│   │           └── task-list.tsx    # Task list (MODIFY - loading/empty states)
│   └── layout.tsx                   # Root layout (EXISTING)
├── components/
│   └── chat/
│       └── ChatInterface.tsx        # Chat UI (MODIFY - responsive, error states)
├── lib/
│   ├── api.ts                       # Task API client (EXISTING)
│   ├── api/
│   │   └── chatAPI.ts               # Chat API client (MODIFY - use auth token)
│   ├── taskSync.ts                  # Cross-tab sync (MODIFY - add polling)
│   └── types/
│       └── chat.d.ts                # Chat types (EXISTING)
├── package.json
└── tsconfig.json
```

**Structure Decision**: Web application structure. Both `backend/` and `frontend/` directories exist and are the established pattern from feature 001-ai-chatbot. No new top-level directories needed. Changes are modifications to existing files, not new directory creation.

## Architecture Decisions

### AD-1: Internal Service Call vs HTTP Round-Trip for Chatbot → Task API

**Decision**: Use **direct service-layer invocation** (import and call the same Python functions that the REST endpoints use) rather than making HTTP requests from the chatbot to the task API.

**Why**:
- Chatbot and task API run in the **same FastAPI process** — no network overhead needed
- Avoids circular HTTP calls (server calling itself)
- Maintains the architectural constraint (AC-003): chatbot routes through the same logic as `/api/v1/tasks`
- Lower latency, no serialization/deserialization overhead

**Implementation**: `TaskIntegrationService` will import and call the same CRUD functions used by `tasks.py` endpoints, passing the authenticated user_id and an async database session.

### AD-2: Dashboard Sync Strategy — Polling + BroadcastChannel

**Decision**: Use **BroadcastChannel** for same-browser cross-tab sync (already implemented) and add **periodic polling** (every 3 seconds) as the primary dashboard-to-API sync mechanism.

**Why**:
- WebSocket/SSE is explicitly out of scope per spec
- BroadcastChannel only works within the same browser — doesn't cover cross-device or chatbot-originated changes that skip the frontend
- Polling at 3s intervals meets the SC-001 success criterion (sync within 3 seconds)
- Simple to implement, reliable, no backend changes needed

**Implementation**: Dashboard `useEffect` adds a 3-second `setInterval` calling `fetchTasks()`. BroadcastChannel provides immediate sync for same-browser scenarios.

### AD-3: Auth Token Flow — Restore JWT Dependency on Chat Endpoints

**Decision**: **Re-add** `Depends(get_current_user)` to chat and conversation endpoints (removed during 001 debugging) and pass the authenticated user_id through the tool chain.

**Why**:
- FR-007 mandates: "No hardcoded user IDs are permitted in production code"
- SC-007: "Chatbot correctly identifies the logged-in user"
- Constitution VI: "All API access requires valid JWT"
- Currently, `user_id` is a URL parameter — anyone can access any user's data

**Implementation**: Chat endpoints extract `user_id` from JWT via `get_current_user` dependency. This user_id flows to `AIAgentService` → `MCP tools` → `TaskIntegrationService`. The `{user_id}` URL parameter is replaced by the authenticated user from the token.

### AD-4: TaskIntegrationService Rewrite — Async + Shared DB Session

**Decision**: Rewrite `TaskIntegrationService` from synchronous direct-DB to **async methods that use the same async session pattern** as the task API endpoints.

**Why**:
- Current implementation uses `create_sync_session()` — a separate sync session bypassing the API
- AC-002: "All task mutations MUST route through `/api/v1/tasks` endpoints" (same logic)
- Async throughout eliminates the sync/async session mismatch
- Eliminates the `create_sync_session()` function and sync engine dependency

**Implementation**: `TaskIntegrationService` becomes an async class. Methods accept `AsyncSession` via dependency injection. They call the same SQLModel queries used by `tasks.py` CRUD functions.

## Change Summary

### WHAT to Change, WHERE, and WHY

| # | What | Where | Why |
|---|------|-------|-----|
| 1 | Rewrite TaskIntegrationService to async, use shared CRUD logic | `backend/src/services/task_integration_service.py` | AC-002, AC-003: Single data path for all task operations |
| 2 | Extract task CRUD into reusable service functions | `backend/services/task_service.py` (new) | Shared between REST endpoints and chatbot tools |
| 3 | Update task tools to async, pass user_id from auth | `backend/src/tools/task_tools.py` | FR-007: Use authenticated user context |
| 4 | Update MCP server for async tool execution | `backend/src/tools/mcp_server.py` | Support async tool handlers |
| 5 | Re-add auth to chat/conversation endpoints | `backend/src/api/v1/chat_endpoints.py`, `conversation_endpoints.py` | Constitution VI, FR-007 |
| 6 | Refactor chat endpoints to remove URL user_id param | `backend/src/api/v1/chat_endpoints.py` | FR-007: User from JWT, not URL |
| 7 | Update AI agent service for async tool flow | `backend/src/services/ai_agent_service.py` | Support async tool execution chain |
| 8 | Add polling-based sync to dashboard | `frontend/app/dashboard/page.tsx` | FR-003: Real-time sync within 3 seconds |
| 9 | Update chatAPI to use auth token from localStorage | `frontend/lib/api/chatAPI.ts` | FR-007: No hardcoded user IDs |
| 10 | Add loading, empty, error states to dashboard | `frontend/app/dashboard/page.tsx`, task-list component | FR-009 |
| 11 | Add loading, error states to chat interface | `frontend/components/chat/ChatInterface.tsx` | FR-009, FR-010 |
| 12 | Make chat page fully responsive | `frontend/app/chat/page.tsx`, `ChatInterface.tsx` | FR-008: 375px–1440px |
| 13 | Make dashboard fully responsive | `frontend/app/dashboard/page.tsx` | FR-008: 375px–1440px |
| 14 | Clean up dead code and unused imports | Various files | Production readiness, FR-011 |
| 15 | Remove `create_sync_session` from db/session.py | `backend/db/session.py` | No longer needed after async rewrite |
| 16 | Fix frontend TypeScript/lint errors | Various frontend files | FR-011: Zero TS errors, zero lint errors |
| 17 | Update chat endpoint URL format | Frontend `chatAPI.ts` + backend routes | Remove hardcoded user_id from URL path |

## Execution Strategy

### Phase Order

1. **Backend Core Refactor** (Changes 1–7): Extract shared task service, rewrite TaskIntegrationService, restore auth, make tools async
2. **Frontend Sync & Auth** (Changes 8–9, 17): Add polling, fix auth token flow, update API URLs
3. **UI Polish & Responsiveness** (Changes 10–13): Loading/empty/error states, responsive layouts
4. **Cleanup & Validation** (Changes 14–16): Dead code removal, TypeScript fixes, build verification

### Parallel Opportunities

- Changes 1–2 (backend service refactor) must complete before Changes 3–7
- Changes 8–9 (frontend sync/auth) can run in parallel with backend refactor
- Changes 10–13 (UI polish) are independent and can run in parallel with each other
- Changes 14–16 (cleanup) should come last

## Risk Mitigation

- **Risk**: Async rewrite breaks existing tool execution flow → **Mitigation**: Test each tool individually after conversion; maintain same response format
- **Risk**: Auth restoration breaks frontend → **Mitigation**: Update frontend chatAPI auth simultaneously; test with real token flow
- **Risk**: Polling creates excessive server load → **Mitigation**: 3-second interval is acceptable for hackathon scale; add conditional polling (only when tab is visible)

## Complexity Tracking

> No constitution violations detected. All changes use existing patterns and infrastructure.

| Aspect | Complexity | Justification |
|--------|-----------|---------------|
| Service extraction | Low | Moving existing CRUD logic into shared functions |
| Async conversion | Medium | TaskIntegrationService + tools need async/await throughout |
| Auth restoration | Low | Re-adding previously removed `Depends()` calls |
| Polling sync | Low | Simple `setInterval` + `fetchTasks()` |
| Responsive UI | Medium | CSS/Tailwind adjustments across 4 breakpoints |
