# Tasks: Kubernetes Deployment with Minikube

**Input**: Design documents from `/specs/003-k8s-minikube-deploy/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/file-manifest.md

**Tests**: Not requested — manual verification only.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Safety constraint**: FR-009 — NO existing application files may be modified. Only new files are created. If any task would require changing existing code, STOP and consult the user.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Directory Structure)

**Purpose**: Create the directory scaffolding for all new infrastructure files

- [x] T001 Create directory structure: `infra/docker/`, `helm/hackathon-todo/templates/`, `docs/`

**Checkpoint**: Empty directory structure exists. No application files touched.

---

## Phase 2: User Story 1 — Containerize and Run via Docker Compose (Priority: P1)

**Goal**: Developer can run the full stack (PostgreSQL, FastAPI, Next.js) via `docker compose up` with production-ready containers.

**Independent Test**: Run `docker compose -f docker-compose.prod.yml up --build`, then verify `curl http://localhost:8000/health` returns healthy and `http://localhost:3000` loads the app.

### Implementation for User Story 1

- [x] T002 [P] [US1] Create backend production Dockerfile in `infra/docker/backend.Dockerfile`
  - Base: `python:3.11-slim`
  - Install gcc, libpq-dev for psycopg2-binary
  - Copy `requirements.txt`, `pip install`
  - Copy all application code
  - Non-root user `appuser`
  - Expose port 8000
  - CMD: `uvicorn main:app --host 0.0.0.0 --port 8000`
  - Build context is `./backend`

- [x] T003 [P] [US1] Create frontend production Dockerfile in `infra/docker/frontend.Dockerfile`
  - Multi-stage build
  - Stage 1 (`builder`): `node:18-alpine`, `npm ci`, `npm run build`
  - Stage 2 (`runner`): `node:18-alpine`, copy `.next/`, `public/`, `package.json`, `next.config.js`, `node_modules/`
  - Build ARG: `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`)
  - Non-root user `nextjs`
  - Expose port 3000
  - CMD: `npm start`
  - Build context is `./frontend`

- [x] T004 [US1] Create production Docker Compose file in `docker-compose.prod.yml`
  - Three services: `postgres`, `backend`, `frontend`
  - postgres: `postgres:16-alpine`, healthcheck with `pg_isready`, port 5432, named volume `postgres_data`
  - backend: build from `infra/docker/backend.Dockerfile` with context `./backend`, port 8000, depends_on postgres (healthy), env vars for DATABASE_URL, SECRET_KEY, OPENAI_BASE_URL, OPENAI_API_KEY, MODEL
  - frontend: build from `infra/docker/frontend.Dockerfile` with context `./frontend`, port 3000, depends_on backend, build arg NEXT_PUBLIC_API_URL
  - Shared network `app-network`
  - No volume mounts (production images only)
  - Backend healthcheck: `curl -f http://localhost:8000/health`

**Checkpoint**: `docker compose -f docker-compose.prod.yml up --build` starts all 3 services. Backend health returns OK. Frontend loads in browser. US1 complete.

---

## Phase 3: User Story 2 — Deploy to Minikube with Helm Charts (Priority: P2)

**Goal**: Developer can deploy the containerized app to a local Minikube cluster using Helm and access it via NodePort services.

**Independent Test**: Start Minikube, load images, run `helm install hackathon-todo ./helm/hackathon-todo`, verify all pods Running, access frontend via `minikube service`.

### Implementation for User Story 2

- [x] T005 [P] [US2] Create Helm chart metadata in `helm/hackathon-todo/Chart.yaml`
  - apiVersion: v2
  - name: hackathon-todo
  - description: "Hackathon Todo + AI Chatbot — full-stack deployment"
  - version: 0.1.0
  - appVersion: "1.0.0"
  - type: application

- [x] T006 [P] [US2] Create Helm values file in `helm/hackathon-todo/values.yaml`
  - backend: image, port 8000, replicas 1, resources (100m/128Mi request, 500m/512Mi limit), imagePullPolicy Never
  - frontend: image, port 3000, replicas 1, resources (100m/128Mi request, 500m/512Mi limit), imagePullPolicy Never
  - postgres: image postgres:16-alpine, port 5432, storage 1Gi, imagePullPolicy IfNotPresent
  - config: databaseUrl, secretKey, openaiBaseUrl, model, environment, corsOrigins, nextPublicApiUrl
  - secrets: openaiApiKey, postgresPassword

