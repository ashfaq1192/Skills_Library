# Dockerfile Patterns for GKE Deployment

Tested, production-ready Dockerfile patterns for Next.js and FastAPI.

---

## Frontend Dockerfile (Next.js — Multi-Stage with Build Args)

```dockerfile
# =============================================================================
# Stage 1: Dependencies
# =============================================================================
FROM node:22-alpine AS deps
WORKDIR /app
RUN apk add --no-cache libc6-compat
ENV NPM_CONFIG_FETCH_TIMEOUT=600000
COPY package.json package-lock.json* ./
RUN npm ci

# =============================================================================
# Stage 2: Builder — THIS IS WHERE BUILD ARGS MATTER
# =============================================================================
FROM node:22-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NEXT_TELEMETRY_DISABLED=1

# ┌─────────────────────────────────────────────────────────┐
# │ BUILD ARGS: These get baked into the JS bundle          │
# │ Pass via: docker build --build-arg NEXT_PUBLIC_API_URL= │
# └─────────────────────────────────────────────────────────┘
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

# Ensure standalone output mode for smaller images
RUN if ! grep -q "output.*standalone" next.config.js 2>/dev/null; then \
        sed -i 's/const nextConfig = {/const nextConfig = {\n  output: "standalone",/' next.config.js; \
    fi

RUN mkdir -p public
RUN npm run build

# =============================================================================
# Stage 3: Runner — Minimal production image
# =============================================================================
FROM node:22-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME="0.0.0.0"

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

CMD ["node", "server.js"]
```

### Key Points
- Build args MUST be in Stage 2 (builder), BEFORE `npm run build`
- `ARG` declares the variable, `ENV` makes it available to the build process
- Default values (localhost) make local development work without args
- Stage 3 (runner) doesn't need the build args — values are already in the JS bundle
- `--platform linux/amd64` is required in the build command for GKE

---

## Backend Dockerfile (FastAPI — Multi-Stage)

```dockerfile
# =============================================================================
# Stage 1: Builder
# =============================================================================
FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# =============================================================================
# Stage 2: Runner
# =============================================================================
FROM python:3.13-slim AS runner

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=8000

RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv

RUN groupadd -r appuser && useradd -r -g appuser -d /app appuser
WORKDIR /app
COPY --chown=appuser:appuser . .

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Key Points
- NO build args needed — all config is via runtime env vars
- `CORS_ORIGINS`, `DATABASE_URL`, etc. are read at startup from K8s Secrets
- To change config, just update K8s Secrets and restart pods (no rebuild)

---

## .dockerignore (Frontend)

Typical frontend `.dockerignore` that causes the `.env` pitfall:

```
node_modules/
.next/
.env              # <-- THIS blocks .env files!
.env.local
.env.development.local
.env.test.local
.env.production.local
__tests__/
e2e/
*.md
.git/
```

**Note**: `.env.production` (without `.local`) is usually NOT blocked.
But `--build-arg` is always the safer approach.

---

## Build Commands Reference

### Frontend (with GKE IPs)
```bash
docker build \
  --build-arg NEXT_PUBLIC_API_URL=http://<BACKEND_IP> \
  --build-arg NEXT_PUBLIC_BETTER_AUTH_URL=http://<FRONTEND_IP> \
  --build-arg BETTER_AUTH_URL=http://<FRONTEND_IP> \
  --build-arg NEXT_PUBLIC_CHATKIT_API_ENDPOINT=http://<BACKEND_IP>/api \
  --platform linux/amd64 \
  -t <USER>/todo-frontend:<VERSION> \
  -f phase-4-k8s/docker/frontend/Dockerfile \
  phase-3-chatbot/frontend
```

### Backend
```bash
docker build \
  --platform linux/amd64 \
  -t <USER>/todo-backend:<VERSION> \
  -f phase-4-k8s/docker/backend/Dockerfile \
  phase-3-chatbot/backend
```

### Push both
```bash
docker push <USER>/todo-frontend:<VERSION>
docker push <USER>/todo-backend:<VERSION>
```
