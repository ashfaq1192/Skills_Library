# FastAPI + Dapr + AI Agent - Reference Documentation

## Architecture Overview

This skill generates production-ready FastAPI microservices with:
- **Dapr sidecar** for service mesh capabilities
- **OpenAI SDK** integration for AI-powered endpoints
- **State management** via Dapr state store (PostgreSQL)
- **Pub/Sub messaging** via Dapr pub/sub (Kafka)
- **Service invocation** via Dapr service-to-service calls

### Service Types

#### 1. AI Agent (`ai-agent`)
Best for: Tutoring services, concept explanations, code analysis

**Features:**
- OpenAI GPT-4 integration
- Streaming responses
- Token usage tracking
- Context management

**Use Cases:**
- Triage service (analyzes learner struggles)
- Concepts service (explains programming concepts)
- Code review service (provides feedback)

#### 2. CRUD API (`crud-api`)
Best for: Data management services

**Features:**
- RESTful endpoints (GET, POST, PUT, DELETE)
- Dapr state store integration
- Input validation with Pydantic
- Automatic OpenAPI docs

**Use Cases:**
- Exercise management
- User profiles
- Learning progress tracking

#### 3. Event Processor (`event-processor`)
Best for: Asynchronous event handling

**Features:**
- Dapr pub/sub subscriptions
- Event-driven architecture
- Automatic retry logic
- Dead letter queue support

**Use Cases:**
- Learning event processor
- Analytics aggregation
- Notification service

#### 4. Code Executor (`code-executor`)
Best for: Running user code safely

**Features:**
- Sandboxed execution
- Resource limits
- Timeout handling
- Result capture

**Use Cases:**
- Python code execution service
- Exercise validation
- Test runner

## Generated Project Structure

```
triage-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models/              # Pydantic models
│   │   ├── __init__.py
│   │   └── schemas.py       # Request/response schemas
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── ai_service.py    # OpenAI integration
│   │   └── dapr_service.py  # Dapr operations
│   └── dapr/                # Dapr pub/sub handlers
│       ├── __init__.py
│       └── events.py        # Event handlers
├── tests/
│   ├── __init__.py
│   ├── test_main.py
│   └── test_ai_service.py
├── k8s/
│   ├── deployment.yaml      # Kubernetes deployment with Dapr annotations
│   └── service.yaml         # Kubernetes service
├── Dockerfile               # Multi-stage Docker build
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # Service-specific documentation
```

## Dapr Integration

### State Management

**Save state:**
```python
import requests

def save_state(key, value):
    response = requests.post(
        f"http://localhost:3500/v1.0/state/statestore",
        json=[{"key": key, "value": value}]
    )
    return response.status_code == 204
```

**Get state:**
```python
def get_state(key):
    response = requests.get(
        f"http://localhost:3500/v1.0/state/statestore/{key}"
    )
    if response.status_code == 200:
        return response.json()
    return None
```

### Pub/Sub Messaging

**Publish event:**
```python
def publish_event(topic, data):
    response = requests.post(
        f"http://localhost:3500/v1.0/publish/pubsub/{topic}",
        json=data
    )
    return response.status_code == 204
```

**Subscribe to events:**
```python
# In main.py
@app.get("/dapr/subscribe")
async def subscribe():
    return [{
        "pubsubname": "pubsub",
        "topic": "learning-events",
        "route": "/events"
    }]

@app.post("/events")
async def handle_event(event: dict):
    # Process event
    return {"status": "processed"}
```

### Service Invocation

**Call another service:**
```python
def call_service(service_name, method, data):
    response = requests.post(
        f"http://localhost:3500/v1.0/invoke/{service_name}/method/{method}",
        json=data
    )
    return response.json()
```

## OpenAI Integration

### Basic Chat Completion

```python
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_ai_response(prompt, context=None):
    messages = [
        {"role": "system", "content": "You are a helpful Python tutor."}
    ]

    if context:
        messages.append({"role": "assistant", "content": context})

    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )

    return {
        "response": response.choices[0].message.content,
        "tokens": response.usage.total_tokens
    }
```

### Streaming Responses

```python
from fastapi.responses import StreamingResponse

async def stream_ai_response(prompt):
    stream = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )

    async def generate():
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    return StreamingResponse(generate(), media_type="text/plain")
```

## Kubernetes Deployment

### Dapr Annotations

