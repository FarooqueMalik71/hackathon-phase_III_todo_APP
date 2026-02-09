# Research: Kubernetes Deployment with Minikube

**Feature**: 003-k8s-minikube-deploy
**Date**: 2026-02-09

## Research Findings

### R1: Existing Backend Dockerfile Gap

**Decision**: The existing `backend/Dockerfile` uses Python 3.9 and exposes port 7860 with entry point `main:app`. The docker-compose.yml overrides the command to `uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload`. For production deployment, we need a new production Dockerfile that uses Python 3.11 (matching project stack) and port 8000 (matching all other config).

**Rationale**: The existing Dockerfile appears to be a Hugging Face Spaces artifact (port 7860 is the HF Spaces default). The actual application runs on port 8000 everywhere else. A new production Dockerfile at the project root (`infra/docker/backend.Dockerfile`) avoids modifying the existing `backend/Dockerfile`.

**Alternatives considered**:
- Modify existing Dockerfile → REJECTED (violates FR-009, zero app changes)
- Override port in docker-compose only → REJECTED (inconsistent for Helm/K8s)

### R2: Frontend Dockerfile Missing

**Decision**: Create a new multi-stage Dockerfile for the Next.js frontend. Stage 1 builds with `npm run build`, stage 2 serves with `npm start`. The `NEXT_PUBLIC_API_URL` env var must be set at build time for Next.js static optimization.

**Rationale**: Next.js embeds `NEXT_PUBLIC_*` variables at build time. For Kubernetes, the backend service URL inside the cluster will differ from localhost. Using a build arg makes this configurable.

**Alternatives considered**:
- Runtime env injection → Complex for Next.js, requires custom entrypoint scripts
- Build-time arg (ARG + ENV) → Simple, standard pattern for Next.js containers

### R3: Docker Compose Strategy

**Decision**: Create a new production-ready `docker-compose.prod.yml` at the project root alongside the existing `docker-compose.yml`. The existing compose file uses volume mounts and `--reload` for development; the production version will use built images without volume mounts.

**Rationale**: The existing docker-compose.yml is dev-oriented (hot reload, volume mounts). A separate prod file avoids modifying the existing one and provides a proper staging environment before Kubernetes.

**Alternatives considered**:
- Modify existing docker-compose.yml → REJECTED (violates FR-009)
- Use docker-compose override files → Adds complexity, harder to understand

### R4: Helm Chart Structure

**Decision**: Single umbrella Helm chart `helm/hackathon-todo/` with sub-templates for backend, frontend, and PostgreSQL. One `values.yaml` controls all configuration.

**Rationale**: The application is a simple 3-service stack. Separate charts per service adds unnecessary complexity. A single chart with sub-templates keeps it minimal while allowing per-service configuration through values.

**Alternatives considered**:
- Three separate Helm charts → Over-engineered for a 3-service app
- Bitnami PostgreSQL subchart → Adds external dependency; simple StatefulSet sufficient for local dev

### R5: Minikube Image Loading

**Decision**: Use `minikube image load` to push locally-built Docker images into Minikube's internal registry. Set `imagePullPolicy: Never` in Helm values so Kubernetes uses the loaded images.

**Rationale**: This avoids needing a container registry. Images are built with `docker build`, then loaded into Minikube. Simple and self-contained for local development.

**Alternatives considered**:
- `eval $(minikube docker-env)` → Requires building in Minikube's Docker daemon; doesn't work with all drivers
- Private registry → Overkill for local dev

### R6: Service Exposure

**Decision**: Use `NodePort` service type for frontend and backend. Access via `minikube service <name>` or `kubectl port-forward`.

**Rationale**: NodePort is the simplest way to expose services in Minikube without an Ingress controller. Matches the spec's non-goal of "No Ingress controller configuration."

**Alternatives considered**:
- Ingress → Explicitly excluded in spec non-goals
- LoadBalancer → Requires `minikube tunnel`, adds a step
- ClusterIP + port-forward only → Less discoverable
