---
name: gke-fullstack-deployment
description: |
  Deploy full-stack applications (Next.js frontend + FastAPI backend) to Google
  Kubernetes Engine (GKE). This skill should be used when building Docker images
  for cloud deployment, configuring Kubernetes secrets and LoadBalancers, fixing
  "failed to fetch" errors from localhost URLs baked into production images, or
  setting up CORS between frontend and backend services on GKE.
---

# GKE Full-Stack Deployment

Deploy Next.js + FastAPI applications to GKE with correct environment configuration,
Docker build strategies, and Kubernetes resource management.

## What This Skill Does

- Guide Docker image builds with correct environment variable injection
- Configure Kubernetes secrets, ConfigMaps, and LoadBalancer services
- Set up CORS between frontend and backend on separate LoadBalancer IPs
- Diagnose and fix common deployment failures (localhost URLs, .dockerignore blocks, auth errors)

## What This Skill Does NOT Do

- Provision GKE clusters (use `gcloud` or Terraform separately)
- Handle CI/CD pipeline setup (GitHub Actions, Cloud Build)
- Manage DNS or TLS certificates
- Configure Dapr or Kafka (see separate skills)

---

## Before Implementation

Gather context to ensure successful deployment:

| Source | Gather |
|--------|--------|
| **Codebase** | Dockerfile locations, .dockerignore contents, next.config.js, backend CORS config |
| **Conversation** | LoadBalancer IPs, Docker Hub repo, image version, namespace |
| **Skill References** | Pitfalls from `references/pitfalls.md`, workflow from `references/deployment-workflow.md` |
| **User Guidelines** | Secret values (DB URL, API keys, JWT secrets) - never hardcode |

Only ask user for THEIR specific values (IPs, secrets, repo names).
Domain expertise on Docker/K8s/Next.js pitfalls is embedded in this skill.

---

## Critical Knowledge: Why "Failed to Fetch" Happens

Next.js `NEXT_PUBLIC_*` variables are **baked into the JavaScript bundle at build time**.
They are NOT read from environment variables at runtime. This is the #1 deployment failure.

```
Build time (docker build)          Runtime (K8s pod)
========================          ==================
NEXT_PUBLIC_API_URL=???  ──────►  JS bundle says: fetch("???/api/tasks")
                                  Browser executes this LITERALLY
```

If `NEXT_PUBLIC_API_URL` is unset or `localhost` during build, the browser will try
`fetch("http://localhost:8000/api/tasks")` in production. This causes "Failed to fetch".

**The fix**: Pass correct URLs via `--build-arg` at Docker build time. See workflow below.

---

## Deployment Workflow

### Phase 1: Get LoadBalancer IPs

Before building images, deploy placeholder services to get IPs:

```bash
# Deploy backend + frontend with LoadBalancer services
kubectl apply -f deploy.yaml
kubectl get svc -n todo-app --watch
# Wait until EXTERNAL-IP changes from <pending> to an actual IP
```

Record the IPs:
- **Frontend LB IP**: e.g., `34.44.146.146`
- **Backend LB IP**: e.g., `34.57.215.48`

### Phase 2: Build Frontend Image (Local Machine)

**IMPORTANT**: Use `--build-arg`, NOT `.env` files (`.dockerignore` blocks them).

```bash
docker build \
  --build-arg NEXT_PUBLIC_API_URL=http://<BACKEND_LB_IP> \
  --build-arg NEXT_PUBLIC_BETTER_AUTH_URL=http://<FRONTEND_LB_IP> \
  --build-arg BETTER_AUTH_URL=http://<FRONTEND_LB_IP> \
  --build-arg NEXT_PUBLIC_CHATKIT_API_ENDPOINT=http://<BACKEND_LB_IP>/api \
  --platform linux/amd64 \
  -t <DOCKER_HUB_USER>/todo-frontend:<VERSION> \
  -f <PATH_TO_DOCKERFILE> \
  <FRONTEND_SOURCE_DIR>
```

Then push:
```bash
docker push <DOCKER_HUB_USER>/todo-frontend:<VERSION>
```

### Phase 3: Create/Update Kubernetes Secrets (Cloud Shell)

