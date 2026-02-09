# Data Model: Kubernetes Deployment with Minikube

**Feature**: 003-k8s-minikube-deploy
**Date**: 2026-02-09

## Overview

This feature introduces no new application data entities. All data models (User, Task, Conversation, Message) remain unchanged. This document describes the **infrastructure entities** — the Kubernetes resources and configuration objects that define the deployment topology.

## Infrastructure Entities

### Container Image

| Attribute      | Description                                    |
| -------------- | ---------------------------------------------- |
| Name           | Image tag (e.g., `hackathon-todo-backend:latest`) |
| Base           | Python 3.11-slim (backend), Node 18-alpine (frontend) |
| Ports exposed  | 8000 (backend), 3000 (frontend)               |
| Build context  | `./backend` or `./frontend`                   |

### Kubernetes Deployment

| Attribute        | Description                                  |
| ---------------- | -------------------------------------------- |
| Name             | `backend`, `frontend`, `postgres`            |
| Replicas         | 1 (all services, sufficient for local dev)   |
| Image            | References locally built container image     |
| Resource requests| CPU: 100m, Memory: 128Mi (backend/frontend)  |
| Resource limits  | CPU: 500m, Memory: 512Mi (backend/frontend)  |
| Probes           | Liveness + readiness on health endpoints     |

### Kubernetes Service

| Attribute   | Description                                       |
| ----------- | ------------------------------------------------- |
| Name        | `backend-svc`, `frontend-svc`, `postgres-svc`    |
| Type        | NodePort (frontend, backend), ClusterIP (postgres) |
| Target port | 8000 (backend), 3000 (frontend), 5432 (postgres)  |

### Kubernetes Secret

| Attribute | Description                                         |
| --------- | --------------------------------------------------- |
| Name      | `hackathon-todo-secrets`                            |
| Keys      | DATABASE_URL, SECRET_KEY, OPENAI_API_KEY            |
| Encoding  | Base64 (standard K8s secret encoding)               |

### Kubernetes ConfigMap

| Attribute | Description                                         |
| --------- | --------------------------------------------------- |
| Name      | `hackathon-todo-config`                             |
| Keys      | ENVIRONMENT, MODEL, CORS_ORIGINS, LOG_LEVEL, etc.   |

## Relationships

```
ConfigMap ──► Backend Deployment (env vars)
Secret ──────► Backend Deployment (sensitive env vars)
                    │
                    ▼
              Backend Service (NodePort :8000)
                    │
PostgreSQL ◄────────┘ (DATABASE_URL connection)
Deployment
    │
    ▼
PostgreSQL Service (ClusterIP :5432)

ConfigMap ──► Frontend Deployment (NEXT_PUBLIC_API_URL)
                    │
                    ▼
              Frontend Service (NodePort :3000)
                    │
                    └──► Backend Service (via NEXT_PUBLIC_API_URL)
```

## No Schema Changes

This feature adds zero database schema changes. The PostgreSQL instance in Kubernetes runs the same schema as the local development database, initialized by `SQLModel.metadata.create_all()` on backend startup.
