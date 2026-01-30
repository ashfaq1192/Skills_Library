# Next.js Kubernetes Deployment - Reference Documentation

**Version**: 1.0.0
**Created**: 2026-01-27
**Purpose**: Deploy Next.js applications with Monaco Editor to Kubernetes

## Overview

The `nextjs-k8s-deploy` skill handles the full lifecycle of deploying a Next.js frontend application to Kubernetes: building for production, containerizing with Docker, generating Kubernetes manifests, and deploying to a cluster. Designed for the LearnFlow frontend with Monaco Editor integration.

### Key Features

- **Production Build**: Optimized Next.js standalone output
- **Multi-Stage Docker**: Minimal image size with node:18-alpine
- **K8s Manifests**: Deployment, Service, and optional Ingress
- **Health Probes**: Liveness and readiness checks configured
- **Monaco Integration**: Browser-based code editor support
- **Cross-Agent Compatible**: Works with both Claude Code and Goose

## Architecture

```
Build Pipeline:
  Next.js Source → npm build → Docker Image → K8s Deployment

Kubernetes Layout:
  ┌─────────────────────────────────────────┐
  │  Namespace: learnflow                   │
  │                                         │
  │  ┌─────────┐  ┌─────────┐  ┌─────────┐ │
  │  │ Pod 1   │  │ Pod 2   │  │ Pod 3   │ │
  │  │ Next.js │  │ Next.js │  │ Next.js │ │
  │  │ :3000   │  │ :3000   │  │ :3000   │ │
  │  └────┬────┘  └────┬────┘  └────┬────┘ │
  │       └────────────┼────────────┘      │
  │              ┌─────▼──────┐            │
  │              │  Service   │            │
  │              │  :80→:3000 │            │
  │              └─────┬──────┘            │
  │              ┌─────▼──────┐            │
  │              │  Ingress   │ (optional) │
  │              │  domain    │            │
  │              └────────────┘            │
  └─────────────────────────────────────────┘
```

## Components

### 1. build_nextjs.py

Builds Next.js application for production.

```bash
python scripts/build_nextjs.py [OPTIONS]

Options:
  --project-dir TEXT    Next.js project directory (required)
  --output-dir TEXT     Ignored (build goes to .next)

Exit Codes:
  0 - Build successful
  1 - Missing package.json, build failure
```

**What It Does:**
1. Validates project directory and package.json
2. Installs dependencies if `node_modules` missing
3. Runs `npm run build`
4. Verifies `.next` directory created
5. Reports file count

### 2. containerize.py

Creates Docker image with multi-stage build.

```bash
python scripts/containerize.py [OPTIONS]

Options:
  --project-dir TEXT    Next.js project directory (required)
  --tag TEXT            Docker image tag (required)

Exit Codes:
  0 - Image built
  1 - Docker not available, build failure
```

**Dockerfile Template (Embedded):**
```dockerfile
FROM node:18-alpine AS base

# Dependencies stage
FROM base AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Build stage
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Production stage
FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
USER nextjs
EXPOSE 3000
CMD ["node", "server.js"]
```

**Requirements:**
- `next.config.js` must include `output: 'standalone'`
- If missing, the script warns but continues

### 3. generate_manifests.py

Generates Kubernetes deployment manifests.

```bash
python scripts/generate_manifests.py [OPTIONS]

Options:
  --image TEXT        Docker image tag (required)
  --namespace TEXT    Target namespace (required)
  --domain TEXT      Domain for Ingress (optional)
  --output TEXT      Output directory (default: ./k8s-manifests)

Exit Codes:
  0 - Manifests generated
  1 - Error writing files
```

**Generated Files:**

| File | Resource | Configuration |
|------|----------|---------------|
| deployment.yaml | Deployment | 3 replicas, resource limits, health probes |
| service.yaml | Service | ClusterIP, port 80 -> 3000 |
| ingress.yaml | Ingress | NGINX rules (only if --domain provided) |

**Deployment Configuration:**
- Replicas: 3
- CPU: 100m request / 500m limit
- Memory: 128Mi request / 512Mi limit
- Liveness probe: GET / on port 3000 (period 30s)
- Readiness probe: GET / on port 3000 (period 10s)