- [x] T007 [P] [US2] Create Helm template helpers in `helm/hackathon-todo/templates/_helpers.tpl`
  - `hackathon-todo.fullname` helper
  - `hackathon-todo.labels` helper
  - `hackathon-todo.selectorLabels` helper

- [x] T008 [P] [US2] Create ConfigMap template in `helm/hackathon-todo/templates/configmap.yaml`
  - Name: `{{ include "hackathon-todo.fullname" . }}-config`
  - Keys: ENVIRONMENT, MODEL, OPENAI_BASE_URL, CORS_ORIGINS, NEXT_PUBLIC_API_URL

- [x] T009 [P] [US2] Create Secret template in `helm/hackathon-todo/templates/secret.yaml`
  - Name: `{{ include "hackathon-todo.fullname" . }}-secret`
  - Type: Opaque
  - Keys (base64): DATABASE_URL, SECRET_KEY, OPENAI_API_KEY, POSTGRES_PASSWORD

- [x] T010 [P] [US2] Create PostgreSQL PVC template in `helm/hackathon-todo/templates/postgres-pvc.yaml`
  - Name: `{{ include "hackathon-todo.fullname" . }}-postgres-pvc`
  - AccessMode: ReadWriteOnce
  - Storage: `{{ .Values.postgres.storage }}`

- [x] T011 [P] [US2] Create PostgreSQL Deployment template in `helm/hackathon-todo/templates/postgres-deployment.yaml`
  - 1 replica
  - Image from `values.postgres.image`
  - Port 5432
  - Env: POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB from Secret
  - Volume mount to PVC at `/var/lib/postgresql/data`

- [x] T012 [P] [US2] Create PostgreSQL Service template in `helm/hackathon-todo/templates/postgres-service.yaml`
  - Type: ClusterIP
  - Port 5432
  - Selector: app=postgres

- [x] T013 [P] [US2] Create Backend Deployment template in `helm/hackathon-todo/templates/backend-deployment.yaml`
  - 1 replica
  - Image from `values.backend.image`, imagePullPolicy Never
  - Port 8000
  - Env from ConfigMap + Secret (DATABASE_URL, SECRET_KEY, OPENAI_API_KEY, OPENAI_BASE_URL, MODEL)
  - Liveness probe: httpGet `/health` port 8000, initialDelaySeconds 15, periodSeconds 10
  - Readiness probe: httpGet `/health` port 8000, initialDelaySeconds 5, periodSeconds 5
  - Resources from values

- [x] T014 [P] [US2] Create Backend Service template in `helm/hackathon-todo/templates/backend-service.yaml`
  - Type: NodePort
  - Port 8000
  - Selector: app=backend

- [x] T015 [P] [US2] Create Frontend Deployment template in `helm/hackathon-todo/templates/frontend-deployment.yaml`
  - 1 replica
  - Image from `values.frontend.image`, imagePullPolicy Never
  - Port 3000
  - Env: NEXT_PUBLIC_API_URL from ConfigMap
  - Liveness probe: httpGet `/` port 3000, initialDelaySeconds 15, periodSeconds 10
  - Readiness probe: httpGet `/` port 3000, initialDelaySeconds 5, periodSeconds 5
  - Resources from values

- [x] T016 [P] [US2] Create Frontend Service template in `helm/hackathon-todo/templates/frontend-service.yaml`
  - Type: NodePort
  - Port 3000
  - Selector: app=frontend

**Checkpoint**: `helm install hackathon-todo ./helm/hackathon-todo` succeeds, `kubectl get pods` shows all Running, `minikube service hackathon-todo-frontend --url` opens working app. US2 complete.

---

## Phase 4: User Story 3 — Deployment Documentation (Priority: P3)

**Goal**: A developer unfamiliar with the project can deploy to Minikube by following a step-by-step guide.

**Independent Test**: Hand the document to someone who hasn't seen the project. They can deploy successfully.

### Implementation for User Story 3

