---
name: fastapi-dapr-agent
description: Generate FastAPI microservices with Dapr and AI agents
version: 2.0.0
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
1. Generate: `python scripts/generate_service.py --name <service-name> --type <type> --output <path>`
   - Types: `ai-agent`, `crud-api`, `code-executor`
   - AI agents use `gpt-4o-mini` via env `OPENAI_MODEL`
2. Configure Dapr: `python scripts/configure_dapr.py --service <name> --namespace learnflow`
3. Build container: `python scripts/build_container.py --service-dir <path> --tag <image:tag>`
4. Deploy: `python scripts/deploy_service.py --service <name> --namespace learnflow`

## Validation
- [ ] Service code generated with domain-specific endpoints
- [ ] Health endpoint responds at `/health`
- [ ] Dapr subscribe endpoint at `/dapr/subscribe`
- [ ] AI services use JSON response format and env-driven model
- [ ] Events published via Dapr pub/sub with struggle detection
- [ ] Container builds successfully

See [REFERENCE.md](./REFERENCE.md) for API patterns, service types, and templates.
