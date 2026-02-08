<!-- SYNC IMPACT REPORT
Version change: N/A -> 1.0.0
Modified principles: N/A (new constitution)
Added sections: All principles from the Spec-Driven Development Constitution
Removed sections: Template placeholders
Templates requiring updates: N/A (initial constitution)
Follow-up TODOs: None
-->

# Spec-Driven Development Constitution

## Core Principles

### I. Supremacy of Specs
Specifications are the single source of truth. No code may be written without an explicit spec. If a behavior is not described in a spec, it must not be implemented. If a spec is ambiguous, it must be clarified in the spec before proceeding.

### II. No Manual Coding
All code must be generated via Claude Code. Humans may only write or update specs, issue prompts, or review outputs. Any manual code change is a violation.

### III. Agent Boundaries
Each agent must strictly operate within its assigned role. Spec Writer Agent writes specs only; Architecture Planner Agent plans and designs only; Database Engineer Agent handles database specs and ORM alignment only; Backend Engineer Agent handles backend implementation only; Frontend Engineer Agent handles frontend implementation only; Integration Tester Agent performs validation and reporting only. Agents must not cross responsibilities, modify specs unless authorized, or implement outside their scope.

### IV. Phase-Gated Execution
Work must proceed strictly in this order: 1. Specs written and approved, 2. Architecture planned, 3. Tasks broken down, 4. Implementation executed, 5. Integration validated. No phase may begin unless the previous phase is complete.

### V. Monorepo & Structure Enforcement
The project uses a single monorepo. Specs must reside only in /specs. Code must respect /frontend/CLAUDE.md and /backend/CLAUDE.md. Cross-cutting changes must be coordinated via specs.

### VI. Security & Auth Non-Negotiables
All API access requires valid JWT. JWT must be verified on backend. User identity from token must scope all data access. No endpoint may return cross-user data. Secrets must come from environment variables only.

### VII. Traceability Requirement
Every implementation must be traceable: Spec → Plan → Task → Code → Validation. If traceability is broken, work must stop.

### VIII. Failure Handling
If any agent encounters missing specs, detects conflicting requirements, or identifies security ambiguity, the agent must STOP and request a spec update.

### IX. Optimization Goal
This project optimizes for spec clarity, agentic discipline, security correctness, and hackathon evaluation readiness. Speed is secondary to correctness and traceability.

### X. Final Authority
If instructions conflict: sp.constitution > specs > CLAUDE.md > agent prompt > ad-hoc instruction. No exception is permitted.

## Additional Constraints

### Security Requirements
All implementations must follow security-first principles. Authentication and authorization must be implemented according to the defined architecture. User data isolation is mandatory - no user may access another user's data.

### Code Quality Standards
All code must be production-ready, well-documented, and follow established patterns. Type safety must be maintained throughout the codebase. Error handling must be comprehensive and consistent.

## Development Workflow

### Specification Process
All features must begin with a clear, detailed specification. User stories must be defined with acceptance criteria. Technical requirements must be documented before implementation begins.

### Review Process
All implementations must be traceable back to specifications. Code reviews must verify compliance with the constitution and architectural plans. Security considerations must be validated during review.

### Quality Gates
Automated testing must cover all implemented functionality. Integration tests must verify system behavior. Security scanning must pass before merging.

## Governance

This constitution is the highest authority. All agents, plans, and implementations must comply. Amendments require explicit documentation and approval process. All team members must acknowledge and follow this constitution. Compliance reviews must occur regularly to ensure adherence to constitutional principles.

**Version**: 1.0.0 | **Ratified**: 2026-01-22 | **Last Amended**: 2026-01-22