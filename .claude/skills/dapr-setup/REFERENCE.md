# Dapr Setup - Reference Documentation

## What is Dapr?

Dapr (Distributed Application Runtime) is a portable, event-driven runtime that simplifies building resilient, stateless, and stateful applications for cloud and edge environments.

## Architecture

### Control Plane Components

1. **dapr-sidecar-injector**
   - Injects Dapr sidecar into annotated pods
   - Watches for pod creation events
   - Configures sidecar container

2. **dapr-operator**
   - Manages Dapr components (state stores, pub/sub)
   - Watches for component CRD changes
   - Updates component configurations

3. **dapr-placement**
   - Actor placement service
   - Manages virtual actor distribution
   - Required for actor-based services

4. **dapr-sentry**
   - Certificate authority for mTLS
   - Issues certificates to sidecars
   - Manages trust root

### Sidecar Architecture

```
┌─────────────────────────────────────┐
│           Kubernetes Pod             │
│  ┌──────────────┐  ┌──────────────┐ │
│  │              │  │              │ │
│  │  Application │◄─┤ Dapr Sidecar │ │
│  │  Container   │  │  (daprd)     │ │
│  │  Port: 8000  │  │  Port: 3500  │ │
│  │              │  │              │ │
│  └──────────────┘  └──────┬───────┘ │
│                           │         │
└───────────────────────────┼─────────┘
                            │
            ┌───────────────┼──────────────┐
            │               │              │
     ┌──────▼─────┐  ┌─────▼──────┐  ┌───▼────┐
     │   State    │  │   Pub/Sub  │  │ Service│
     │   Store    │  │   (Kafka)  │  │  Calls │
     └────────────┘  └────────────┘  └────────┘
```

## Building Blocks

### 1. State Management

Provides key-value storage abstraction with pluggable backends.

**Supported Operations:**
- `save` - Store key-value pairs
- `get` - Retrieve values
- `delete` - Remove keys
- `bulk` - Batch operations
- `query` - Query with filters (alpha)

**Example Component:**
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    secretKeyRef:
      name: postgres-credentials
      key: DATABASE_URL
```

**Usage:**
```bash
# Save state
curl -X POST http://localhost:3500/v1.0/state/statestore \
  -H "Content-Type: application/json" \
  -d '[{"key":"user-123","value":{"name":"John"}}]'

# Get state
curl http://localhost:3500/v1.0/state/statestore/user-123
```

### 2. Pub/Sub Messaging

Event-driven architecture with multiple message brokers.

**Features:**
- At-least-once delivery
- Message ordering (with partitions)
- Dead letter queues
- Content-based routing

**Example Component:**
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka.kafka.svc.cluster.local:9092"
  - name: consumerGroup
    value: "learnflow"
```

**Publish:**
```bash
curl -X POST http://localhost:3500/v1.0/publish/pubsub/learning-events \
  -H "Content-Type: application/json" \
  -d '{"event":"struggle","userId":"123"}'
```

**Subscribe:**
```python
@app.get("/dapr/subscribe")
def subscribe():
    return [{
        "pubsubname": "pubsub",
        "topic": "learning-events",
        "route": "/events"
    }]

@app.post("/events")
def handle_event(event: dict):
    # Process event
    return {"status": "success"}
```

### 3. Service Invocation

Service-to-service calls with service discovery, retries, and mTLS.

**Benefits:**
- Service discovery via DNS
- Automatic retries
- Circuit breaking
- mTLS encryption
- Distributed tracing

**Usage:**
```bash
# Call another service
curl http://localhost:3500/v1.0/invoke/concepts-service/method/explain \
  -H "Content-Type: application/json" \
  -d '{"concept":"lists"}'
```

**With retry:**
```python
import requests

def call_with_retry(service, method, data, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"http://localhost:3500/v1.0/invoke/{service}/method/{method}",
                json=data,
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
    return None
```

### 4. Bindings (Input/Output)

Connect to external systems without SDK dependencies.

**Input Bindings:**
- Cron (scheduled jobs)
- Kafka (consume messages)
- AWS SQS, Azure Event Hubs, etc.

**Output Bindings:**
- HTTP
- Kafka
- AWS S3, Azure Blob Storage, etc.
- Twilio, SendGrid, etc.

**Example:**
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: cron-job
spec:
  type: bindings.cron
  version: v1
  metadata:
  - name: schedule
    value: "@every 1h"
```

### 5. Secrets Management

Retrieve secrets from secret stores.

**Supported Stores:**
- Kubernetes Secrets
- HashiCorp Vault
- AWS Secrets Manager
- Azure Key Vault

**Usage:**
```bash
# Get secret
curl http://localhost:3500/v1.0/secrets/kubernetes/db-password
```

### 6. Actors (Virtual Actors)

Stateful objects with method invocation and timers.

**Features:**
- Single-threaded execution
- Automatic activation/deactivation
- State persistence
- Timers and reminders

**Example:**
```python
from dapr.actor import Actor, ActorInterface

class UserActor(Actor):
    async def get_state(self):
        return await self._state_manager.get_state("user_data")

    async def set_state(self, data):
        await self._state_manager.set_state("user_data", data)
        await self._state_manager.save_state()
```

## Component Configuration

### State Store (PostgreSQL)

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: learnflow
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    secretKeyRef:
      name: postgres-credentials
      key: DATABASE_URL
  - name: tableName
    value: state
  - name: metadataTableName
    value: state_metadata
```

