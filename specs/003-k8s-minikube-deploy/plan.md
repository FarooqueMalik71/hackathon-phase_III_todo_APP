# Implementation Plan: Kubernetes Deployment with Minikube

**Branch**: `003-k8s-minikube-deploy` | **Date**: 2026-02-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-k8s-minikube-deploy/spec.md`

## Summary

Deploy the existing full-stack Todo + AI Chatbot application (FastAPI backend, Next.js frontend, PostgreSQL) to a local Kubernetes cluster using Minikube and Helm charts. This is infrastructure-only — zero application code changes. New files added: production Dockerfiles, docker-compose.prod.yml, Helm chart, and deployment documentation.

## Technical Context

**Language/Version**: Python 3.11 (backend), Node.js 18+ / TypeScript (frontend)
**Primary Dependencies**: FastAPI, Next.js 16, PostgreSQL 16, Docker, Minikube, Helm 3
**Storage**: PostgreSQL 16-alpine (PersistentVolumeClaim in K8s)
**Testing**: Manual verification — `docker compose up`, `helm install`, `kubectl get pods`
**Target Platform**: Local Kubernetes (Minikube) on Linux/macOS/Windows
**Project Type**: Web application (backend + frontend + database)
**Performance Goals**: N/A — same as local dev (infrastructure parity, not optimization)
**Constraints**: Zero changes to existing application code (FR-009)
**Scale/Scope**: Single-node Minikube, 1 replica per service, local development only

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
| --------- | ------ | ----- |
| I. Supremacy of Specs | PASS | Spec written and approved before planning |
| II. No Manual Coding | PASS | All infrastructure files generated via Claude Code |
| III. Agent Boundaries | PASS | Plan phase only — no implementation |
| IV. Phase-Gated Execution | PASS | Spec → Plan → Tasks → Implement → Validate |
| V. Monorepo & Structure | PASS | All files in monorepo; infra/ and helm/ at root |
| VI. Security & Auth | PASS | Secrets via K8s Secrets, not hardcoded; JWT unchanged |
| VII. Traceability | PASS | Spec → Plan → Tasks chain maintained |
| VIII. Failure Handling | PASS | FR-009 constraint: stop if app code change needed |
| IX. Optimization Goal | PASS | Minimal, correct infrastructure — no over-engineering |
| X. Final Authority | PASS | Constitution > Spec > Plan hierarchy respected |

## Project Structure

### Documentation (this feature)

```text
specs/003-k8s-minikube-deploy/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0: research findings
├── data-model.md        # Phase 1: infrastructure entities
├── quickstart.md        # Phase 1: quick deployment guide
├── contracts/           # Phase 1: file manifest & contracts
│   └── file-manifest.md
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (created by /sp.tasks)
```

### Source Code (new files at repository root)

```text
hackathon_todo_II/
├── infra/
│   └── docker/
│       ├── backend.Dockerfile          # Production backend image
│       └── frontend.Dockerfile         # Production frontend image
├── docker-compose.prod.yml             # Production compose file
├── helm/
│   └── hackathon-todo/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
│           ├── _helpers.tpl
│           ├── backend-deployment.yaml
│           ├── backend-service.yaml
│           ├── frontend-deployment.yaml
│           ├── frontend-service.yaml
│           ├── postgres-deployment.yaml
│           ├── postgres-service.yaml
│           ├── postgres-pvc.yaml
│           ├── configmap.yaml
│           └── secret.yaml
└── docs/
    └── k8s-deployment-guide.md
```

**Structure Decision**: New infrastructure files placed in `infra/`, `helm/`, and `docs/` directories at the repo root. No existing directories are modified. The `infra/docker/` pattern separates production Dockerfiles from the application source.

## Implementation Steps

### Step 1: Create Backend Production Dockerfile

**File**: `infra/docker/backend.Dockerfile`
**Traces to**: FR-001

- Base image: `python:3.11-slim`
- Install system deps (gcc, libpq-dev for psycopg2)
- Copy `requirements.txt`, pip install
- Copy application code
- Non-root user
- Expose port 8000
- CMD: `uvicorn main:app --host 0.0.0.0 --port 8000`
- Build context: `./backend`

**Key detail**: The existing `backend/Dockerfile` uses port 7860 (Hugging Face Spaces). The production Dockerfile uses port 8000 (matching all other config). The existing file is NOT modified.

### Step 2: Create Frontend Production Dockerfile

**File**: `infra/docker/frontend.Dockerfile`
**Traces to**: FR-002

- Multi-stage build:
  - Stage 1 (`builder`): `node:18-alpine`, `npm ci`, `npm run build`
  - Stage 2 (`runner`): `node:18-alpine`, copy built assets, `npm start`
- Build ARG: `NEXT_PUBLIC_API_URL` (needed at build time by Next.js)
- Non-root user
- Expose port 3000
- Build context: `./frontend`

### Step 3: Create Production Docker Compose

**File**: `docker-compose.prod.yml`
**Traces to**: FR-003

- Three services: postgres, backend, frontend
- Uses production Dockerfiles from `infra/docker/`
- No volume mounts (built images only)
- Health checks on postgres and backend
- Dependency ordering: postgres → backend → frontend
- Environment variables from `.env` file with sensible defaults

### Step 4: Create Helm Chart Structure

**Files**: `helm/hackathon-todo/Chart.yaml`, `values.yaml`, `templates/`
**Traces to**: FR-004, FR-005, FR-006, FR-007, FR-008

**Chart.yaml**: Name `hackathon-todo`, version 0.1.0, appVersion 1.0.0

**values.yaml** structure:
```yaml
backend:
  image: hackathon-todo-backend:latest
  port: 8000
  replicas: 1
  resources: { requests: {cpu: 100m, memory: 128Mi}, limits: {cpu: 500m, memory: 512Mi} }

