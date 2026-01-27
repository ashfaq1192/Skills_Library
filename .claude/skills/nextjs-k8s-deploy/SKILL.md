---
name: nextjs-k8s-deploy
description: |
  Deploy Next.js applications with Monaco Editor to Kubernetes. This skill should be
  used when deploying frontend applications, containerizing Next.js apps, or setting
  up client-side applications with code editing capabilities on Kubernetes clusters.
---

# Next.js Kubernetes Deployment

Deploy Next.js frontend with Monaco Editor integration to Kubernetes.

## When to Use

- Deploy Next.js application to Kubernetes
- Containerize frontend with Monaco code editor
- Set up production Next.js deployment
- Configure ingress for frontend access

## Prerequisites

- Node.js 18+ installed:
  ```bash
  node --version  # Should be v18 or higher
  ```
- Docker installed (for containerization)
- `kubectl` access for K8s deployment
- Next.js project ready for deployment

## Before Implementation

Gather context for Next.js deployment:

| Source | Gather |
|--------|--------|
| **Project** | Next.js project location, build configuration, environment variables |
| **User** | Domain name for access, replica count, resource requirements |
| **Cluster** | Target namespace, ingress controller available, storage needs |

## Required Clarifications

1. **Next.js Project**: Where is your Next.js project?
   - Path to project directory
   - Verify package.json exists

2. **Build Configuration**: Is your Next.js configured for standalone output?
   - Check next.config.js for `output: 'standalone'`
   - If not present: Add it for optimal Docker builds

3. **Environment Variables**: What environment variables does your app need?
   - API URLs (e.g., `NEXT_PUBLIC_API_URL`)
   - Feature flags
   - Analytics keys (optional)

4. **Deployment Settings**: How should the application be deployed?
   - Namespace (default: learnflow)
   - Replicas (default: 3 for high availability)
   - Domain name (optional, for Ingress)

## Instructions

### 1. Build Production Next.js
```bash
python scripts/build_nextjs.py --project-dir <path> --output-dir ./build
```

### 2. Create Docker Image
```bash
python scripts/containerize.py --project-dir <path> --tag learnflow-frontend:v1.0.0
```

### 3. Generate K8s Manifests
```bash
python scripts/generate_manifests.py --image <image-tag> --namespace learnflow
```

### 4. Deploy to Cluster
```bash
python scripts/deploy_frontend.py --namespace learnflow --domain app.learnflow.com
```

## Validation

- [ ] Next.js builds successfully
- [ ] Docker image created
- [ ] Pods running in K8s
- [ ] Frontend accessible via ingress
- [ ] Monaco Editor loads correctly

## Troubleshooting

- **Build fails**: Check Node.js version, verify dependencies installed
- **Docker build timeout**: Increase timeout, check network connectivity
- **Pods CrashLoopBackOff**: Check environment variables, review logs
- **404 on routes**: Verify standalone output configured in next.config.js

## Official Documentation

- Next.js: https://nextjs.org/docs
- Next.js Deployment: https://nextjs.org/docs/deployment
- Monaco Editor: https://microsoft.github.io/monaco-editor/
