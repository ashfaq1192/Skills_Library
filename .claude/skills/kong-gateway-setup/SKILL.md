---
name: kong-gateway-setup
description: Deploy Kong API Gateway on Kubernetes
version: 1.0.0
---

# Kong API Gateway Setup

## When to Use
- Deploy API Gateway for microservices
- Configure routing, rate limiting, JWT auth

## Prerequisites
- Kubernetes cluster running (`kubectl cluster-info`)
- Helm 3 installed (`helm version`)

## Instructions
1. Deploy: `python scripts/deploy_kong.py --namespace kong`
2. Routes: `python scripts/configure_services.py --namespace kong --config <routes.yaml>`
3. Rate limit: `python scripts/configure_rate_limiting.py --namespace kong`
4. JWT auth: `python scripts/enable_jwt_auth.py --namespace kong`

## Validation
- [ ] Kong pods running in kong namespace
- [ ] API routes configured
- [ ] Rate limiting enabled
- [ ] JWT authentication active

See [REFERENCE.md](./REFERENCE.md) for route configuration and troubleshooting.
