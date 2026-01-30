# Kafka Kubernetes Setup - Reference Documentation

**Version**: 1.0.0
**Created**: 2026-01-27
**Purpose**: Deploy Apache Kafka on Kubernetes with event-driven topics for LearnFlow

## Overview

The `kafka-k8s-setup` skill deploys a production-ready Apache Kafka cluster on Kubernetes using Helm charts, creates application topics, and verifies cluster health. It follows the MCP Code Execution pattern: scripts handle all Helm/kubectl operations and return minimal status output.

### Key Features

- **Helm-Based Deployment**: Uses Bitnami Kafka chart for production-ready setup
- **Configurable Brokers**: 1-5+ broker replicas for dev through production
- **Auto Topic Creation**: Creates LearnFlow event topics with partitions and replication
- **Health Verification**: Checks broker readiness, Zookeeper status, and connectivity
- **Cross-Agent Compatible**: Works with both Claude Code and Goose

## Architecture

```
                    Kubernetes Cluster
    ┌──────────────────────────────────────────┐
    │  Namespace: learnflow (or custom)        │
    │                                          │
    │  ┌──────────┐  ┌──────────┐  ┌────────┐ │
    │  │ Kafka    │  │ Kafka    │  │ Kafka  │ │
    │  │ Broker 0 │  │ Broker 1 │  │ Broker │ │
    │  │ :9092    │  │ :9092    │  │ 2:9092 │ │
    │  └────┬─────┘  └────┬─────┘  └───┬────┘ │
    │       └──────────────┼────────────┘      │
    │              ┌───────▼────────┐          │
    │              │   Zookeeper    │          │
    │              │   :2181        │          │
    │              └────────────────┘          │
    └──────────────────────────────────────────┘
```

### LearnFlow Topics

| Topic | Purpose | Partitions | Replication |
|-------|---------|------------|-------------|
| `learning.events` | Student learning activities | 3 | 2 |
| `code.submitted` | Code submissions for execution | 3 | 2 |
| `struggle.detected` | AI-detected student struggles | 3 | 2 |

## Components

### 1. deploy_kafka.py

Deploys Kafka cluster using Helm.

```bash
python scripts/deploy_kafka.py [OPTIONS]

Options:
  --namespace TEXT    Target namespace (default: learnflow)
  --brokers INT      Number of broker replicas (default: 3)

Exit Codes:
  0 - Deployment successful
  1 - Helm not installed or deployment failed
```

**What It Does:**
1. Verifies Helm 3 is installed
2. Adds Bitnami Helm repository
3. Creates target namespace (idempotent)
4. Installs Kafka chart with Zookeeper and persistence (8Gi per broker)
5. Waits for pods to reach Ready state
6. Reports running/total pod counts

### 2. check_kafka.py

Verifies Kafka cluster health.

```bash
python scripts/check_kafka.py [OPTIONS]

Options:
  --namespace TEXT    Namespace to check (default: learnflow)

Exit Codes:
  0 - Cluster healthy
  1 - Issues detected (CrashLoopBackOff, missing services, etc.)
```

**What It Does:**
1. Queries Kafka pod status via kubectl JSON output
2. Checks Zookeeper pod status
3. Verifies Kafka service exists
4. Identifies unhealthy pods (CrashLoopBackOff, ImagePullBackOff)
5. Reports critical issues and warnings

### 3. create_topics.py

Creates LearnFlow event topics.

```bash
python scripts/create_topics.py [OPTIONS]

Options:
  --namespace TEXT    Kafka namespace (default: learnflow)

Exit Codes:
  0 - Topics created successfully
  1 - Failed to create topics (broker not reachable)
```

**What It Does:**
1. Finds first available Kafka broker pod
2. Executes `kafka-topics.sh` via kubectl exec
3. Creates 3 topics: learning.events, code.submitted, struggle.detected
4. Handles existing topics gracefully (no error on duplicate)
5. Reports per-topic status

## Configuration

### Default Helm Values

```yaml
replicaCount: 3            # Broker count
zookeeper:
  replicaCount: 1          # Single Zookeeper for dev
persistence:
  enabled: true
  size: 8Gi                # Storage per broker
```

### Custom Values

Create `templates/kafka-values.yaml` to override defaults:

```yaml
replicaCount: 1            # Dev: single broker
persistence:
  enabled: false           # Dev: no persistent storage
resources:
  requests:
    memory: 512Mi
    cpu: 250m
  limits:
    memory: 1Gi
    cpu: 500m
```

### Topic Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| Partitions | 3 | Parallelism per topic |
| Replication Factor | 2 | Data redundancy |
| Retention | 7 days | Message retention period |

## Usage

### Single Command Workflow

```bash
python .claude/skills/kafka-k8s-setup/scripts/deploy_kafka.py --namespace learnflow && \
python .claude/skills/kafka-k8s-setup/scripts/check_kafka.py --namespace learnflow && \
python .claude/skills/kafka-k8s-setup/scripts/create_topics.py --namespace learnflow
```

### With Claude Code or Goose

```bash
"Use kafka-k8s-setup to deploy Kafka with 3 brokers in the learnflow namespace"
```

### Development (Minimal Resources)

```bash
python scripts/deploy_kafka.py --namespace learnflow --brokers 1
```

## Integration with Dapr

Kafka connects to Dapr pub/sub via the `pubsub` component:

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
    value: "kafka-0.kafka-headless.learnflow.svc.cluster.local:9092"
  - name: consumerGroup
    value: "learnflow"
```

## Resource Requirements

| Component | CPU Request | Memory Request | Storage |
|-----------|-------------|----------------|---------|
| Kafka Broker (x3) | 250m each | 512Mi each | 8Gi each |
| Zookeeper | 100m | 256Mi | 2Gi |
| **Total** | **850m** | **1.8Gi** | **26Gi** |

### Minikube Minimum

```bash
minikube start --cpus=4 --memory=8192 --driver=docker
```

## Troubleshooting

### Pods Stuck in Pending

**Cause**: Insufficient resources or no storage class
```bash
kubectl describe pod <kafka-pod> -n learnflow
kubectl get pvc -n learnflow
kubectl get storageclass
```
**Fix**: Reduce brokers (`--brokers 1`) or disable persistence

### Broker Not Ready

**Cause**: Zookeeper not reachable or JVM out of memory
```bash
kubectl logs kafka-0 -n learnflow
kubectl logs kafka-zookeeper-0 -n learnflow
```
**Fix**: Check Zookeeper health first, adjust JVM heap settings

### Topic Creation Fails

**Cause**: No running broker pod found
```bash
kubectl get pods -n learnflow -l app.kubernetes.io/name=kafka
```
**Fix**: Wait for at least one broker to be Running, then retry

### Connection Refused from Services

**Cause**: Network policy or wrong broker address
```bash
kubectl get svc -n learnflow | grep kafka
kubectl run test-kafka --rm -it --image=bitnami/kafka -- \
  kafka-console-producer.sh --broker-list kafka.learnflow.svc.cluster.local:9092 --topic test
```

## Security Considerations

- **Default**: No authentication (suitable for development)
- **Production**: Enable SASL/SCRAM and TLS in Helm values
- **Network**: Use Kubernetes NetworkPolicies to restrict access
- **Secrets**: Store credentials in Kubernetes Secrets, not environment variables

## References

- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Bitnami Kafka Helm Chart](https://github.com/bitnami/charts/tree/main/bitnami/kafka)
- [Strimzi Kafka Operator](https://strimzi.io/docs/)
- [Kafka on Kubernetes Best Practices](https://www.confluent.io/blog/kafka-on-kubernetes/)