```yaml
annotations:
  dapr.io/enabled: "true"           # Enable Dapr sidecar
  dapr.io/app-id: "triage-service"  # Service identifier
  dapr.io/app-port: "8000"          # Application port
  dapr.io/log-level: "info"         # Dapr logging level
  dapr.io/enable-profiling: "false" # Profiling
```

### Environment Variables

Required:
- `DAPR_HTTP_PORT`: Dapr HTTP port (default: 3500)
- `OPENAI_API_KEY`: OpenAI API key (for AI services)
- `DATABASE_URL`: PostgreSQL connection (via secret)

Optional:
- `LOG_LEVEL`: Application log level
- `MAX_TOKENS`: Maximum tokens for AI responses
- `RATE_LIMIT`: Requests per minute

### Resource Limits

Recommended for production:

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

For AI services (higher memory for OpenAI SDK):

```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "200m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

## Testing

### Unit Tests

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_ai_endpoint():
    response = client.post("/process", json={
        "prompt": "Explain Python lists",
        "context": {}
    })
    assert response.status_code == 200
    assert "response" in response.json()
```

### Integration Tests

Test with Dapr:

```bash
# Start Dapr sidecar
dapr run --app-id test-service --app-port 8000 --dapr-http-port 3500

# Run tests
pytest tests/

# Stop Dapr
dapr stop test-service
```

## Troubleshooting

### Issue: Dapr sidecar not injecting

**Solution:**
1. Verify Dapr installed: `dapr status -k`
2. Check annotations in deployment.yaml
3. Verify namespace has Dapr enabled: `kubectl get namespace <namespace> -o yaml`

### Issue: OpenAI API errors

**Solution:**
1. Check API key: `kubectl get secret openai-credentials -o yaml`
2. Verify rate limits not exceeded
3. Check network egress from cluster

### Issue: State store connection failed

**Solution:**
1. Verify PostgreSQL running: `kubectl get pods -n default -l app=postgres`
2. Check Dapr component: `kubectl get component statestore -n <namespace>`
3. Test connection: `psql $DATABASE_URL -c '\l'`

### Issue: Pub/Sub events not received

**Solution:**
1. Verify Kafka running: `kubectl get pods -n kafka`
2. Check Dapr component: `kubectl get component pubsub -n <namespace>`
3. Verify subscription endpoint: `curl http://localhost:8000/dapr/subscribe`

## Performance Optimization

### 1. Connection Pooling

Use connection pooling for database and OpenAI:

```python
from openai import OpenAI
import psycopg2.pool

# OpenAI client (reuse across requests)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Database pool
db_pool = psycopg2.pool.SimpleConnectionPool(
    1, 20,
    os.getenv("DATABASE_URL")
)
```

### 2. Caching

Cache AI responses for common queries:

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_cached_ai_response(prompt: str):
    return get_ai_response(prompt)
```

### 3. Async Operations

Use async for I/O operations:

```python
import httpx

async def call_service_async(service_name, method, data):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"http://localhost:3500/v1.0/invoke/{service_name}/method/{method}",
            json=data
        )
        return response.json()
```

## Security Best Practices

1. **API Key Management**
   - Never hardcode API keys
   - Use Kubernetes Secrets
   - Rotate keys regularly

2. **Input Validation**
   - Use Pydantic models
   - Sanitize user inputs
   - Limit request sizes

3. **Rate Limiting**
   - Implement per-user rate limits
   - Use Kong Gateway for global limits
   - Monitor token usage

4. **Error Handling**
   - Don't expose internal errors
   - Log security events
   - Use structured logging

## Monitoring

### Health Checks

```python
@app.get("/health")
async def health():
    # Check dependencies
    dapr_healthy = check_dapr()
    db_healthy = check_database()
    ai_healthy = check_openai()

    return {
        "status": "healthy" if all([dapr_healthy, db_healthy, ai_healthy]) else "unhealthy",
        "checks": {
            "dapr": dapr_healthy,
            "database": db_healthy,
            "openai": ai_healthy
        }
    }
```

### Metrics

Track key metrics:
- Request count and latency
- AI token usage
- Error rates
- Dapr operation latency

### Logging

Use structured logging:

```python
import logging
import json

logger = logging.getLogger(__name__)

def log_event(event_type, data):
    logger.info(json.dumps({
        "event": event_type,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }))
```

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Dapr Python SDK](https://docs.dapr.io/developing-applications/sdks/python/)
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
