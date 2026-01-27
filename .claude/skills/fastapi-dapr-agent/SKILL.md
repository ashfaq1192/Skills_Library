---
name: fastapi-dapr-agent
description: |
  Generate FastAPI microservices with Dapr integration and AI agent capabilities. This skill
  should be used when scaffolding new microservices, creating AI-powered backend services,
  or building event-driven services with state management and pub/sub messaging.
---

# FastAPI + Dapr + AI Agent Generator

Generate production-ready FastAPI microservices with Dapr sidecars and OpenAI integration.

## When to Use

- Create new microservice for LearnFlow platform
- Scaffold AI-powered service (tutoring, code execution, triage)
- Generate service with Dapr state management and pub/sub
- Bootstrap FastAPI project with proper structure

## Prerequisites

- Python 3.9+ installed:
  ```bash
  python3 --version  # Should be 3.9 or higher
  pip install fastapi uvicorn openai requests
  ```
- Docker installed (for containerization)
- Dapr installed on K8s cluster (use dapr-setup skill)
- `kubectl` access for deployment
- OpenAI API key (for AI-powered services, optional)

## Before Implementation

Gather context for microservice generation:

| Source | Gather |
|--------|--------|
| **Project** | Service purpose, existing services, naming conventions |
| **User** | Service type (AI/CRUD/Event/Code), required endpoints, AI model preferences |
| **Cluster** | Target namespace, Dapr components available, resource limits |

## Required Clarifications

1. **Service Purpose**: What does this service do?
   - Example: "Analyze learner struggles", "Manage exercises", "Execute Python code"
   - Use description for service name and documentation

2. **Service Type**: Which type best fits your needs?
   - `ai-agent`: Integrates OpenAI for intelligent processing
   - `crud-api`: RESTful CRUD operations with state management
   - `event-processor`: Handles async events from Kafka/pub-sub
   - `code-executor`: Safely executes user code in sandbox

3. **AI Integration** (if ai-agent selected): Do you have an OpenAI API key?
   - If yes: Which model? (gpt-4, gpt-3.5-turbo)
   - If no: Cannot create AI-powered service without API key

4. **Deployment Details**: Where should this service run?
   - Namespace (default: learnflow)
   - Replicas (default: 2 for high availability)
   - Resource limits (default: 512Mi memory, 500m CPU)

## Instructions

### 1. Generate Service
```bash
python scripts/generate_service.py \
  --name triage-service \
  --type ai-agent \
  --output ./services/triage
```

Service types: `ai-agent`, `crud-api`, `event-processor`, `code-executor`

### 2. Configure Dapr Components
```bash
python scripts/configure_dapr.py --service-dir ./services/triage
```

### 3. Build Container
```bash
python scripts/build_container.py --service-dir ./services/triage --tag v1.0.0
```

### 4. Deploy to K8s
```bash
python scripts/deploy_service.py --service-dir ./services/triage --namespace learnflow
```

## Generated Structure

```
triage-service/
├── app/
│   ├── main.py              # FastAPI app with Dapr integration
│   ├── models/              # Pydantic models
│   ├── services/            # Business logic with OpenAI
│   └── dapr/                # Dapr pub/sub handlers
├── Dockerfile
├── requirements.txt
├── k8s/
│   ├── deployment.yaml      # With Dapr annotations
│   └── service.yaml
└── tests/
```

## Validation

- [ ] Service generates without errors
- [ ] FastAPI app starts locally
- [ ] Dapr sidecar attaches in K8s
- [ ] Health endpoint responds
- [ ] AI functionality works (if ai-agent type)

## Troubleshooting

- **OpenAI errors**: Verify API key in K8s secret, check rate limits
- **Dapr sidecar not attached**: Check Dapr annotations, verify Dapr installed
- **State store unavailable**: Verify statestore component exists in namespace
- **Pub/Sub not working**: Verify pubsub component configured, check Kafka

## Official Documentation

- FastAPI: https://fastapi.tiangolo.com/
- Dapr Python SDK: https://docs.dapr.io/developing-applications/sdks/python/
- OpenAI Python SDK: https://platform.openai.com/docs/api-reference
- See REFERENCE.md in this directory for comprehensive patterns