### 4. deploy_frontend.py

Deploys to Kubernetes cluster.

```bash
python scripts/deploy_frontend.py [OPTIONS]

Options:
  --namespace TEXT        Target namespace (required)
  --manifests-dir TEXT   Manifests directory (default: ./k8s-manifests)
  --domain TEXT          Domain for access instructions (optional)

Exit Codes:
  0 - Deployment successful
  1 - kubectl not available, namespace error
```

**What It Does:**
1. Creates namespace if needed
2. Applies all YAML files from manifests directory
3. Waits for pod scheduling
4. Reports pod status
5. Provides access instructions

## Usage

### Full Pipeline

```bash
cd /path/to/learnflow-app

# 1. Build
python .claude/skills/nextjs-k8s-deploy/scripts/build_nextjs.py \
  --project-dir src/frontend

# 2. Containerize (use Minikube's Docker)
eval $(minikube docker-env)
python .claude/skills/nextjs-k8s-deploy/scripts/containerize.py \
  --project-dir src/frontend \
  --tag learnflow-frontend:v1.0.0

# 3. Generate manifests
python .claude/skills/nextjs-k8s-deploy/scripts/generate_manifests.py \
  --image learnflow-frontend:v1.0.0 \
  --namespace learnflow

# 4. Deploy
python .claude/skills/nextjs-k8s-deploy/scripts/deploy_frontend.py \
  --namespace learnflow
```

### With Claude Code or Goose

```bash
"Use nextjs-k8s-deploy to build and deploy the LearnFlow frontend"
```

### Accessing the Frontend

```bash
# Port-forward for local access
kubectl port-forward -n learnflow svc/learnflow-frontend 3000:80

# Open: http://localhost:3000
```

## Monaco Editor Integration

The LearnFlow frontend uses Monaco Editor for the code editor component:

```tsx
// src/components/CodeEditor.tsx
import dynamic from 'next/dynamic';

const MonacoEditor = dynamic(() => import('@monaco-editor/react'), {
  ssr: false,
  loading: () => <div>Loading editor...</div>
});

export default function CodeEditor({ value, onChange }) {
  return (
    <MonacoEditor
      height="400px"
      language="python"
      theme="vs-dark"
      value={value}
      onChange={onChange}
      options={{
        minimap: { enabled: false },
        fontSize: 14,
        automaticLayout: true,
      }}
    />
  );
}
```

**Dependencies:**
```bash
npm install @monaco-editor/react monaco-editor
```

## Troubleshooting

### Build Fails

```bash
# Check Node version
node --version  # Need v18+

# Clear cache and rebuild
rm -rf .next node_modules
npm install
npm run build
```

### Docker Build Timeout

```bash
# Increase Docker timeout
export DOCKER_BUILDKIT=1
docker build --progress=plain -t my-image .
```

### Pods CrashLoopBackOff

```bash
# Check logs
kubectl logs -n learnflow <pod-name>

# Common causes:
# 1. Missing standalone output: Add output: 'standalone' to next.config.js
# 2. Missing env vars: Check .env.local.template
# 3. Port mismatch: Ensure EXPOSE 3000 matches app
```

### ImagePullBackOff on Minikube

```bash
# Load image into Minikube
eval $(minikube docker-env)
docker build -t learnflow-frontend:latest src/frontend/

# Set imagePullPolicy: Never in deployment.yaml
```

### Monaco Editor Not Loading

```bash
# Ensure dynamic import with ssr: false
# Check browser console for chunk loading errors
# Verify public directory has Monaco assets
```

## Dependencies

| Dependency | Version | Purpose |
|-----------|---------|---------|
| Node.js | 18+ | Build runtime |
| npm | 9+ | Package manager |
| Docker | 20+ | Containerization |
| kubectl | 1.24+ | Kubernetes deployment |
| Next.js | 14+ | Framework |
| Monaco Editor | Latest | Code editor |

## References

- [Next.js Documentation](https://nextjs.org/docs)
- [Next.js Standalone Output](https://nextjs.org/docs/pages/api-reference/next-config-js/output)
- [Monaco Editor React](https://github.com/suren-atoyan/monaco-react)
- [Kubernetes Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
