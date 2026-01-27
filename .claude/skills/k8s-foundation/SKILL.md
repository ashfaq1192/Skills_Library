---
name: k8s-foundation
description: |
  Kubernetes cluster operations and health checks. This skill should be used
  when deploying applications to Kubernetes, checking cluster health, managing
  resources, or troubleshooting deployments. Provides foundational K8s operations
  that other infrastructure skills depend on.
---

# Kubernetes Foundation

Core Kubernetes operations for cluster management, health checks, and resource deployment.

## When to Use

- Check Kubernetes cluster connectivity and health
- Create or verify namespaces for application deployments
- Deploy applications using kubectl apply
- Check pod status, logs, and troubleshoot issues
- Verify resource deployments (deployments, services, configmaps, secrets)
- Execute commands in running pods for debugging

## Prerequisites

- Kubernetes cluster running: `minikube start` or cloud cluster (GKE, EKS, AKS)
- kubectl installed: `kubectl version --client` (v1.24+)
- Cluster context configured: `kubectl config current-context`
- Cluster access verified: `kubectl cluster-info`

## Before Implementation

Gather context to ensure successful Kubernetes operations:

| Source | Gather |
|--------|--------|
| **Cluster Environment** | Cluster type (Minikube/cloud), node count, resource capacity |
| **Target Namespace** | Namespace name, resource quotas, network policies |
| **Application Manifests** | YAML file paths, resource types, dependencies |
| **Existing Resources** | Current deployments, services, configmaps to verify/update |

## Required Clarifications

1. **Cluster Type**: What Kubernetes environment is targeted?
   - Local development (Minikube, Kind, Docker Desktop)
   - Cloud managed (GKE, EKS, AKS)
   - Self-managed cluster
   - Resource constraints to consider

2. **Namespace Strategy**: How should namespaces be organized?
   - Single namespace for all components
   - Per-service namespaces (e.g., kafka, learnflow, kong)
   - Environment-based (dev, staging, prod)

3. **Resource Requirements**: What are the deployment resource needs?
   - CPU/memory requests and limits
   - Storage requirements (PVCs, storage classes)
   - Scaling expectations (HPA configuration)

4. **Deployment Strategy**: How should updates be deployed?
   - Rolling updates (default)
   - Blue/green deployments
   - Canary deployments
   - Rollback strategy on failures

## Instructions

### 1. Check Cluster Health
```bash
python scripts/cluster_health.py
```
Verifies cluster connectivity, node status, and core components.

### 2. Manage Namespaces
```bash
python scripts/namespace.py --name <namespace> [--create]
```
Creates namespace if it doesn't exist, or verifies existing namespace.

### 3. Deploy Resources
```bash
python scripts/deploy.py --file <manifest.yaml> --namespace <namespace>
```
Applies Kubernetes manifests with validation.

### 4. Check Resource Status
```bash
python scripts/status.py --namespace <namespace> --resource <type>
```
Checks status of deployments, pods, services, etc.

### 5. Get Pod Logs
```bash
python scripts/logs.py --pod <pod-name> --namespace <namespace> [--tail 50]
```
Retrieves logs from running or failed pods.

### 6. Troubleshoot Deployments
```bash
python scripts/troubleshoot.py --namespace <namespace>
```
Automated troubleshooting of common deployment issues.

## Validation

After operations, verify:
- [ ] Cluster is accessible: `kubectl cluster-info`
- [ ] Namespaces exist and are Active
- [ ] Pods are Running or Completed (check with `status.py`)
- [ ] Services have endpoints
- [ ] No CrashLoopBackOff or ImagePullBackOff errors

## Common Issues

| Issue | Script | Solution |
|-------|--------|----------|
| Cluster not accessible | `cluster_health.py` | Check kubectl config, cluster running |
| Pods pending | `troubleshoot.py` | Check resource quotas, node capacity |
| Pods failing | `logs.py` | Check pod logs for errors |
| Service not routing | `status.py` | Verify service selectors match pod labels |

## Official Documentation

- Kubernetes Docs: https://kubernetes.io/docs/home/
- kubectl Cheat Sheet: https://kubernetes.io/docs/reference/kubectl/cheatsheet/
- Minikube Docs: https://minikube.sigs.k8s.io/docs/
