# Kong API Gateway - Reference Documentation

## Overview

Kong Gateway is an open-source API gateway and microservices management layer built on Nginx. It provides authentication, rate limiting, transformations, logging, and more through a plugin architecture.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Kong Gateway                            │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   JWT    │  │   Rate   │  │   CORS   │  │ Request  │   │
│  │   Auth   │  │ Limiting │  │  Plugin  │  │Transform │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Kong Core (Nginx)                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              PostgreSQL Database                      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   ┌────▼────┐         ┌────▼────┐        ┌────▼────┐
   │ Triage  │         │Concepts │        │Exercise │
   │ Service │         │ Service │        │ Service │
   └─────────┘         └─────────┘        └─────────┘
```

## Core Concepts

### 1. Services

A Service represents an upstream API or microservice.

**Create Service:**
```bash
curl -X POST http://localhost:8001/services \
  -d name=triage-service \
  -d url=http://triage-service.learnflow.svc.cluster.local:80
```

**Service Fields:**
- `name` - Unique identifier
- `url` - Upstream URL (protocol://host:port)
- `protocol` - http, https, grpc, grpcs, tcp, tls
- `retries` - Number of retries (default: 5)
- `connect_timeout` - Connection timeout (ms)
- `write_timeout` - Write timeout (ms)
- `read_timeout` - Read timeout (ms)

### 2. Routes

Routes define how requests are proxied to Services.

**Create Route:**
```bash
curl -X POST http://localhost:8001/services/triage-service/routes \
  -d name=triage-route \
  -d 'paths[]=/triage' \
  -d strip_path=true
```

**Route Matching:**
- `paths` - URL paths (e.g., /api/v1)
- `hosts` - Hostnames (e.g., api.example.com)
- `methods` - HTTP methods (GET, POST, etc.)
- `headers` - Header-based routing

**Path Handling:**
- `strip_path=true` - Remove matched path before proxying
- `preserve_host=true` - Keep original Host header

### 3. Consumers

Consumers represent users/applications using the API.

**Create Consumer:**
```bash
curl -X POST http://localhost:8001/consumers \
  -d username=better-auth
```

**Consumer Authentication:**
- JWT credentials
- API keys
- OAuth2 tokens
- Basic Auth
- HMAC

### 4. Plugins

Plugins extend Kong's functionality.

**Plugin Scopes:**
- Global - Apply to all services
- Service - Apply to specific service
- Route - Apply to specific route
- Consumer - Apply to specific consumer

## Essential Plugins

### JWT Authentication

Validate JSON Web Tokens.

**Enable JWT:**
```bash
curl -X POST http://localhost:8001/plugins \
  -d name=jwt \
  -d config.claims_to_verify=exp
```

**JWT Credential:**
```bash
curl -X POST http://localhost:8001/consumers/better-auth/jwt \
  -d algorithm=HS256 \
  -d key=better-auth \
  -d secret=your-jwt-secret
```

**Request with JWT:**
```bash
curl http://localhost:8000/triage/health \
  -H "Authorization: Bearer <jwt-token>"
```

**JWT Token Format:**
```json
{
  "iss": "better-auth",
  "exp": 1234567890,
  "sub": "user-123",
  "aud": "learnflow"
}
```

### Rate Limiting

Control request rates.

**Enable Rate Limiting:**
```bash
curl -X POST http://localhost:8001/plugins \
  -d name=rate-limiting \
  -d config.minute=100 \
  -d config.policy=local
```

**Policies:**
- `local` - In-memory (single node)
- `cluster` - Database-backed (shared)
- `redis` - Redis-backed (recommended for production)

**Response Headers:**
```
X-RateLimit-Limit-Minute: 100
X-RateLimit-Remaining-Minute: 87
```

**429 Response:**
```json
{
  "message": "API rate limit exceeded"
}
```

### CORS

Enable Cross-Origin Resource Sharing.

**Enable CORS:**
```bash
curl -X POST http://localhost:8001/plugins \
  -d name=cors \
  -d 'config.origins=*' \
  -d 'config.methods=GET,POST,PUT,DELETE,PATCH,OPTIONS' \
  -d 'config.headers=Accept,Authorization,Content-Type' \
  -d 'config.exposed_headers=X-Auth-Token' \
  -d config.credentials=true \
  -d config.max_age=3600
```

**CORS Headers:**
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET,POST,PUT,DELETE
Access-Control-Allow-Headers: Accept,Authorization
Access-Control-Allow-Credentials: true
```

### Request Transformer

Modify requests before proxying.

**Add Headers:**
```bash
curl -X POST http://localhost:8001/plugins \
  -d name=request-transformer \
  -d 'config.add.headers=X-Service-Name:kong'
```

**Transform Body:**
```bash
curl -X POST http://localhost:8001/plugins \
  -d name=request-transformer \
  -d 'config.add.body=api_version:v1'
```

### Response Transformer

Modify responses.

