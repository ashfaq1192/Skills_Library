#!/usr/bin/env python3
"""Create Kafka topics for LearnFlow platform."""
import subprocess, sys, argparse

def create_topics(namespace):
    topics = [
        ("learning.events", 3, 2),
        ("code.submitted", 3, 2),
        ("struggle.detected", 3, 2)
    ]

    broker_pod = subprocess.run(
        ["kubectl", "get", "pods", "-n", namespace, "-l", "app.kubernetes.io/name=kafka",
         "-o", "jsonpath={.items[0].metadata.name}"],
        capture_output=True, text=True, timeout=10
    ).stdout.strip()

    if not broker_pod:
        print("❌ No Kafka broker pods found")
        return 1

    for topic, partitions, replication in topics:
        cmd = f"kafka-topics.sh --create --topic {topic} --partitions {partitions} --replication-factor {replication} --if-not-exists --bootstrap-server kafka:9092"
        result = subprocess.run(
            ["kubectl", "exec", "-it", broker_pod, "-n", namespace, "--", "sh", "-c", cmd],
            capture_output=True, timeout=15
        )
        if result.returncode == 0:
            print(f"✓ Topic '{topic}' created")
        else:
            print(f"⚠ Topic '{topic}' (may exist)")

    print(f"✓ Topics configured for LearnFlow")
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--namespace", default="learnflow")
    args = parser.parse_args()
    sys.exit(create_topics(args.namespace))
