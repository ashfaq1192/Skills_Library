---
name: nextjs-k8s-deploy
description: Deploy Next.js with Monaco Editor and service rewrite proxy to Kubernetes
version: 2.0.0
---

# Next.js Kubernetes Deployment

## When to Use
- Deploy Next.js frontend to Kubernetes
- Set up service rewrite proxy to backend microservices
- Containerize frontend with Monaco code editor

## Prerequisites
- Node.js 18+ (`node --version`)
- Docker installed
- kubectl configured

## Instructions
1. Build: `python scripts/build_nextjs.py --project-dir <path>`
2. Containerize: `python scripts/containerize.py --project-dir <path> --tag <image:tag>`
3. Manifests: `python scripts/generate_manifests.py --image <tag> --namespace learnflow --services triage,concepts,exercises,execute,debug,review,progress`
4. Deploy: `python scripts/deploy_frontend.py --namespace learnflow`

## Validation
- [ ] Next.js builds with standalone output
- [ ] next.config.js has service rewrite rules for all backend services
- [ ] Monaco Editor loads in browser
- [ ] Service env vars set (TRIAGE_SERVICE_URL, etc.)
- [ ] K8s deployment includes env vars for all service URLs
- [ ] Docker image created and pods running

See [REFERENCE.md](./REFERENCE.md) for rewrite proxy config and Monaco setup.