**Add Headers:**
```bash
curl -X POST http://localhost:8001/plugins \
  -d name=response-transformer \
  -d 'config.add.headers=X-Powered-By:Kong'
```

### Logging

Log requests to various sinks.

**HTTP Log:**
```bash
curl -X POST http://localhost:8001/plugins \
  -d name=http-log \
  -d config.http_endpoint=http://logger.example.com/logs
```

**File Log:**
```bash
curl -X POST http://localhost:8001/plugins \
  -d name=file-log \
  -d config.path=/var/log/kong/access.log
```

## LearnFlow Integration

### Service Configuration

```bash
# Triage Service
curl -X POST http://localhost:8001/services \
  -d name=triage-service \
  -d url=http://triage-service.learnflow.svc.cluster.local:80

curl -X POST http://localhost:8001/services/triage-service/routes \
  -d 'paths[]=/triage' \
  -d strip_path=true

# Concepts Service
curl -X POST http://localhost:8001/services \
  -d name=concepts-service \
  -d url=http://concepts-service.learnflow.svc.cluster.local:80

curl -X POST http://localhost:8001/services/concepts-service/routes \
  -d 'paths[]=/concepts' \
  -d strip_path=true

# Exercise Service
curl -X POST http://localhost:8001/services \
  -d name=exercise-service \
  -d url=http://exercise-service.learnflow.svc.cluster.local:80

curl -X POST http://localhost:8001/services/exercise-service/routes \
  -d 'paths[]=/exercises' \
  -d strip_path=true

# Code Execution Service
curl -X POST http://localhost:8001/services \
  -d name=code-execution-service \
  -d url=http://code-execution-service.learnflow.svc.cluster.local:80

curl -X POST http://localhost:8001/services/code-execution-service/routes \
  -d 'paths[]=/execute' \
  -d strip_path=true
```

### Better Auth Integration

**Consumer Setup:**
```bash
# Create consumer for Better Auth
curl -X POST http://localhost:8001/consumers \
  -d username=better-auth

# Add JWT credential
curl -X POST http://localhost:8001/consumers/better-auth/jwt \
  -d algorithm=HS256 \
  -d key=better-auth \
  -d secret=$JWT_SECRET
```

**Better Auth Configuration:**

In your Next.js app, configure Better Auth to include required claims:

```typescript
// lib/auth.ts
export const auth = betterAuth({
  jwt: {
    claims: {
      iss: "better-auth",  // Kong expects this
      aud: "learnflow",
      exp: Math.floor(Date.now() / 1000) + (60 * 60), // 1 hour
    }
  }
})
```

### Rate Limiting Strategy

**Per-Service Limits:**
```bash
# Triage Service - Heavy AI usage, lower limit
curl -X POST http://localhost:8001/services/triage-service/plugins \
  -d name=rate-limiting \
  -d config.minute=30

# Concepts Service - Moderate usage
curl -X POST http://localhost:8001/services/concepts-service/plugins \
  -d name=rate-limiting \
  -d config.minute=60

# Exercise Service - High read volume
curl -X POST http://localhost:8001/services/exercise-service/plugins \
  -d name=rate-limiting \
  -d config.minute=100
```

## Kubernetes Deployment

### Helm Values

```yaml
# kong-values.yaml
ingressController:
  enabled: true
  installCRDs: false

proxy:
  type: LoadBalancer
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"

env:
  database: postgres
  pg_host: postgres.default.svc.cluster.local
  pg_port: 5432
  pg_user: kong
  pg_password: kong
  pg_database: kong
  log_level: info
  plugins: bundled,jwt,rate-limiting,cors

resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "1Gi"
    cpu: "1000m"

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 5
  targetCPUUtilizationPercentage: 70
```

### Database Setup

**PostgreSQL for Kong:**
```bash
# Create database
kubectl exec -it postgres-0 -- psql -U postgres
CREATE DATABASE kong;
CREATE USER kong WITH PASSWORD 'kong';
GRANT ALL PRIVILEGES ON DATABASE kong TO kong;

# Run migrations
kubectl exec -it kong-kong-<pod-id> -- kong migrations bootstrap
```

### Ingress Configuration

**Expose Kong:**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: kong-ingress
spec:
  ingressClassName: kong
  rules:
  - host: api.learnflow.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: kong-kong-proxy
            port:
              number: 80
```

## Monitoring

### Admin API Health

```bash
# Kong health
curl http://localhost:8001/status

# Database connectivity
curl http://localhost:8001/

# Cluster status
curl http://localhost:8001/cluster/status
```

### Metrics

Kong exposes Prometheus metrics:

**Enable Prometheus Plugin:**
```bash
curl -X POST http://localhost:8001/plugins \
  -d name=prometheus
```

**Metrics Endpoint:**
```
http://localhost:8001/metrics
```

**Key Metrics:**
- `kong_http_status` - HTTP status codes
- `kong_latency` - Request latency
- `kong_bandwidth` - Bytes transferred
- `kong_datastore_reachable` - Database health

### Logging

**Access Logs:**
```bash
kubectl logs -n kong kong-kong-<pod-id> | grep "GET /triage"
```

**Error Logs:**
```bash
kubectl logs -n kong kong-kong-<pod-id> | grep ERROR
```

**Structured Logging:**
```bash
curl -X POST http://localhost:8001/plugins \
  -d name=file-log \
  -d config.path=/dev/stdout \
  -d config.reopen=true
