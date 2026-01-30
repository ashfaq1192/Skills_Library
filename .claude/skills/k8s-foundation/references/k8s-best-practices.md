# Kubernetes Best Practices

Domain expertise for production-ready Kubernetes deployments.

## Resource Management

### Resource Limits and Requests

Always set resource limits and requests for containers:

```yaml
resources:
  requests:
    memory: "64Mi"
    cpu: "250m"
  limits:
    memory: "128Mi"
    cpu: "500m"
```

**Why**: Prevents resource starvation and enables proper scheduling.

### Namespace Organization

- **Production**: Isolate by environment (prod, staging, dev)
- **Team-based**: Separate by team or service domain
- **Resource quotas**: Set limits per namespace

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-quota
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    limits.cpu: "20"
    limits.memory: 40Gi
```

## Health Checks

### Liveness Probes

Detect when container is unhealthy and needs restart:

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```

### Readiness Probes

Detect when container is ready to receive traffic:

```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3
```

**Why**: Prevents routing traffic to unhealthy/unready pods.

## Configuration Management

### ConfigMaps for Configuration

Store non-sensitive configuration:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  LOG_LEVEL: "info"
  API_ENDPOINT: "https://api.example.com"
```

### Secrets for Sensitive Data

Store passwords, tokens, keys:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
stringData:
  username: admin
  password: <base64-encoded>
```

**Never commit secrets to version control.**

## Deployment Strategies

### Rolling Updates (Default)

Gradual replacement of old pods:

```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
```

**Use when**: Zero-downtime updates needed.

### Recreate

All pods terminated before new ones created:

```yaml
spec:
  strategy:
    type: Recreate
```

**Use when**: Stateful apps that can't run multiple versions.

## Labels and Selectors

### Standard Labels

```yaml
metadata:
  labels:
    app.kubernetes.io/name: myapp
    app.kubernetes.io/instance: myapp-prod
    app.kubernetes.io/version: "1.0.0"
    app.kubernetes.io/component: backend
    app.kubernetes.io/part-of: learnflow
    app.kubernetes.io/managed-by: helm
```

### Service Selectors

Match pod labels precisely:

```yaml
# Service
selector:
  app: myapp
  tier: frontend

# Pod
labels:
  app: myapp
  tier: frontend
```

## Security

### Pod Security Standards

Use built-in PSS (Pod Security Standards):

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

### Service Accounts

Create dedicated service accounts:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: myapp-sa
```

### Network Policies

Control pod-to-pod communication:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
spec:
  podSelector:
    matchLabels:
      app: backend
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
```

## Anti-Patterns

### ❌ Don't: Run as Root

**Problem**: Security vulnerability.
**Solution**: Use `securityContext`:

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 2000
```

### ❌ Don't: Use `latest` Tag

**Problem**: Unpredictable deployments.
**Solution**: Use specific version tags:

```yaml
image: myapp:v1.2.3  # Not myapp:latest
```

### ❌ Don't: Skip Resource Limits

**Problem**: Resource exhaustion, noisy neighbors.
**Solution**: Always set requests and limits.

### ❌ Don't: Ignore Health Checks

**Problem**: Traffic routed to unhealthy pods.
**Solution**: Implement liveness and readiness probes.

### ❌ Don't: Store Secrets in ConfigMaps

**Problem**: Security breach.
**Solution**: Use Secret resources or external secret managers.

## Official Documentation

- [Kubernetes Docs](https://kubernetes.io/docs/)
- [Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [Security Best Practices](https://kubernetes.io/docs/concepts/security/security-checklist/)
- [Production Checklist](https://learnk8s.io/production-best-practices)
