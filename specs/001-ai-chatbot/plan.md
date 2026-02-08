# Implementation Plan: AI-Powered Todo Chatbot via OpenRouter + MCP

**Branch**: `001-ai-chatbot` | **Date**: 2026-02-07 | **Spec**: /mnt/e/hackathon_todo_II/specs/001-ai-chatbot/spec.md
**Input**: Feature specification from `/specs/001-ai-chatbot/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implementation of an AI-powered chatbot interface that allows users to manage todo tasks through natural language commands. The system will integrate with OpenRouter API for AI processing, use MCP tools for executing task operations, and maintain conversation history persistence. The solution will support both English and Roman Urdu input while maintaining a stateless backend architecture.

## Technical Context

**Language/Version**: Python 3.11, TypeScript/JavaScript (Node.js 18+)
**Primary Dependencies**: FastAPI, OpenRouter API, MCP Protocol, existing Phase II backend services
**Storage**: PostgreSQL (Neon), Conversation and Message entities
**Testing**: pytest for backend, Jest for frontend components
**Target Platform**: Web application (Linux server)
**Project Type**: web (dual frontend/backend structure)
**Performance Goals**: <3s response time for 90% of AI requests, 95% successful command interpretation rate
**Constraints**: <3s p95 response time, stateless backend, secure JWT authentication, conversation persistence
**Scale/Scope**: Individual user conversations, horizontally scalable, multi-language support (English/Roman Urdu)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Gates satisfied:
- ✓ Specifications exist and are clear
- ✓ No manual coding - all generation via Claude Code
- ✓ Agent boundaries respected (planning phase)
- ✓ Phase-gated execution followed (after spec phase)
- ✓ Monorepo structure respected (specs in /specs)
- ✓ Security requirements met (JWT authentication, user data isolation)
- ✓ Traceability maintained (Spec → Plan → Task → Code)

## Project Structure

### Documentation (this feature)

```text
specs/001-ai-chatbot/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── chat-api.yaml    # API contract specification
│   └── mcp-tools.md     # MCP tool specifications
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── conversation.py
│   │   └── message.py
│   ├── services/
│   │   ├── chat_service.py
│   │   ├── ai_agent_service.py
│   │   ├── mcp_tool_service.py
│   │   └── task_integration_service.py
│   ├── api/
│   │   ├── v1/
│   │   │   ├── chat_endpoints.py
│   │   │   └── conversation_endpoints.py
│   │   └── __init__.py
│   └── tools/
│       ├── mcp_server.py
│       └── task_tools.py
└── tests/
    ├── unit/
    ├── integration/
    └── contract/

frontend/
├── src/
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── MessageBubble.tsx
│   │   │   └── InputArea.tsx
│   │   └── ...
│   ├── services/
│   │   ├── api/
│   │   │   └── chat_api.ts
│   │   └── ...
│   ├── pages/
│   │   └── ChatPage.tsx
│   └── types/
│       └── chat.d.ts
└── tests/
    ├── unit/
    └── integration/
```

**Structure Decision**: Selected dual frontend/backend structure to accommodate the existing Phase II todo application architecture while adding the new AI chatbot functionality. The backend will handle AI integration, MCP tools, and conversation persistence, while the frontend will provide the chat interface that communicates with the backend API.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
