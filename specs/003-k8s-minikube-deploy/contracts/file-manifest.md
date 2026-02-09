# File Manifest: Infrastructure Files to Create

**Feature**: 003-k8s-minikube-deploy
**Date**: 2026-02-09

## Files to CREATE (new files only)

```text
hackathon_todo_II/
├── infra/
│   └── docker/
│       ├── backend.Dockerfile          # Production Dockerfile for FastAPI
│       └── frontend.Dockerfile         # Production Dockerfile for Next.js
├── docker-compose.prod.yml             # Production compose (no volume mounts)
├── helm/
│   └── hackathon-todo/
│       ├── Chart.yaml                  # Helm chart metadata
│       ├── values.yaml                 # Default configuration values
│       └── templates/
│           ├── _helpers.tpl            # Template helpers
│           ├── backend-deployment.yaml # Backend Deployment
│           ├── backend-service.yaml    # Backend Service (NodePort)
│           ├── frontend-deployment.yaml# Frontend Deployment
│           ├── frontend-service.yaml   # Frontend Service (NodePort)
│           ├── postgres-deployment.yaml# PostgreSQL Deployment
│           ├── postgres-service.yaml   # PostgreSQL Service (ClusterIP)
│           ├── postgres-pvc.yaml       # Persistent Volume Claim
│           ├── configmap.yaml          # Non-sensitive config
│           └── secret.yaml             # Sensitive credentials
└── docs/
    └── k8s-deployment-guide.md         # Step-by-step deployment instructions
```

## Files NOT modified (existing — zero changes)

- `backend/Dockerfile` — existing HF Spaces Dockerfile, untouched
- `docker-compose.yml` — existing dev compose, untouched
- `backend/**` — all application code untouched
- `frontend/**` — all application code untouched
- `.env.example` — untouched

## Contract: Each new file's responsibility

| File | Responsibility | Inputs | Outputs |
| ---- | -------------- | ------ | ------- |
| `infra/docker/backend.Dockerfile` | Build production backend image | `backend/` source + `requirements.txt` | Image `hackathon-todo-backend:latest` |
| `infra/docker/frontend.Dockerfile` | Build production frontend image | `frontend/` source + `package.json` | Image `hackathon-todo-frontend:latest` |
| `docker-compose.prod.yml` | Orchestrate 3 services for local testing | Built images + env vars | Running stack on ports 8000, 3000, 5432 |
| `helm/hackathon-todo/Chart.yaml` | Define chart name, version, metadata | N/A | Helm chart identity |
| `helm/hackathon-todo/values.yaml` | All configurable parameters | N/A | Default values for all templates |
| `helm/hackathon-todo/templates/*.yaml` | Kubernetes resource definitions | `values.yaml` | K8s manifests applied to cluster |
| `docs/k8s-deployment-guide.md` | Human-readable deployment steps | N/A | Step-by-step instructions |