### Pub/Sub (Kafka)

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
  namespace: learnflow
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka-0.kafka-headless.kafka.svc.cluster.local:9092,kafka-1.kafka-headless.kafka.svc.cluster.local:9092,kafka-2.kafka-headless.kafka.svc.cluster.local:9092"
  - name: consumerGroup
    value: "learnflow"
  - name: authType
    value: "none"
  - name: maxMessageBytes
    value: "1024000"
```

### Secret Store (Kubernetes)

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
  namespace: learnflow
spec:
  type: secretstores.kubernetes
  version: v1
  metadata: []
```

## Security

### mTLS (Mutual TLS)

Dapr automatically enables mTLS between sidecars:

1. **Certificate Issuance**: Sentry service issues certificates
2. **Certificate Rotation**: Automatic rotation every 24 hours
3. **Trust Root**: Shared across all services

**Verify mTLS:**
```bash
kubectl logs -n dapr-system <dapr-sidecar-injector-pod> | grep mTLS
```

### RBAC (Role-Based Access Control)

Control which services can invoke others:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: appconfig
spec:
  accessControl:
    defaultAction: deny
    trustDomain: "cluster.local"
    policies:
    - appId: triage-service
      defaultAction: allow
      operations:
      - name: /process
        httpVerb: ['POST']
        action: allow
```

## Observability

### Logging

**Sidecar Logs:**
```bash
# Application logs
kubectl logs <pod-name> -c <app-container>

# Dapr sidecar logs
kubectl logs <pod-name> -c daprd
```

**Log Levels:**
- `debug` - Detailed logs
- `info` - Standard logs
- `warn` - Warnings only
- `error` - Errors only

### Metrics

Dapr exposes Prometheus metrics on port 9090:

**Key Metrics:**
- `dapr_http_server_request_count` - HTTP requests
- `dapr_http_server_latency_ms` - Request latency
- `dapr_component_invocation_count` - Component operations
- `dapr_sidecar_injector_sidecar_count` - Active sidecars

**Scrape Config:**
```yaml
- job_name: 'dapr-sidecar'
  kubernetes_sd_configs:
  - role: pod
  relabel_configs:
  - source_labels: [__meta_kubernetes_pod_container_port_name]
    action: keep
    regex: metrics
```

### Tracing

Dapr supports distributed tracing with:
- Zipkin
- Jaeger
- OpenTelemetry

**Enable Tracing:**
```yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: tracing
spec:
  tracing:
    samplingRate: "1"
    zipkin:
      endpointAddress: "http://zipkin.istio-system.svc.cluster.local:9411/api/v2/spans"
```

## Performance Tuning

### Sidecar Resources

Adjust based on workload:

**Light workload:**
```yaml
requests:
  memory: "50Mi"
  cpu: "50m"
limits:
  memory: "100Mi"
  cpu: "100m"
```

**Heavy workload:**
```yaml
requests:
  memory: "200Mi"
  cpu: "200m"
limits:
  memory: "500Mi"
  cpu: "500m"
```

### HTTP/2 vs HTTP/1.1

Enable HTTP/2 for better performance:

```yaml
annotations:
  dapr.io/enable-api-logging: "false"
  dapr.io/http-max-request-size: "4"
  dapr.io/http-read-buffer-size: "4"
```

### Connection Pooling

Configure connection pools:

```yaml
annotations:
  dapr.io/app-max-concurrency: "100"
```

## Troubleshooting

### Issue: Sidecar not injecting

**Check:**
```bash
# Verify Dapr installed
dapr status -k

# Check sidecar injector logs
kubectl logs -n dapr-system -l app=dapr-sidecar-injector

# Verify annotations
kubectl get pod <pod-name> -o yaml | grep dapr.io
```

### Issue: Component not found

**Check:**
```bash
# List components
kubectl get components -n <namespace>

# Describe component
kubectl describe component <component-name> -n <namespace>

# Check sidecar logs
kubectl logs <pod-name> -c daprd | grep component
```

### Issue: Service invocation fails

**Check:**
```bash
# Verify target service running
kubectl get pods -n <namespace> -l app=<target-service>

# Test service directly
kubectl port-forward -n <namespace> <pod-name> 8000:8000
curl http://localhost:8000/health

# Check Dapr service discovery
kubectl logs <pod-name> -c daprd | grep "service invocation"
```

## Upgrading Dapr

```bash
# Check current version
dapr version

# Upgrade control plane
dapr upgrade -k --runtime-version 1.12.0

# Restart pods to get new sidecars
kubectl rollout restart deployment/<deployment-name> -n <namespace>
```

## Best Practices

1. **Use Configuration CRDs**
   - Centralize configuration
   - Apply consistent settings
   - Enable tracing and metrics

2. **Separate Namespaces**
   - Dapr control plane in `dapr-system`
   - Applications in separate namespaces
   - Components scoped to namespaces

3. **Monitor Component Health**
   - Set up alerts for component failures
   - Monitor connection pools
   - Track error rates

4. **Test Locally First**
   - Use `dapr init` for local development
   - Test components in self-hosted mode
   - Validate before K8s deployment

5. **Version Components**
   - Use specific component versions
   - Test upgrades in staging
   - Document breaking changes

## References

- [Dapr Documentation](https://docs.dapr.io/)
- [Dapr GitHub](https://github.com/dapr/dapr)
- [Component Specs](https://docs.dapr.io/reference/components-reference/)
- [Best Practices](https://docs.dapr.io/operations/best-practices/)
