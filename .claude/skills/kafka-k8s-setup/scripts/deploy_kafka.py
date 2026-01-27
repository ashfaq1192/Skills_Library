#!/usr/bin/env python3
"""
Deploy Apache Kafka on Kubernetes using Helm.
Returns minimal deployment summary.
"""

import subprocess
import sys
import argparse
import time
from pathlib import Path

def deploy_kafka(namespace, brokers=3):
    """Deploy Kafka cluster using Helm."""
    try:
        # Check if helm is installed
        result = subprocess.run(["helm", "version"], capture_output=True, timeout=5)
        if result.returncode != 0:
            print("❌ Helm not installed")
            print("→ Install: https://helm.sh/docs/intro/install/")
            return 1

        # Add bitnami repo if not present
        print("→ Adding Bitnami Helm repository...")
        subprocess.run(
            ["helm", "repo", "add", "bitnami", "https://charts.bitnami.com/bitnami"],
            capture_output=True,
            timeout=30
        )
        subprocess.run(
            ["helm", "repo", "update"],
            capture_output=True,
            timeout=30
        )

        # Check if namespace exists
        result = subprocess.run(
            ["kubectl", "get", "namespace", namespace],
            capture_output=True,
            timeout=5
        )
        if result.returncode != 0:
            print(f"→ Creating namespace '{namespace}'...")
            result = subprocess.run(
                ["kubectl", "create", "namespace", namespace],
                capture_output=True,
                timeout=10
            )
            if result.returncode != 0:
                print(f"❌ Cannot create namespace: {result.stderr.decode().strip()}")
                return 1

        # Load values file if exists
        values_file = Path(__file__).parent.parent / "templates" / "kafka-values.yaml"

        # Deploy Kafka
        print(f"→ Deploying Kafka with {brokers} brokers...")
        cmd = [
            "helm", "install", "kafka",
            "bitnami/kafka",
            "--namespace", namespace,
            "--set", f"replicaCount={brokers}",
            "--set", "zookeeper.enabled=true",
            "--set", "persistence.enabled=true",
            "--set", "persistence.size=8Gi",
            "--wait",
            "--timeout", "10m"
        ]

        if values_file.exists():
            cmd.extend(["-f", str(values_file)])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        if result.returncode != 0:
            # Check if already installed
            if "already exists" in result.stderr:
                print("⚠ Kafka already installed")
                print("→ Upgrade: helm upgrade kafka bitnami/kafka -n", namespace)
                return 0
            print(f"❌ Kafka deployment failed")
            print(f"→ Error: {result.stderr.strip()}")
            return 1

        print(f"✓ Kafka deployed successfully")
        print(f"  Brokers: {brokers}")
        print(f"  Namespace: {namespace}")
        print(f"  Release: kafka")

        # Wait for pods to be ready
        print("→ Waiting for pods to be ready...")
        time.sleep(10)

        result = subprocess.run(
            ["kubectl", "get", "pods", "-n", namespace, "-l", "app.kubernetes.io/name=kafka"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            running = sum(1 for line in lines[1:] if 'Running' in line)
            print(f"✓ Kafka pods: {running}/{brokers} running")

        return 0

    except subprocess.TimeoutExpired:
        print("❌ Deployment timeout")
        print("→ Check: kubectl get pods -n", namespace)
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy Kafka on Kubernetes")
    parser.add_argument("--namespace", default="learnflow", help="Target namespace")
    parser.add_argument("--brokers", type=int, default=3, help="Number of Kafka brokers")
    args = parser.parse_args()

    sys.exit(deploy_kafka(args.namespace, args.brokers))
