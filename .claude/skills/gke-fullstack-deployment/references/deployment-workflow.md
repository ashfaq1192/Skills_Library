# GKE Deployment Workflow — Complete Step-by-Step

This is the full deployment procedure from zero to a working app on GKE.

---

## Prerequisites

| Requirement | How to Verify |
|-------------|---------------|
| GKE cluster running | `gcloud container clusters list` |
| kubectl connected | `kubectl get nodes` |
| Docker installed locally | `docker --version` |
| Docker Hub login | `docker login` |
| gcloud CLI authenticated | `gcloud auth list` |

---

## Step 1: Prepare Kubernetes Namespace

```bash
kubectl create namespace todo-app --dry-run=client -o yaml | kubectl apply -f -
```

---

## Step 2: Deploy Initial Services (to get LoadBalancer IPs)

Create a `deploy.yaml` with frontend + backend deployments and LoadBalancer services.
Use any working image initially (even `nginx:latest` for frontend placeholder).

```bash
kubectl apply -f deploy.yaml
kubectl get svc -n todo-app --watch
```

Wait until both services show EXTERNAL-IP (can take 1-3 minutes):
```
NAME           TYPE           CLUSTER-IP     EXTERNAL-IP      PORT(S)
todo-frontend  LoadBalancer   10.x.x.x       34.44.146.146    80:xxxxx/TCP
todo-backend   LoadBalancer   10.x.x.x       34.57.215.48     80:xxxxx/TCP
```

**Record these IPs.** You need them for the frontend build.

---

## Step 3: Build Frontend Image (Local Machine)

### 3a. Ensure Dockerfile has build args

In the builder stage of the frontend Dockerfile, BEFORE `npm run build`:

```dockerfile
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ARG NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
ARG BETTER_AUTH_URL=http://localhost:3000
ARG NEXT_PUBLIC_CHATKIT_API_ENDPOINT=http://localhost:8000/api
ARG NEXT_PUBLIC_VOICE_INPUT_ENABLED=true

ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL \
    NEXT_PUBLIC_BETTER_AUTH_URL=$NEXT_PUBLIC_BETTER_AUTH_URL \
    BETTER_AUTH_URL=$BETTER_AUTH_URL \
    NEXT_PUBLIC_CHATKIT_API_ENDPOINT=$NEXT_PUBLIC_CHATKIT_API_ENDPOINT \
    NEXT_PUBLIC_VOICE_INPUT_ENABLED=$NEXT_PUBLIC_VOICE_INPUT_ENABLED
```

### 3b. Build with LoadBalancer IPs

```bash
docker build \
  --build-arg NEXT_PUBLIC_API_URL=http://<BACKEND_LB_IP> \
  --build-arg NEXT_PUBLIC_BETTER_AUTH_URL=http://<FRONTEND_LB_IP> \
  --build-arg BETTER_AUTH_URL=http://<FRONTEND_LB_IP> \
  --build-arg NEXT_PUBLIC_CHATKIT_API_ENDPOINT=http://<BACKEND_LB_IP>/api \
  --platform linux/amd64 \
  -t <DOCKER_USER>/todo-frontend:<VERSION> \
  -f <DOCKERFILE_PATH> \
  <FRONTEND_SOURCE_DIR>
```

**Real example from our deployment:**
```bash
docker build \
  --build-arg NEXT_PUBLIC_API_URL=http://34.57.215.48 \
  --build-arg NEXT_PUBLIC_BETTER_AUTH_URL=http://34.44.146.146 \
  --build-arg BETTER_AUTH_URL=http://34.44.146.146 \
  --build-arg NEXT_PUBLIC_CHATKIT_API_ENDPOINT=http://34.57.215.48/api \
  --platform linux/amd64 \
  -t ashfaq1192/todo-frontend:v4 \
  -f phase-4-k8s/docker/frontend/Dockerfile \
  phase-3-chatbot/frontend
```

### 3c. Push to Docker Hub

```bash
docker push <DOCKER_USER>/todo-frontend:<VERSION>
```

---

## Step 4: Build Backend Image (if needed)

The backend reads env vars at runtime, so it rarely needs rebuilding for config changes.
Only rebuild if code changed.