```

## Performance Tuning

### Worker Processes

```yaml
env:
  nginx_worker_processes: "4"
  nginx_worker_connections: "4096"
```

### Database Connection Pool

```yaml
env:
  pg_max_concurrent_queries: "0"  # Unlimited
  pg_semaphore_timeout: "60000"   # 60 seconds
```

### DNS Resolver

```yaml
env:
  dns_resolver: "kube-dns.kube-system.svc.cluster.local"
  dns_hostsfile: "/etc/hosts"
  dns_order: "LAST,SRV,A,CNAME"
```

### Memory Configuration

```yaml
env:
  mem_cache_size: "128m"
  lua_shared_dict: "prometheus_metrics 5m"
```

## Security Best Practices

1. **Disable Admin API Public Access**
   ```yaml
   admin:
     enabled: true
     type: ClusterIP  # Not LoadBalancer
   ```

2. **Enable mTLS for Admin API**
   ```yaml
   env:
     admin_ssl_enabled: "true"
     admin_ssl_cert: "/etc/secrets/admin-cert.pem"
     admin_ssl_cert_key: "/etc/secrets/admin-key.pem"
   ```

3. **Use RBAC Plugin**
   ```bash
   curl -X POST http://localhost:8001/plugins \
     -d name=rbac
   ```

4. **Rotate JWT Secrets**
   - Use Kubernetes Secrets
   - Rotate every 90 days
   - Support multiple active secrets

5. **Rate Limit Admin API**
   ```bash
   curl -X POST http://localhost:8001/plugins \
     -d name=ip-restriction \
     -d 'config.allow=10.0.0.0/8'
   ```

## Troubleshooting

### Issue: 502 Bad Gateway

**Causes:**
- Upstream service down
- DNS resolution failure
- Connection timeout

**Debug:**
```bash
# Check service
kubectl get pods -n learnflow -l app=triage-service

# Test direct connection
kubectl port-forward -n learnflow svc/triage-service 8080:80
curl http://localhost:8080/health

# Check Kong logs
kubectl logs -n kong kong-kong-<pod-id> | grep "upstream"
```

### Issue: JWT validation fails

**Check:**
```bash
# Verify JWT plugin
curl http://localhost:8001/plugins | jq '.data[] | select(.name=="jwt")'

# Verify consumer
curl http://localhost:8001/consumers/better-auth

# Verify credentials
curl http://localhost:8001/consumers/better-auth/jwt

# Test JWT
echo "JWT_PAYLOAD" | base64 -d
```

### Issue: Rate limit not working

**Check:**
```bash
# Verify plugin
curl http://localhost:8001/plugins | jq '.data[] | select(.name=="rate-limiting")'

# Check response headers
curl -I http://localhost:8000/triage/health | grep X-RateLimit

# Check Redis connection (if using Redis policy)
kubectl exec -it kong-kong-<pod-id> -- redis-cli ping
```

### Issue: High latency

**Investigate:**
```bash
# Check Kong metrics
curl http://localhost:8001/metrics | grep latency

# Enable detailed logging
curl -X PATCH http://localhost:8001/ \
  -d log_level=debug

# Profile specific route
curl http://localhost:8001/routes/<route-id>/plugins \
  -X POST \
  -d name=request-termination \
  -d config.status_code=503 \
  -d config.message="Under maintenance"
```

## Declarative Configuration

Use Kong's declarative config for GitOps:

```yaml
# kong.yaml
_format_version: "3.0"

services:
- name: triage-service
  url: http://triage-service.learnflow.svc.cluster.local:80
  routes:
  - name: triage-route
    paths:
    - /triage
    strip_path: true
  plugins:
  - name: jwt
    config:
      claims_to_verify:
      - exp
  - name: rate-limiting
    config:
      minute: 30

consumers:
- username: better-auth
  jwt_secrets:
  - key: better-auth
    algorithm: HS256
    secret: ${JWT_SECRET}

plugins:
- name: cors
  config:
    origins:
    - "*"
    methods:
    - GET
    - POST
    - PUT
    - DELETE
    credentials: true
```

**Apply Configuration:**
```bash
kubectl create configmap kong-config --from-file=kong.yaml -n kong
kubectl set env deployment/kong-kong KONG_DECLARATIVE_CONFIG=/etc/kong/kong.yaml -n kong
kubectl rollout restart deployment/kong-kong -n kong
```

## References

- [Kong Documentation](https://docs.konghq.com/)
- [Kong Helm Chart](https://github.com/Kong/charts)
- [Kong Plugin Hub](https://docs.konghq.com/hub/)
- [Kong Admin API](https://docs.konghq.com/gateway/latest/admin-api/)
