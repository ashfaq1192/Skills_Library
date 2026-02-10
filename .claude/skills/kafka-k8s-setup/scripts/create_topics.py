#!/usr/bin/env python3
"""Create Kafka topics using Strimzi KafkaTopic CRDs.

Matches actual LearnFlow production patterns:
- Strimzi KafkaTopic CRDs (declarative YAML) instead of imperative kafka-topics.sh
- Topic names use HYPHENS (learning-events), Dapr uses DOTS (learning.events) internally
- 24-hour retention with delete cleanup policy
- Single partition/replica for development (scalable for production)
- Kafka namespace separate from application namespace (learnflow)

Topic naming convention:
  Kafka topic name: learning-events (hyphenated)
  Dapr pub/sub topic: learning.events (dotted, mapped by Dapr)
"""
import subprocess, sys, argparse
from pathlib import Path

# LearnFlow Kafka topics - matches actual k8s/kafka/kafka-topics.yaml
LEARNFLOW_TOPICS = [
    {
        "name": "learning-events",
        "partitions": 1,
        "replicas": 1,
        "retention_ms": 86400000,  # 24 hours
        "dapr_topic": "learning.events",
        "description": "Learning events (triage, concepts, exercises, progress)",
    },
    {
        "name": "code-submitted",
        "partitions": 1,
        "replicas": 1,
        "retention_ms": 86400000,
        "dapr_topic": "code.submitted",
        "description": "Code submission events for execution and debugging",
    },
    {
        "name": "struggle-detected",
        "partitions": 1,
        "replicas": 1,
        "retention_ms": 86400000,
        "dapr_topic": "struggle.detected",
        "description": "Student struggle detection events for triage",
    },
]

KAFKA_TOPIC_CRD_TEMPLATE = '''apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: {name}
  namespace: {namespace}
  labels:
    strimzi.io/cluster: {cluster}
spec:
  partitions: {partitions}
  replicas: {replicas}
  config:
    retention.ms: {retention_ms}
    cleanup.policy: delete'''


def create_topics(namespace, cluster, output_dir=None):
    """Create Kafka topics using Strimzi KafkaTopic CRDs."""

    print(f"Creating Strimzi KafkaTopic resources...")
    print(f"  Namespace: {namespace}")
    print(f"  Cluster: {cluster}")

    # Generate KafkaTopic YAML
    topic_yamls = []
    for topic in LEARNFLOW_TOPICS:
        yaml_content = KAFKA_TOPIC_CRD_TEMPLATE.format(
            name=topic["name"],
            namespace=namespace,
            cluster=cluster,
            partitions=topic["partitions"],
            replicas=topic["replicas"],
            retention_ms=topic["retention_ms"],
        )
        topic_yamls.append(yaml_content)

    combined_yaml = "\n---\n".join(topic_yamls)

    # Write to file
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = Path(f"./k8s/kafka")

    output_path.mkdir(parents=True, exist_ok=True)
    topics_file = output_path / "kafka-topics.yaml"
    topics_file.write_text(combined_yaml + "\n")

    print(f"  Created: {topics_file}")

    # Apply to cluster
    try:
        result = subprocess.run(
            ["kubectl", "apply", "-f", str(topics_file)],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0:
            print(f"\n  Applied to cluster:")
            for line in result.stdout.strip().split("\n"):
                print(f"    {line}")
        else:
            print(f"\n  kubectl apply output: {result.stderr.strip()}")
            print(f"  You can apply manually: kubectl apply -f {topics_file}")
    except FileNotFoundError:
        print(f"\n  kubectl not found. Apply manually: kubectl apply -f {topics_file}")
    except Exception as e:
        print(f"\n  Could not apply: {e}")
        print(f"  Apply manually: kubectl apply -f {topics_file}")

    # Print summary
    print(f"\n✓ {len(LEARNFLOW_TOPICS)} KafkaTopic resources created")
    print(f"\n  Topic mapping (Kafka name -> Dapr pub/sub topic):")
    for topic in LEARNFLOW_TOPICS:
        print(f"    {topic['name']} -> {topic['dapr_topic']}  ({topic['description']})")

    print(f"\n  Retention: 24 hours | Cleanup: delete")
    print(f"  Bootstrap: {cluster}-kafka-bootstrap.{namespace}.svc.cluster.local:9092")

    print(f"\n  Dapr pubsub component connects to these topics via:")
    print(f"    brokers: {cluster}-kafka-bootstrap.{namespace}.svc.cluster.local:9092")
    print(f"    consumerGroup: learnflow-group")

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create LearnFlow Kafka topics via Strimzi CRDs")
    parser.add_argument("--namespace", default="kafka", help="Kafka namespace")
    parser.add_argument("--cluster", default="learnflow-kafka", help="Strimzi Kafka cluster name")
    parser.add_argument("--output", help="Output directory for topic YAML")
    args = parser.parse_args()
    sys.exit(create_topics(args.namespace, args.cluster, args.output))
