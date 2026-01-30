---
name: dapr-setup
description: Install and configure Dapr on Kubernetes
version: 1.0.0
---

# Dapr Setup

## When to Use
- Install Dapr runtime on Kubernetes
- Configure state store and pub/sub components
- Enable service mesh for microservices

## Prerequisites
- Kubernetes cluster running (`kubectl cluster-info`)
- Helm 3 installed (`helm version`)

## Instructions
1. Install CLI: `python scripts/install_dapr_cli.py`
2. Init on K8s: `python scripts/init_dapr.py --namespace dapr-system`
3. Configure: `python scripts/configure_components.py --namespace learnflow`
4. Verify: `python scripts/check_dapr.py`

## Validation
- [ ] Dapr control plane running (dapr-system namespace)
- [ ] State store component configured
- [ ] Pub/sub component configured (Kafka)
- [ ] Sidecar injection enabled

See [REFERENCE.md](./REFERENCE.md) for component configuration and troubleshooting.
