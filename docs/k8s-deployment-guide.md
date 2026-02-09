# Kubernetes Deployment Guide

Deploy the Hackathon Todo + AI Chatbot application to a local Kubernetes cluster using Minikube and Helm.

## Prerequisites

| Tool | Minimum Version | Install Guide |
| ---- | --------------- | ------------- |
| Docker | 20.10+ | https://docs.docker.com/get-docker/ |
| Minikube | v1.30+ | https://minikube.sigs.k8s.io/docs/start/ |
| kubectl | v1.27+ | https://kubernetes.io/docs/tasks/tools/ |
| Helm | v3.12+ | https://helm.sh/docs/intro/install/ |

**Minikube resources**: At least 4 GB RAM and 2 CPUs (Minikube defaults).

## 1. Build Docker Images

From the project root directory:

```bash
# Build backend image
docker build -f infra/docker/backend.Dockerfile -t hackathon-todo-backend:latest ./backend

# Build frontend image
docker build -f infra/docker/frontend.Dockerfile \
  -t hackathon-todo-frontend:latest \
  --build-arg NEXT_PUBLIC_API_URL=http://localhost:8000 \
  ./frontend
```

Verify images were built:

```bash
docker images | grep hackathon-todo
```

## 2. Test with Docker Compose (Optional)

Before deploying to Kubernetes, verify containers work locally:

```bash
# Start all services
docker compose -f docker-compose.prod.yml up --build

# In another terminal, verify:
curl http://localhost:8000/health
# Expected: {"status":"healthy","message":"Backend is running"}

# Open browser to http://localhost:3000
# Expected: App loads with login page

# Stop when done
docker compose -f docker-compose.prod.yml down
```

## 3. Start Minikube

```bash
# Start cluster with recommended resources
minikube start --memory=4096 --cpus=2

# Verify cluster is running
kubectl cluster-info
```

## 4. Load Images into Minikube

Minikube has its own Docker daemon. Load your locally-built images into it:

```bash
minikube image load hackathon-todo-backend:latest
minikube image load hackathon-todo-frontend:latest
```

This can take a few minutes depending on image size.

Verify images are loaded:

```bash
minikube image list | grep hackathon-todo
```

## 5. Deploy with Helm

```bash
# Install the Helm chart
helm install hackathon-todo ./helm/hackathon-todo

# Watch pods start up
kubectl get pods -w
```

Wait until all pods show `Running` status and `READY 1/1`.

## 6. Verify Deployment

```bash
# Check all pods are running
kubectl get pods

# Expected output:
# NAME                                          READY   STATUS    RESTARTS   AGE
# hackathon-todo-backend-xxx                    1/1     Running   0          1m
# hackathon-todo-frontend-xxx                   1/1     Running   0          1m
# hackathon-todo-postgres-xxx                   1/1     Running   0          1m

# Check services
kubectl get svc

# Check pod logs
kubectl logs -l app=backend
kubectl logs -l app=frontend
kubectl logs -l app=postgres
```

## 7. Access the Application

### Option A: minikube service (recommended)

```bash
# Open frontend in browser
minikube service hackathon-todo-frontend --url

# Open backend API
minikube service hackathon-todo-backend --url
```

### Option B: kubectl port-forward

```bash
# Forward frontend
kubectl port-forward svc/hackathon-todo-frontend 3000:3000 &

# Forward backend
kubectl port-forward svc/hackathon-todo-backend 8000:8000 &

# Access at http://localhost:3000 (frontend) and http://localhost:8000 (backend)
```

## 8. Troubleshooting

### Pod stuck in ImagePullBackOff

The images were not loaded into Minikube. Fix:

```bash
minikube image load hackathon-todo-backend:latest
minikube image load hackathon-todo-frontend:latest
kubectl delete pods --all
```

Verify `imagePullPolicy: Never` is set in `values.yaml` for backend and frontend.

### Pod stuck in CrashLoopBackOff

Check logs for the failing pod:

```bash
kubectl logs <pod-name> --previous
kubectl describe pod <pod-name>
```

Common causes:
- **Backend**: Missing environment variables (DATABASE_URL, SECRET_KEY). Check Secret and ConfigMap.
- **Frontend**: Build failed. Rebuild the Docker image.
- **PostgreSQL**: PVC issues. Delete PVC and re-deploy.

### Backend can't connect to PostgreSQL

Verify the PostgreSQL service is running and the DATABASE_URL matches:

```bash
kubectl get svc hackathon-todo-postgres
kubectl exec -it <backend-pod> -- env | grep DATABASE_URL
```

The DATABASE_URL should point to `hackathon-todo-postgres:5432`.

### Port conflicts

If ports 3000, 5432, or 8000 are already in use on your host:

- Use `kubectl port-forward` with different local ports:
  ```bash
  kubectl port-forward svc/hackathon-todo-frontend 3001:3000
  ```
- Or use `minikube service` which assigns random available ports.

### Resource limits

If Minikube is slow or pods are being OOMKilled:

```bash
# Increase Minikube resources
minikube stop
minikube start --memory=8192 --cpus=4

# Or reduce resource limits in values.yaml
```

## 9. Teardown

```bash
# Remove the Helm release
helm uninstall hackathon-todo

# Verify all resources are cleaned up
kubectl get all

# Stop Minikube
minikube stop

# (Optional) Delete the Minikube cluster entirely
minikube delete
```

## 10. Configuration Reference

All configuration is managed through `helm/hackathon-todo/values.yaml`:

| Parameter | Default | Description |
| --------- | ------- | ----------- |
| `backend.image` | `hackathon-todo-backend:latest` | Backend Docker image |
| `backend.imagePullPolicy` | `Never` | Use locally loaded images |
| `backend.port` | `8000` | Backend container port |
| `backend.replicas` | `1` | Number of backend pods |
| `frontend.image` | `hackathon-todo-frontend:latest` | Frontend Docker image |
| `frontend.imagePullPolicy` | `Never` | Use locally loaded images |
| `frontend.port` | `3000` | Frontend container port |
| `frontend.replicas` | `1` | Number of frontend pods |
| `postgres.image` | `postgres:16-alpine` | PostgreSQL Docker image |
| `postgres.port` | `5432` | PostgreSQL container port |
| `postgres.storage` | `1Gi` | Persistent volume size |
| `config.databaseUrl` | `postgresql://...` | Database connection string |
| `config.secretKey` | `your-secret-key...` | JWT signing key |
| `config.openaiBaseUrl` | `https://openrouter.ai/api/v1` | AI API endpoint |
| `config.model` | `mistralai/mistral-7b-instruct` | AI model name |
| `config.environment` | `development` | App environment |
| `config.nextPublicApiUrl` | `http://hackathon-todo-backend:8000` | Backend URL for frontend |
| `secrets.openaiApiKey` | `""` | OpenRouter API key |
| `secrets.postgresPassword` | `postgres` | PostgreSQL password |

Override values during install:

```bash
helm install hackathon-todo ./helm/hackathon-todo \
  --set secrets.openaiApiKey="your-api-key" \
  --set config.secretKey="your-production-secret"
```
