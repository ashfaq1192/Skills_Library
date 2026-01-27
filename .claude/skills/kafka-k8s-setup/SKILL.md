---
name: kafka-k8s-setup
description: |
  Deploy Apache Kafka on Kubernetes with event-driven architecture topics. This skill
  should be used when setting up Kafka messaging infrastructure for microservices,
  creating pub/sub event streams, or building event-driven applications. Includes
  Zookeeper, Kafka brokers, and topic creation for LearnFlow platform.
---

# Kafka Kubernetes Setup

Deploy production-ready Apache Kafka cluster on Kubernetes with required topics for event-driven architecture.

## When to Use

- Deploy Kafka cluster for event streaming
- Set up pub/sub messaging for microservices
- Create Kafka topics for event-driven applications
- Configure Kafka for LearnFlow platform (learning events, code submission, struggle detection)

## Prerequisites

- Kubernetes cluster running: Use `k8s-foundation` skill to verify health
- kubectl configured: `kubectl cluster-info`
- Helm 3 installed: `helm version` (v3.0+)
- Target namespace exists: `kubectl create namespace learnflow` (default: `learnflow`)
- Sufficient cluster resources: 3 brokers need ~3GB RAM, 3 CPU cores

## Before Implementation

Gather context to ensure successful Kafka deployment:

| Source | Gather |
|--------|--------|
| **Cluster Resources** | Available nodes, CPU/memory capacity, storage classes |
| **Application Requirements** | Topic names, partition counts, retention policies |
| **Event Schema** | Event types (learning.events, code.submitted, struggle.detected) |
| **Integration Points** | Services that will produce/consume (Dapr sidecars, microservices) |

## Required Clarifications

1. **Deployment Scale**: What scale is needed for Kafka?
   - Development (1 broker, minimal resources)
   - Staging (2 brokers, moderate resources)
   - Production (3+ brokers, high availability, resource limits)

2. **Topic Configuration**: How should topics be configured?
   - Partition count per topic (affects parallelism)
   - Replication factor (2-3 for reliability)
   - Retention policy (time-based: 7 days, size-based: 1GB)
   - Cleanup policy (delete old messages vs compact)

3. **Storage Requirements**: What storage strategy is needed?
   - Persistent volumes (PVCs with storage class)
   - Ephemeral storage (fast but data loss on pod restart)
   - Storage size per broker (e.g., 10Gi, 50Gi)

4. **Security and Access**: What security is required?
   - No authentication (development only)
   - SASL/SCRAM authentication
   - TLS encryption for data in transit
   - ACLs for topic access control

## Instructions

### 1. Deploy Kafka Cluster
```bash
python scripts/deploy_kafka.py --namespace <namespace> --brokers 3
```
Deploys Kafka with Zookeeper using Helm. Creates 3 broker replicas by default.

### 2. Verify Kafka Health
```bash
python scripts/check_kafka.py --namespace <namespace>
```
Checks broker readiness, Zookeeper connectivity, and cluster health.

### 3. Create Application Topics
```bash
python scripts/create_topics.py --namespace <namespace> --config <topics-config.yaml>
```
Creates topics with specified partitions and replication. LearnFlow default topics:
- `learning.events` - Student learning activities
- `code.submitted` - Code submissions for execution
- `struggle.detected` - AI-detected student struggles

### 4. Test Kafka Connection
```bash
python scripts/test_kafka.py --namespace <namespace> --topic test-topic
```
Produces and consumes test message to verify functionality.

## Validation

After deployment, verify:
- [ ] Kafka pods running: `kubectl get pods -n <namespace> -l app.kubernetes.io/name=kafka`
- [ ] Zookeeper healthy: `kubectl get pods -n <namespace> -l app.kubernetes.io/name=zookeeper`
- [ ] Topics created: Use `scripts/list_topics.py`
- [ ] Message flow works: Use `scripts/test_kafka.py`

## Configuration

Default configuration (customizable via `templates/kafka-values.yaml`):
- **Brokers**: 3 replicas
- **Partitions**: 3 per topic
- **Replication Factor**: 2
- **Retention**: 7 days

For production: Adjust resources, enable auth (SASL/SSL), configure monitoring.

## Common Issues

| Issue | Solution |
|-------|----------|
| Pods pending | Check PVC storage class availability |
| Broker not ready | Check logs: `kubectl logs <pod> -n <namespace>` |
| Topic creation fails | Verify broker connectivity with `check_kafka.py` |
| Messages not flowing | Check network policies, service endpoints |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Pods stuck in Pending | Check PVC binding, storage class availability, node resources |
| Broker not ready | Review logs `kubectl logs <pod> -n <namespace>`, check Zookeeper |
| Topic creation timeout | Verify broker connectivity, check network policies |
| High resource usage | Adjust JVM heap settings, scale brokers, review topic configs |

## Official Documentation

- Apache Kafka: https://kafka.apache.org/documentation/
- Kafka on Kubernetes: https://strimzi.io/docs/operators/latest/overview.html
- Helm Charts: https://github.com/bitnami/charts/tree/main/bitnami/kafka
