#!/usr/bin/env python3
"""
Check Kafka cluster health on Kubernetes.
Returns minimal health summary.
"""

import subprocess
import sys
import argparse
import json

def check_kafka(namespace):
    """Verify Kafka and Zookeeper health."""
    try:
        issues = []
        warnings = []

        # Check Kafka pods
        result = subprocess.run(
            ["kubectl", "get", "pods", "-n", namespace,
             "-l", "app.kubernetes.io/name=kafka", "-o", "json"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            print(f"❌ Cannot access Kafka pods in '{namespace}'")
            print("→ Check: kubectl get pods -n", namespace)
            return 1

        kafka_data = json.loads(result.stdout)
        kafka_pods = kafka_data.get("items", [])

        if not kafka_pods:
            print(f"❌ No Kafka pods found in namespace '{namespace}'")
            print("→ Deploy: python scripts/deploy_kafka.py --namespace", namespace)
            return 1

        kafka_running = sum(
            1 for pod in kafka_pods
            if pod.get("status", {}).get("phase") == "Running"
        )
        kafka_total = len(kafka_pods)

        # Check Zookeeper pods
        result = subprocess.run(
            ["kubectl", "get", "pods", "-n", namespace,
             "-l", "app.kubernetes.io/name=zookeeper", "-o", "json"],
            capture_output=True,
            text=True,
            timeout=10
        )

        zk_running = 0
        zk_total = 0
        if result.returncode == 0:
            zk_data = json.loads(result.stdout)
            zk_pods = zk_data.get("items", [])
            zk_total = len(zk_pods)
            zk_running = sum(
                1 for pod in zk_pods
                if pod.get("status", {}).get("phase") == "Running"
            )

        # Check Kafka service
        result = subprocess.run(
            ["kubectl", "get", "service", "kafka", "-n", namespace],
            capture_output=True,
            timeout=5
        )

        service_exists = (result.returncode == 0)

        # Print summary
        print(f"✓ Kafka Cluster Health: {namespace}")
        print(f"  Kafka Brokers: {kafka_running}/{kafka_total} running")

        if zk_total > 0:
            print(f"  Zookeeper: {zk_running}/{zk_total} running")
        else:
            warnings.append("Zookeeper pods not found")

        if service_exists:
            print(f"  Service: Available")
        else:
            warnings.append("Kafka service not found")

        # Check for unhealthy pods
        for pod in kafka_pods:
            pod_name = pod["metadata"]["name"]
            phase = pod.get("status", {}).get("phase", "Unknown")
            if phase != "Running":
                issues.append(f"Kafka pod '{pod_name}' in {phase} state")

        # Print issues and warnings
        if issues:
            print(f"\n❌ Issues:")
            for issue in issues:
                print(f"  • {issue}")

        if warnings:
            print(f"\n⚠ Warnings:")
            for warning in warnings:
                print(f"  • {warning}")

        if not issues and not warnings:
            print(f"\n✓ All systems healthy")
            return 0
        elif issues:
            return 1
        else:
            return 0

    except json.JSONDecodeError as e:
        print(f"❌ Error parsing kubectl output: {e}")
        return 1
    except subprocess.TimeoutExpired:
        print("❌ Timeout checking Kafka health")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check Kafka cluster health")
    parser.add_argument("--namespace", default="learnflow", help="Kafka namespace")
    args = parser.parse_args()

    sys.exit(check_kafka(args.namespace))
