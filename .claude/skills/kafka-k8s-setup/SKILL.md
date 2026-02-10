---
name: kafka-k8s-setup
description: Deploy Apache Kafka on Kubernetes with Strimzi and KRaft
version: 2.0.0
---

# Kafka Kubernetes Setup

## When to Use
- Deploy Kafka for event-driven microservice communication
- Create Strimzi KafkaTopic resources with retention policies

## Prerequisites
- Kubernetes cluster running (`kubectl cluster-info`)
- Strimzi operator installed (or Helm 3)

## Instructions
1. Deploy: `python scripts/deploy_kafka.py --namespace kafka`
2. Verify: `python scripts/check_kafka.py --namespace kafka`
3. Topics: `python scripts/create_topics.py --namespace kafka --cluster learnflow-kafka`

## Validation
- [ ] Kafka cluster running in kafka namespace (KRaft mode, no ZooKeeper)
- [ ] Strimzi KafkaTopic CRDs created (learning-events, code-submitted, struggle-detected)
- [ ] Topics have 24h retention and delete cleanup policy
- [ ] Dapr pubsub component connects at bootstrap:9092

See [REFERENCE.md](./REFERENCE.md) for Strimzi config, topic naming, and Dapr integration.
