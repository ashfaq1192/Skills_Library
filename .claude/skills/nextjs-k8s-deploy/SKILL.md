---
name: nextjs-k8s-deploy
description: Deploy Next.js with Monaco Editor to Kubernetes
version: 1.0.0
---

# Next.js Kubernetes Deployment

## When to Use
- Deploy Next.js frontend to Kubernetes
- Containerize frontend with Monaco code editor

## Prerequisites
- Node.js 18+ (`node --version`)
- Docker installed
- kubectl configured

## Instructions
1. Build: `python scripts/build_nextjs.py --project-dir <path>`
2. Containerize: `python scripts/containerize.py --project-dir <path> --tag <image:tag>`
3. Manifests: `python scripts/generate_manifests.py --image <tag> --namespace learnflow`
4. Deploy: `python scripts/deploy_frontend.py --namespace learnflow`

## Validation
- [ ] Next.js builds successfully
- [ ] Docker image created
- [ ] Pods running in K8s
- [ ] Monaco Editor loads correctly

See [REFERENCE.md](./REFERENCE.md) for configuration and troubleshooting.
