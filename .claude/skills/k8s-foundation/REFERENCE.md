# Kubernetes Foundation - Reference Documentation

**Version**: 1.0.0
**Created**: 2026-01-27
**Purpose**: Core Kubernetes operations for cluster management, deployments, and troubleshooting

## Overview

The `k8s-foundation` skill provides foundational Kubernetes operations that other infrastructure skills depend on. It handles cluster health checks, namespace management, resource deployment, status monitoring, log retrieval, and automated troubleshooting. All output is filtered to return minimal, actionable information.

### Key Features

- **Cluster Health**: Verify connectivity, node readiness, system pod status
- **Namespace Management**: Create/verify namespaces idempotently
- **Resource Deployment**: Apply manifests with change tracking
- **Status Monitoring**: Check pods, deployments, services with problem detection
- **Log Retrieval**: Tail pod logs with follow capability
- **Auto Troubleshoot**: Diagnose common issues with actionable recommendations
- **Cross-Agent Compatible**: Works with both Claude Code and Goose

## Architecture

```
k8s-foundation/
├── SKILL.md               # ~125 tokens
├── REFERENCE.md            # This file
└── scripts/
    ├── cluster_health.py   # Cluster connectivity and health
    ├── namespace.py        # Create/verify namespaces
    ├── deploy.py           # Apply K8s manifests
    ├── status.py           # Check resource status
    ├── logs.py             # Retrieve pod logs
    └── troubleshoot.py     # Automated diagnostics
```

## Components

### 1. cluster_health.py

Checks cluster connectivity and overall health.

```bash
python scripts/cluster_health.py

Arguments: None

Exit Codes:
  0 - Cluster healthy and accessible
  1 - Cluster not accessible or has issues
```

**Checks Performed:**
1. kubectl cluster-info (API server reachable)
2. Node status (Ready count vs total)
3. System pods in kube-system namespace (Running count)

### 2. namespace.py

Creates or verifies Kubernetes namespaces.

```bash
python scripts/namespace.py [OPTIONS]

Options:
  --name TEXT     Namespace name (required)
  --create        Create namespace if missing (flag)

Exit Codes:
  0 - Namespace exists/created
  1 - Namespace missing and --create not specified
```

### 3. deploy.py

Applies Kubernetes manifests with change tracking.

```bash
python scripts/deploy.py [OPTIONS]

Options:
  --file TEXT        Path to YAML manifest (required)
  --namespace TEXT   Target namespace (default: default)

Exit Codes:
  0 - Resources applied
  1 - Manifest not found or apply failed
```

**Output**: Reports created/configured/unchanged resource counts.

### 4. status.py

Checks status of Kubernetes resources with problem detection.

```bash
python scripts/status.py [OPTIONS]

Options:
  --namespace TEXT    Namespace to check (required)
  --resource TEXT     Resource type (default: pods)
                     Supported: pods, deployments, services, configmaps, secrets

Exit Codes:
  0 - Resources healthy
  1 - Issues detected
```

**Pod Analysis:**
- Groups by phase: Running, Pending, Failed, Succeeded
- Identifies problem pods: CrashLoopBackOff, ImagePullBackOff, ErrImagePull
- Reports container restart counts

**Deployment Analysis:**
- Ready vs desired replica counts
- Identifies deployments with unavailable replicas

### 5. logs.py

Retrieves logs from Kubernetes pods.

```bash
python scripts/logs.py [OPTIONS]

Options:
  --pod TEXT          Pod name (required)
  --namespace TEXT    Namespace (required)
  --tail INT         Lines to show (default: 50)
  --follow           Stream logs continuously (flag)

Exit Codes:
  0 - Logs retrieved
  1 - Pod not found or log retrieval failed
```

### 6. troubleshoot.py

Automated diagnostics for deployment issues.

```bash
python scripts/troubleshoot.py [OPTIONS]

Options:
  --namespace TEXT    Namespace to troubleshoot (required)

Exit Codes:
  0 - No issues found
  1 - Issues detected (with recommendations)
```

**Diagnostics Performed:**
1. Pod analysis: Pending conditions, Failed status, container wait states
2. Service verification: Endpoint availability
3. Issue categorization: Critical vs Warning
4. Recommendations based on detected issues

**Recommendations Generated:**
| Issue | Recommendation |
|-------|---------------|
| CrashLoopBackOff | Check logs, fix application errors |
| ImagePullBackOff | Verify image name, check registry access |
| Pending pods | Check resource quotas, node capacity |
| No endpoints | Verify service selector matches pod labels |

## Usage

### Full Health Check

```bash
python scripts/cluster_health.py && \
python scripts/namespace.py --name learnflow --create && \
python scripts/status.py --namespace learnflow
```

### Deploy and Verify

```bash
python scripts/deploy.py --file ./k8s/deployment.yaml --namespace learnflow && \
python scripts/status.py --namespace learnflow --resource pods && \
python scripts/status.py --namespace learnflow --resource services
```

### Diagnose Issues

```bash
python scripts/troubleshoot.py --namespace learnflow
python scripts/logs.py --pod <failing-pod> --namespace learnflow --tail 100
```

### With Claude Code or Goose

```bash
"Use k8s-foundation to check cluster health and create the learnflow namespace"
```

## Minikube Quick Start

```bash
# Start cluster with adequate resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Verify
python scripts/cluster_health.py

# Create application namespace
python scripts/namespace.py --name learnflow --create
```

## Common Kubernetes Patterns

### Deployment with Dapr Sidecar

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-service
  namespace: learnflow
spec:
  replicas: 3
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "my-service"
        dapr.io/app-port: "8000"
    spec:
      containers:
      - name: my-service
        image: my-service:latest
        ports:
        - containerPort: 8000
```

### Service with ClusterIP

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
  namespace: learnflow
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: my-service
```

## Troubleshooting

### Cluster Not Accessible

```bash
# Check minikube status
minikube status

# Check kubectl context
kubectl config current-context
kubectl config get-contexts

# Restart minikube if needed
minikube delete && minikube start --cpus=4 --memory=8192
```

### Pods Stuck in Pending

**Common Causes:**
1. Insufficient CPU/memory on nodes
2. PVC not bound (no storage class)
3. Node affinity/taint issues

```bash
kubectl describe pod <pod-name> -n <namespace>
kubectl get nodes -o wide
kubectl describe nodes
```

### CrashLoopBackOff

**Common Causes:**
1. Application error (check logs)
2. Missing environment variables
3. Config file not mounted

```bash
python scripts/logs.py --pod <pod> --namespace <ns> --tail 100
kubectl describe pod <pod> -n <ns>
```

### ImagePullBackOff

**Common Causes:**
1. Image not found in registry
2. Private registry without credentials
3. Minikube not configured for local images

```bash
# For Minikube: load image directly
eval $(minikube docker-env)
docker build -t my-image:latest .
# Set imagePullPolicy: Never in deployment
```

## Dependencies

| Tool | Minimum Version | Check Command |
|------|----------------|---------------|
| kubectl | v1.24+ | `kubectl version --client` |
| minikube | v1.30+ | `minikube version` |
| Python | 3.9+ | `python --version` |

## Security Considerations

- Use RBAC to limit kubectl access per namespace
- Never store kubeconfig in source control
- Use ServiceAccounts for pod-level access
- Enable NetworkPolicies for namespace isolation

## References

- [Kubernetes Documentation](https://kubernetes.io/docs/home/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
