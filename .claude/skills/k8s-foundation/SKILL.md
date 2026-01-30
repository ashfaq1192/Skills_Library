---
name: k8s-foundation
description: Kubernetes cluster operations and health checks
version: 1.0.0
---

# Kubernetes Foundation

## When to Use
- Check cluster health and connectivity
- Create namespaces for deployments
- Deploy manifests and check status
- Troubleshoot failing pods

## Prerequisites
- kubectl installed (`kubectl version --client`)
- Cluster running (`minikube start` or cloud cluster)

## Instructions
1. Health check: `python scripts/cluster_health.py`
2. Create namespace: `python scripts/namespace.py --name <ns> --create`
3. Deploy: `python scripts/deploy.py --file <manifest.yaml> --namespace <ns>`
4. Status: `python scripts/status.py --namespace <ns> --resource pods`
5. Logs: `python scripts/logs.py --pod <name> --namespace <ns> --tail 50`
6. Diagnose: `python scripts/troubleshoot.py --namespace <ns>`

## Validation
- [ ] Cluster accessible
- [ ] Namespaces Active
- [ ] Pods Running (no CrashLoopBackOff)

See [REFERENCE.md](./REFERENCE.md) for details.
