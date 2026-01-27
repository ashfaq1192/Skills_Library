---
name: dapr-setup
description: |
  Install Dapr runtime on Kubernetes for service mesh capabilities. This skill should
  be used when setting up distributed application runtime, enabling state management,
  pub/sub messaging, service invocation, and observability for microservices.
---

# Dapr Setup

Install and configure Dapr (Distributed Application Runtime) on Kubernetes cluster.

## When to Use

- Enable service mesh for microservices
- Add state management to stateless applications
- Configure pub/sub messaging between services
- Enable service-to-service invocation
- Add observability to distributed applications

## Prerequisites

- Kubernetes cluster running and accessible
- Tools installed:
  ```bash
  # Verify kubectl
  kubectl version --client

  # Verify Helm 3
  helm version
  ```
- Cluster admin permissions (for CRD installation)
- PostgreSQL and Kafka already deployed (for component configuration)

## Before Implementation

Gather context to ensure successful Dapr setup:

| Source | Gather |
|--------|--------|
| **Cluster** | Kubernetes version, existing Dapr installation, available resources |
| **User** | Target namespace for applications, state store choice, pub/sub choice |
| **Dependencies** | PostgreSQL connection details, Kafka broker addresses |

## Required Clarifications

1. **Dapr Installation Check**: Is Dapr already installed on this cluster?
   - Check: `dapr status -k`
   - If yes: Skip installation, proceed to component configuration
   - If no: Install Dapr control plane

2. **Application Namespace**: Which namespace will run your Dapr-enabled applications?
   - Default: Use "learnflow" or user-specified namespace
   - Verify: Namespace should exist or will be created

3. **State Store**: What should Dapr use for state management?
   - PostgreSQL (recommended): Requires connection string
   - Redis: Requires Redis deployment
   - In-memory: Dev only, not for production

4. **Pub/Sub**: What should Dapr use for messaging?
   - Kafka (recommended): Requires broker addresses
   - Redis: Requires Redis deployment
   - In-memory: Dev only, not for production

## Instructions

### 1. Install Dapr CLI
```bash
python scripts/install_dapr_cli.py
```
Downloads and installs Dapr CLI.

### 2. Initialize Dapr on K8s
```bash
python scripts/init_dapr.py --namespace dapr-system
```
Deploys Dapr control plane to Kubernetes.

### 3. Verify Installation
```bash
python scripts/check_dapr.py
```
Checks Dapr components and health.

### 4. Configure Components
```bash
python scripts/configure_components.py --namespace <app-namespace>
```
Creates Dapr components for state store (PostgreSQL) and pub/sub (Kafka).

## Validation

- [ ] Dapr CLI installed: `dapr version`
- [ ] Dapr control plane running: `kubectl get pods -n dapr-system`
- [ ] Components configured: `kubectl get components -n <namespace>`

## Troubleshooting

- **Sidecar not injecting**: Check annotations on deployment, verify Dapr installed
- **Component not found**: Verify component created in same namespace as application
- **mTLS errors**: Check Sentry service running in dapr-system namespace
- **High latency**: Check sidecar resource limits, consider increasing CPU/memory

## Official Documentation

- Dapr Docs: https://docs.dapr.io/
- Dapr Components: https://docs.dapr.io/reference/components-reference/
- Dapr Best Practices: https://docs.dapr.io/operations/best-practices/
- REFERENCE.md in this skill directory for comprehensive guide
