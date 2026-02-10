---
name: kong-gateway-setup
description: Deploy Kong API Gateway with Kubernetes Ingress routing
version: 2.0.0
---

# Kong API Gateway Setup

## When to Use
- Deploy API Gateway for LearnFlow microservices
- Configure Kubernetes Ingress routing for frontend, API, and docs

## Prerequisites
- Kubernetes cluster running (`kubectl cluster-info`)
- Helm 3 installed (`helm version`)

## Instructions
1. Deploy: `python scripts/deploy_kong.py --namespace kong`
2. Routes: `python scripts/configure_services.py --namespace learnflow --output k8s/kong/`
3. Rate limit: `python scripts/configure_rate_limiting.py --namespace kong`
4. JWT auth: `python scripts/enable_jwt_auth.py --namespace kong`

## Validation
- [ ] Kong pods running in kong namespace
- [ ] 3 Ingress resources created (frontend, API, docs)
- [ ] All 9 API routes configured (triage, concepts, exercises, execute, debug, review, progress, curriculum, quizzes)
- [ ] Frontend accessible via Kong proxy

See [REFERENCE.md](./REFERENCE.md) for Ingress configuration and troubleshooting.
