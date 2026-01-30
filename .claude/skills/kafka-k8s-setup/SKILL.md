---
name: kafka-k8s-setup
description: Deploy Apache Kafka on Kubernetes
version: 1.0.0
---

# Kafka Kubernetes Setup

## When to Use
- Deploy Kafka for event streaming
- Create pub/sub topics for microservices

## Prerequisites
- Kubernetes cluster running (`kubectl cluster-info`)
- Helm 3 installed (`helm version`)

## Instructions
1. Deploy: `python scripts/deploy_kafka.py --namespace learnflow --brokers 3`
2. Verify: `python scripts/check_kafka.py --namespace learnflow`
3. Topics: `python scripts/create_topics.py --namespace learnflow`

## Validation
- [ ] Kafka pods running
- [ ] Zookeeper healthy
- [ ] Topics created (learning.events, code.submitted, struggle.detected)

See [REFERENCE.md](./REFERENCE.md) for configuration and troubleshooting.
