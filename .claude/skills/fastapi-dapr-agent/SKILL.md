---
name: fastapi-dapr-agent
description: Generate FastAPI microservices with Dapr and AI agents
version: 1.0.0
---

# FastAPI + Dapr + AI Agent Generator

## When to Use
- Creating new microservices for LearnFlow
- Building AI-powered backend services with Dapr

## Prerequisites
- Python 3.9+ installed
- Docker installed (for containerization)
- Kubernetes cluster running

## Instructions
1. Generate: `python scripts/generate_service.py --name <service-name> --description "<desc>" --output <path>`
2. Configure Dapr: `python scripts/configure_dapr.py --service <name> --namespace learnflow`
3. Build container: `python scripts/build_container.py --service-dir <path> --tag <image:tag>`
4. Deploy: `python scripts/deploy_service.py --service <name> --namespace learnflow`

## Validation
- [ ] Service code generated with FastAPI + Dapr
- [ ] Health endpoint responds
- [ ] Dapr sidecar annotations present
- [ ] Container builds successfully

See [REFERENCE.md](./REFERENCE.md) for API patterns and templates.
