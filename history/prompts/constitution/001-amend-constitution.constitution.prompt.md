---
id: 001
title: Amend Constitution
stage: constitution
date: 2026-01-22
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: farooque_malik
command: sp.constitution
labels: [constitution, governance, sdd]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
---

## Prompt

```text
You are operating under the Spec-Driven Development Constitution (sp.constitution).

This constitution is the highest authority. All agents, plans, and implementations must comply.

────────────────────────────────────────
1. SUPREMACY OF SPECS
────────────────────────────────────────
• Specifications are the single source of truth.
• No code may be written without an explicit spec.
• If a behavior is not described in a spec, it must not be implemented.
• If a spec is ambiguous, it must be clarified in the spec before proceeding.

────────────────────────────────────────
2. NO MANUAL CODING
────────────────────────────────────────
• All code must be generated via Claude Code.
• Humans may only:
  – Write or update specs
  – Issue prompts
  – Review outputs
• Any manual code change is a violation.

────────────────────────────────────────
3. AGENT BOUNDARIES
────────────────────────────────────────
Each agent must strictly operate within its assigned role:

• Spec Writer Agent → writes specs only
• Architecture Planner Agent → plans and designs only
• Database Engineer Agent → database specs and ORM alignment only
• Backend Engineer Agent → backend implementation only
• Frontend Engineer Agent → frontend implementation only
• Integration Tester Agent → validation and reporting only

Agents must not:
• Cross responsibilities
• Modify specs unless authorized
• Implement outside their scope

────────────────────────────────────────
4. PHASE-GATED EXECUTION
────────────────────────────────────────
Work must proceed strictly in this order:

1. Specs written and approved
2. Architecture planned
3. Tasks broken down
4. Implementation executed
5. Integration validated

No phase may begin unless the previous phase is complete.

────────────────────────────────────────
5. MONOREPO & STRUCTURE ENFORCEMENT
────────────────────────────────────────
• The project uses a single monorepo.
• Specs must reside only in /specs.
• Code must respect:
  – /frontend/CLAUDE.md
  – /backend/CLAUDE.md
• Cross-cutting changes must be coordinated via specs.

────────────────────────────────────────
6. SECURITY & AUTH NON-NEGOTIABLES
────────────────────────────────────────
• All API access requires valid JWT.
• JWT must be verified on backend.
• User identity from token must scope all data access.
• No endpoint may return cross-user data.
• Secrets must come from environment variables only.

────────────────────────────────────────
7. TRACEABILITY REQUIREMENT
────────────────────────────────────────
Every implementation must be traceable:

Spec → Plan → Task → Code → Validation

If traceability is broken, work must stop.

────────────────────────────────────────
8. FAILURE HANDLING
────────────────────────────────────────
If any agent:
• Encounters missing specs
• Detects conflicting requirements
• Identifies security ambiguity

The agent must STOP and request a spec update.

────────────────────────────────────────
9. OPTIMIZATION GOAL
────────────────────────────────────────
This project optimizes for:
• Spec clarity
• Agentic discipline
• Security correctness
• Hackathon evaluation readiness

Speed is secondary to correctness and traceability.

────────────────────────────────────────
10. FINAL AUTHORITY
────────────────────────────────────────
If instructions conflict:
sp.constitution > specs > CLAUDE.md > agent prompt > ad-hoc instruction

No exception is permitted.
```

## Response snapshot

I've successfully updated the constitution file with the Spec-Driven Development Constitution. The new constitution contains 10 core principles that govern the development process:

1. Supremacy of Specs - Specifications are the single source of truth
2. No Manual Coding - All code must be generated via Claude Code
3. Agent Boundaries - Each agent operates within assigned role
4. Phase-Gated Execution - Work proceeds in strict order
5. Monorepo & Structure Enforcement - Single monorepo with defined structure
6. Security & Auth Non-Negotiables - JWT-based authentication and data isolation
7. Traceability Requirement - All implementations must be traceable
8. Failure Handling - Stop and request spec updates when issues arise
9. Optimization Goal - Prioritize spec clarity and security
10. Final Authority - Constitution supersedes all other instructions

The constitution also includes sections on Additional Constraints (Security Requirements and Code Quality Standards), Development Workflow (Specification Process, Review Process, Quality Gates), and Governance.

## Outcome

- ✅ Impact: Major governance update - new constitution replaces template
- 🧪 Tests: N/A
- 📁 Files: Updated .specify/memory/constitution.md with complete SDD constitution
- 🔁 Next prompts: Ready to proceed with spec-driven development workflow
- 🧠 Reflection: Constitution now provides clear governance framework for all development activities

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A