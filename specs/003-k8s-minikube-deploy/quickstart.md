# Quickstart: Kubernetes Deployment with Minikube

**Feature**: 003-k8s-minikube-deploy

## Prerequisites

- Docker Desktop (or Docker Engine + Docker Compose)
- Minikube v1.30+
- kubectl v1.27+
- Helm v3.12+

## Quick Deploy (5 commands)

```bash
# 1. Build production images
docker build -f infra/docker/backend.Dockerfile -t hackathon-todo-backend:latest ./backend
docker build -f infra/docker/frontend.Dockerfile -t hackathon-todo-frontend:latest --build-arg NEXT_PUBLIC_API_URL=http://localhost:8000 ./frontend

# 2. Start Minikube
minikube start --memory=4096 --cpus=2

# 3. Load images into Minikube
minikube image load hackathon-todo-backend:latest
minikube image load hackathon-todo-frontend:latest

# 4. Deploy with Helm
helm install hackathon-todo ./helm/hackathon-todo

# 5. Access the app
minikube service hackathon-todo-frontend --url
```

## Docker Compose Testing (before K8s)

```bash
# Build and run all services
docker compose -f docker-compose.prod.yml up --build

# Verify
curl http://localhost:8000/health
open http://localhost:3000
```

## Teardown

```bash
# Remove Helm release
helm uninstall hackathon-todo

# Stop Minikube
minikube stop

# (Optional) Delete Minikube cluster
minikube delete
```

## Verify Deployment

```bash
# Check all pods are running
kubectl get pods

# Check services
kubectl get svc

# View backend logs
kubectl logs -l app=backend

# View frontend logs
kubectl logs -l app=frontend
```