```bash
docker build \
  --platform linux/amd64 \
  -t <DOCKER_USER>/todo-backend:<VERSION> \
  -f <DOCKERFILE_PATH> \
  <BACKEND_SOURCE_DIR>

docker push <DOCKER_USER>/todo-backend:<VERSION>
```

---

## Step 5: Create Kubernetes Secrets (Cloud Shell)

```bash
# Set your real values
export REAL_DB_URL="postgresql://user:pass@host/db?sslmode=require"
export JWT_SECRET="your-jwt-secret-key"
export BETTER_AUTH="your-better-auth-secret"
export GEMINI_KEY="your-gemini-api-key"
export FRONTEND_IP="http://<FRONTEND_LB_IP>"
export BACKEND_IP="http://<BACKEND_LB_IP>"

# Delete old secret and create new one
kubectl delete secret project-secrets --namespace=todo-app --ignore-not-found=true

kubectl create secret generic project-secrets \
  --namespace=todo-app \
  --from-literal=DATABASE_URL="${REAL_DB_URL}" \
  --from-literal=JWT_SECRET_KEY="${JWT_SECRET}" \
  --from-literal=GEMINI_API_KEY="${GEMINI_KEY}" \
  --from-literal=GEMINI_MODEL="gemini-2.5-flash" \
  --from-literal=GEMINI_BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai/" \
  --from-literal=CORS_ORIGINS="${FRONTEND_IP},http://localhost:3000" \
  --from-literal=BETTER_AUTH_SECRET="${BETTER_AUTH}" \
  --from-literal=BETTER_AUTH_URL="${FRONTEND_IP}" \
  --from-literal=NEXT_PUBLIC_BETTER_AUTH_URL="${FRONTEND_IP}" \
  --from-literal=NEXT_PUBLIC_API_URL="${BACKEND_IP}" \
  --from-literal=DAPR_ENABLED="false"
```

---

## Step 6: Update deploy.yaml with New Image Version

```yaml
# In deploy.yaml, update the frontend container image:
containers:
- name: frontend
  image: ashfaq1192/todo-frontend:v4   # <- Update version here
```

```bash
kubectl apply -f deploy.yaml
```

---

## Step 7: Restart Pods

```bash
kubectl delete pods --all --namespace=todo-app
```

Or more targeted:
```bash
kubectl rollout restart deployment/todo-frontend -n todo-app
kubectl rollout restart deployment/todo-backend -n todo-app
```

---

## Step 8: Verify

```bash
# Check pods are running
kubectl get pods -n todo-app

# Check logs for errors
kubectl logs -l app=todo-frontend -n todo-app
kubectl logs -l app=todo-backend -n todo-app

# Test backend health
curl http://<BACKEND_LB_IP>/health
```

Then open `http://<FRONTEND_LB_IP>` in browser and test login + task creation.

---

## Environment Variable Reference

### Build-Time Variables (Frontend — passed via --build-arg)

| Variable | Value | Purpose |
|----------|-------|---------|
| `NEXT_PUBLIC_API_URL` | `http://<BACKEND_LB_IP>` | Browser → Backend API calls |
| `NEXT_PUBLIC_BETTER_AUTH_URL` | `http://<FRONTEND_LB_IP>` | Auth redirect URLs |
| `BETTER_AUTH_URL` | `http://<FRONTEND_LB_IP>` | Server-side auth URL |
| `NEXT_PUBLIC_CHATKIT_API_ENDPOINT` | `http://<BACKEND_LB_IP>/api` | ChatKit endpoint |

### Runtime Variables (Both — passed via K8s Secrets)

| Variable | Used By | Purpose |
|----------|---------|---------|
| `DATABASE_URL` | Both | Neon PostgreSQL connection |
| `JWT_SECRET_KEY` | Both | Token signing (MUST match) |
| `BETTER_AUTH_SECRET` | Frontend | Session signing |
| `CORS_ORIGINS` | Backend | Allowed frontend origins |
| `GEMINI_API_KEY` | Backend | AI chatbot API |
| `GEMINI_MODEL` | Backend | Model version |