frontend:
  image: hackathon-todo-frontend:latest
  port: 3000
  replicas: 1
  resources: { requests: {cpu: 100m, memory: 128Mi}, limits: {cpu: 500m, memory: 512Mi} }

postgres:
  image: postgres:16-alpine
  port: 5432
  storage: 1Gi

config:
  databaseUrl: postgresql://postgres:postgres@hackathon-todo-postgres:5432/hackathon_todo
  secretKey: your-secret-key-change-in-production
  openaiBaseUrl: https://openrouter.ai/api/v1
  model: mistralai/mistral-7b-instruct
  environment: development
  nextPublicApiUrl: http://hackathon-todo-backend:8000

secrets:
  openaiApiKey: ""
  postgresPassword: postgres
```

**Templates**:
- `backend-deployment.yaml`: Deployment with liveness probe (`/health`), readiness probe (`/health`), env from ConfigMap + Secret
- `backend-service.yaml`: NodePort targeting port 8000
- `frontend-deployment.yaml`: Deployment with liveness probe (`/`), env from ConfigMap
- `frontend-service.yaml`: NodePort targeting port 3000
- `postgres-deployment.yaml`: Deployment with PVC mount, env from Secret
- `postgres-service.yaml`: ClusterIP targeting port 5432
- `postgres-pvc.yaml`: 1Gi PersistentVolumeClaim
- `configmap.yaml`: Non-sensitive configuration
- `secret.yaml`: Base64-encoded sensitive values

### Step 5: Test with Docker Compose

**Manual verification**:
```bash
docker build -f infra/docker/backend.Dockerfile -t hackathon-todo-backend:latest ./backend
docker build -f infra/docker/frontend.Dockerfile -t hackathon-todo-frontend:latest ./frontend
docker compose -f docker-compose.prod.yml up
# Verify: curl http://localhost:8000/health → {"status": "healthy"}
# Verify: http://localhost:3000 → App loads
```

### Step 6: Deploy to Minikube

**Manual verification**:
```bash
minikube start --memory=4096 --cpus=2
minikube image load hackathon-todo-backend:latest
minikube image load hackathon-todo-frontend:latest
helm install hackathon-todo ./helm/hackathon-todo
kubectl get pods  # All pods Running
minikube service hackathon-todo-frontend --url  # Access app
```

### Step 7: Create Deployment Documentation

**File**: `docs/k8s-deployment-guide.md`
**Traces to**: FR-011

- Prerequisites section (Docker, Minikube, kubectl, Helm versions)
- Step-by-step: build images → start Minikube → load images → helm install
- Verification steps
- Troubleshooting section (common errors and fixes)
- Teardown instructions

## Complexity Tracking

No constitution violations to justify. The plan adds only new files and uses the simplest viable approach for each component (single Helm chart, NodePort services, local image loading).

## Risks

1. **Next.js build-time env vars**: `NEXT_PUBLIC_API_URL` is baked at build time. Inside K8s, the frontend needs to reach the backend via the K8s service name, but the browser needs to reach it via the external URL. Mitigation: Use Next.js API rewrites (already configured in `next.config.js`) so browser calls go through the frontend's own server, which forwards to the backend service.
2. **Port conflicts**: Developer may have services on 8000/3000/5432. Mitigation: Document port changes in values.yaml and deployment guide.
3. **Image size**: Python and Node images can be large. Mitigation: Use slim/alpine base images and multi-stage builds.

## Follow-ups

- Run `/sp.tasks` to generate implementation tasks from this plan
- After implementation, verify SC-001 through SC-005 from the spec