```bash
kubectl delete secret project-secrets --namespace=todo-app --ignore-not-found=true

kubectl create secret generic project-secrets \
  --namespace=todo-app \
  --from-literal=DATABASE_URL="${REAL_DB_URL}" \
  --from-literal=JWT_SECRET_KEY="${JWT_SECRET}" \
  --from-literal=GEMINI_API_KEY="${GEMINI_KEY}" \
  --from-literal=CORS_ORIGINS="http://<FRONTEND_LB_IP>,http://localhost:3000" \
  --from-literal=BETTER_AUTH_SECRET="${BETTER_AUTH}" \
  --from-literal=BETTER_AUTH_URL="http://<FRONTEND_LB_IP>" \
  --from-literal=NEXT_PUBLIC_BETTER_AUTH_URL="http://<FRONTEND_LB_IP>" \
  --from-literal=NEXT_PUBLIC_API_URL="http://<BACKEND_LB_IP>"
```

### Phase 4: Update Deployment and Restart

```bash
# Update image version in deploy.yaml, then:
kubectl apply -f deploy.yaml

# Force pod restart to pick up new secrets + image
kubectl delete pods --all --namespace=todo-app

# Verify rollout
kubectl get pods -n todo-app --watch
```

### Phase 5: Verify

1. Open `http://<FRONTEND_LB_IP>` in browser
2. Test login/signup
3. Create a task to verify backend connectivity
4. Check browser DevTools Network tab for any failed requests

---

## Dockerfile Requirements

The frontend Dockerfile MUST have build args in the **builder stage** (before `npm run build`):

```dockerfile
# In the builder stage, BEFORE npm run build:
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ARG NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
ARG BETTER_AUTH_URL=http://localhost:3000
ARG NEXT_PUBLIC_CHATKIT_API_ENDPOINT=http://localhost:8000/api

ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL \
    NEXT_PUBLIC_BETTER_AUTH_URL=$NEXT_PUBLIC_BETTER_AUTH_URL \
    BETTER_AUTH_URL=$BETTER_AUTH_URL \
    NEXT_PUBLIC_CHATKIT_API_ENDPOINT=$NEXT_PUBLIC_CHATKIT_API_ENDPOINT
```

The backend Dockerfile needs NO changes - it reads env vars at runtime from K8s secrets.

---

## Quick Checklist

Before deploying, verify:

- [ ] Frontend Dockerfile has `ARG` + `ENV` for all `NEXT_PUBLIC_*` vars
- [ ] `.dockerignore` is checked (it likely blocks `.env` files)
- [ ] `--build-arg` flags used in `docker build` with correct LB IPs
- [ ] `--platform linux/amd64` used (GKE nodes are x86_64)
- [ ] Backend `CORS_ORIGINS` includes the frontend LB IP
- [ ] `BETTER_AUTH_URL` points to frontend LB IP (not localhost)
- [ ] `BETTER_AUTH_SECRET` / `AUTH_SECRET` is set (auth will 500 without it)
- [ ] Docker image pushed to registry before updating K8s deployment
- [ ] Secrets verified non-empty after creation (see pitfall below)

## Critical Pitfall: Empty Kubernetes Secrets

API keys with special characters (e.g., `sk-proj-...` with dashes) can cause
`kubectl create secret --from-literal` to silently create **empty** secrets
when passed inline. Always use `source .env` + variable reference:

```bash
# BAD - may create empty secret due to shell escaping
kubectl create secret generic my-secret \
  --from-literal=API_KEY="sk-proj-qJUk..." -n my-namespace

# GOOD - source .env first, then reference the variable
source .env
kubectl create secret generic my-secret \
  --from-literal=API_KEY="$OPENAI_API_KEY" \
  --dry-run=client -o yaml | kubectl apply -f -

# ALWAYS VERIFY - check the secret is not empty
kubectl get secret my-secret -n my-namespace \
  -o jsonpath='{.data.API_KEY}' | base64 -d | wc -c
```

Symptoms of empty secrets: services start but return 401/500 when calling
external APIs (e.g., OpenAI "You didn't provide an API key"), or Better Auth
throws `BetterAuthError: You are using the default secret`.

---

## Reference Files

| File | When to Read |
|------|--------------|
| `references/pitfalls.md` | Before ANY deployment - common mistakes and fixes |
| `references/deployment-workflow.md` | Step-by-step deployment with detailed commands |
| `references/dockerfile-patterns.md` | Frontend/backend Dockerfile templates with build args |
| `references/troubleshooting.md` | When something goes wrong after deployment |
| `assets/deploy-template.yaml` | Starter K8s deployment manifest |