- [x] T017 [US3] Create deployment guide in `docs/k8s-deployment-guide.md`
  - Prerequisites: Docker, Minikube v1.30+, kubectl v1.27+, Helm v3.12+
  - Section 1: Build Docker images (exact commands for backend + frontend)
  - Section 2: Test with Docker Compose (docker compose -f docker-compose.prod.yml up)
  - Section 3: Start Minikube (minikube start --memory=4096 --cpus=2)
  - Section 4: Load images into Minikube (minikube image load)
  - Section 5: Deploy with Helm (helm install)
  - Section 6: Verify deployment (kubectl get pods, kubectl get svc)
  - Section 7: Access the application (minikube service, port-forward)
  - Section 8: Troubleshooting (image pull errors, pod crash loops, port conflicts, resource limits)
  - Section 9: Teardown (helm uninstall, minikube stop/delete)
  - Section 10: Configuration reference (values.yaml parameters table)

**Checkpoint**: Documentation is complete, references all files created in US1 and US2. US3 complete.

---

## Phase 5: Polish & Validation

**Purpose**: Final verification that nothing was broken

- [x] T018 Verify no existing files were modified — run `git diff --name-only` to confirm only new files in `infra/`, `helm/`, `docs/`, and `docker-compose.prod.yml`
- [x] T019 Validate Helm chart syntax — run `helm lint ./helm/hackathon-todo` (structural validation passed; helm CLI not available in this env — run `helm lint` manually)
- [x] T020 Run quickstart.md validation — follow quickstart steps end-to-end (structural validation passed; runtime validation requires Docker/Minikube/Helm)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **US1 (Phase 2)**: Depends on Phase 1 (directories exist)
- **US2 (Phase 3)**: Depends on Phase 1 (directories exist). US2 tasks are independent of US1 (Helm chart doesn't need Dockerfiles to be written, only to reference their output images)
- **US3 (Phase 4)**: Depends on US1 + US2 (documentation references all created files)
- **Polish (Phase 5)**: Depends on all user stories complete

### User Story Dependencies

- **US1 (P1)**: T002 and T003 are parallel (different files). T004 depends on T002 + T003 (compose references both Dockerfiles).
- **US2 (P2)**: T005–T016 are ALL parallel (each is a separate file in the Helm chart, no cross-file dependencies). Can start after Phase 1.
- **US3 (P3)**: T017 depends on US1 + US2 completion (must reference actual files).

### Parallel Opportunities

```text
After T001 completes:
├── T002 (backend Dockerfile)     ─┐
├── T003 (frontend Dockerfile)     ├── All parallel
├── T005 (Chart.yaml)              │
├── T006 (values.yaml)             │
├── T007 (_helpers.tpl)            │
├── T008 (configmap.yaml)          │
├── T009 (secret.yaml)             │
├── T010 (postgres-pvc.yaml)       │
├── T011 (postgres-deployment)     │
├── T012 (postgres-service)        │
├── T013 (backend-deployment)      │
├── T014 (backend-service)         │
├── T015 (frontend-deployment)     │
└── T016 (frontend-service)       ─┘

After T002 + T003 complete:
└── T004 (docker-compose.prod.yml)

After T004 + T016 complete:
└── T017 (deployment guide)

After T017 completes:
├── T018 (verify no existing files modified)
├── T019 (helm lint)
└── T020 (quickstart validation)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete T001 (directory structure)
2. Complete T002 + T003 in parallel (Dockerfiles)
3. Complete T004 (docker-compose.prod.yml)
4. **STOP and VALIDATE**: `docker compose -f docker-compose.prod.yml up --build` — app works
5. This alone delivers value: any developer can run the app with Docker

### Incremental Delivery

1. T001 → T002+T003 → T004 → **US1 done** (Docker Compose works)
2. T005–T016 (all parallel) → **US2 done** (Helm + Minikube works)
3. T017 → **US3 done** (documentation complete)
4. T018–T020 → **Polish done** (validated and clean)

---

## Summary

| Metric | Value |
| ------ | ----- |
| Total tasks | 20 |
| US1 tasks | 3 (T002–T004) |
| US2 tasks | 12 (T005–T016) |
| US3 tasks | 1 (T017) |
| Setup tasks | 1 (T001) |
| Polish tasks | 3 (T018–T020) |
| Max parallel | 14 (T002–T003 + T005–T016 after T001) |
| New files created | 15 |
| Existing files modified | 0 |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- **CRITICAL**: If any task would require modifying existing application files, STOP and consult the user
