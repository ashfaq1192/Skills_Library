#!/usr/bin/env python3
"""Configure Dapr components for LearnFlow (state store and pub/sub)."""
import subprocess, sys, argparse
from pathlib import Path

# State store component (PostgreSQL)
STATESTORE_YAML = """apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    secretKeyRef:
      name: postgres-credentials
      key: DATABASE_URL
"""

# Pub/Sub component (Kafka)
PUBSUB_YAML = """apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka.kafka.svc.cluster.local:9092"
  - name: consumerGroup
    value: "learnflow"
  - name: authType
    value: "none"
"""

def configure_components(namespace):
    # Verify namespace exists
    result = subprocess.run(
        ["kubectl", "get", "namespace", namespace],
        capture_output=True
    )

    if result.returncode != 0:
        print(f"❌ Namespace '{namespace}' does not exist")
        print(f"→ Create namespace: kubectl create namespace {namespace}")
        return 1

    # Create temporary files
    temp_dir = Path("/tmp/dapr-components")
    temp_dir.mkdir(exist_ok=True)

    statestore_file = temp_dir / "statestore.yaml"
    pubsub_file = temp_dir / "pubsub.yaml"

    statestore_file.write_text(STATESTORE_YAML)
    pubsub_file.write_text(PUBSUB_YAML)

    # Apply state store component
    result = subprocess.run(
        ["kubectl", "apply", "-f", str(statestore_file), "-n", namespace],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"❌ Failed to create statestore component: {result.stderr.strip()}")
        return 1

    print(f"✓ Statestore component configured")
    print(f"  Type: state.postgresql")
    print(f"  Name: statestore")

    # Apply pub/sub component
    result = subprocess.run(
        ["kubectl", "apply", "-f", str(pubsub_file), "-n", namespace],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"❌ Failed to create pubsub component: {result.stderr.strip()}")
        return 1

    print(f"✓ Pub/Sub component configured")
    print(f"  Type: pubsub.kafka")
    print(f"  Name: pubsub")

    # Verify components
    result = subprocess.run(
        ["kubectl", "get", "components", "-n", namespace],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        lines = result.stdout.strip().split('\n')
        print(f"\n✓ Components created: {len(lines)-1} in namespace '{namespace}'")
        print(f"\n→ Services can now use:")
        print(f"  - State API: http://localhost:3500/v1.0/state/statestore")
        print(f"  - Pub/Sub API: http://localhost:3500/v1.0/publish/pubsub/<topic>")
    else:
        print(f"\n⚠ Could not verify components")

    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--namespace", required=True, help="Kubernetes namespace for components")
    args = parser.parse_args()
    sys.exit(configure_components(args.namespace))
