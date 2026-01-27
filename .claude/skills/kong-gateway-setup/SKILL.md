---
name: kong-gateway-setup
description: |
  Deploy Kong API Gateway on Kubernetes with JWT authentication and routing. This skill
  should be used when setting up API gateway, configuring service routing, adding
  authentication/authorization, or implementing rate limiting for microservices.
---

# Kong API Gateway Setup

Deploy and configure Kong Gateway for LearnFlow microservices.

## When to Use

- Deploy API gateway for microservices
- Configure routing and load balancing
- Add JWT authentication to APIs
- Implement rate limiting and CORS

## Prerequisites

- Kubernetes cluster running: `kubectl cluster-info`
- Helm 3 installed: `helm version` (v3.0+)
- kubectl configured: `kubectl get nodes`
- Microservices deployed (triage, concepts, exercise, code-execution)

## Before Implementation

Gather context to ensure successful API gateway deployment:

| Source | Gather |
|--------|--------|
| **Kubernetes Cluster** | Namespace names, service endpoints, ingress requirements |
| **Microservices** | Service names, ports, health check endpoints, API paths |
| **Authentication** | JWT issuer (Better Auth), token validation requirements |
| **Network** | External domain/IP, TLS certificates, DNS configuration |

## Required Clarifications

1. **Database Mode**: How should Kong store configuration?
   - DB-less mode (declarative config in Kubernetes ConfigMaps)
   - PostgreSQL mode (requires separate database instance)
   - Hybrid mode (control plane + data plane)

2. **Service Routing**: What routing strategy is needed?
   - Path-based routing (e.g., /api/triage → triage-service)
   - Host-based routing (e.g., api.learnflow.com → gateway)
   - Service mesh integration (with Dapr service invocation)

3. **Security Requirements**: What security features are required?
   - JWT authentication with Better Auth
   - Rate limiting per endpoint/user
   - CORS configuration for frontend
   - API key authentication for specific services

4. **Observability**: What monitoring/logging is needed?
   - Request logging level (basic, extended, debug)
   - Metrics export (Prometheus integration)
   - Distributed tracing (Jaeger/Zipkin)

## Instructions

### 1. Deploy Kong
```bash
python scripts/deploy_kong.py --namespace kong --database postgres
```

### 2. Configure Services
```bash
python scripts/configure_services.py --namespace learnflow --config services.yaml
```

Routes microservices through Kong gateway.

### 3. Enable JWT Auth
```bash
python scripts/enable_jwt_auth.py --issuer better-auth --namespace kong
```

### 4. Configure Rate Limiting
```bash
python scripts/configure_rate_limiting.py --requests 100 --per minute
```

## Validation

- [ ] Kong pods running
- [ ] Admin API accessible
- [ ] Services registered
- [ ] JWT validation works
- [ ] Rate limiting active

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Kong pods CrashLoopBackOff | Check database connectivity, review pod logs |
| 404 for service routes | Verify service registration, check Kong routes config |
| JWT validation fails | Ensure issuer matches Better Auth, verify public key |
| Rate limiting not working | Check plugin configuration, verify consumer setup |

## Official Documentation

- Kong Gateway: https://docs.konghq.com/gateway/latest/
- Kong Kubernetes: https://docs.konghq.com/kubernetes-ingress-controller/
- JWT Plugin: https://docs.konghq.com/hub/kong-inc/jwt/
