#!/usr/bin/env python3
"""
Check Kubernetes cluster health and connectivity.
Returns minimal status summary.
"""

import subprocess
import sys
import json

def check_cluster_health():
    """Check cluster connectivity and node status."""
    try:
        # Check cluster-info
        result = subprocess.run(
            ["kubectl", "cluster-info"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            print(f"❌ Cluster not accessible")
            print(f"→ Check: kubectl config current-context")
            print(f"→ Ensure: Cluster is running (minikube status / kubectl get nodes)")
            return 1

        # Check nodes
        result = subprocess.run(
            ["kubectl", "get", "nodes", "-o", "json"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            print(f"❌ Cannot get node status")
            return 1

        nodes = json.loads(result.stdout)
        total_nodes = len(nodes.get("items", []))
        ready_nodes = sum(
            1 for node in nodes.get("items", [])
            if any(
                cond["type"] == "Ready" and cond["status"] == "True"
                for cond in node.get("status", {}).get("conditions", [])
            )
        )

        # Check system pods
        result = subprocess.run(
            ["kubectl", "get", "pods", "-n", "kube-system", "-o", "json"],
            capture_output=True,
            text=True,
            timeout=10
        )

        system_pods_healthy = False
        if result.returncode == 0:
            pods = json.loads(result.stdout)
            total = len(pods.get("items", []))
            running = sum(
                1 for pod in pods.get("items", [])
                if pod.get("status", {}).get("phase") == "Running"
            )
            system_pods_healthy = (running == total and total > 0)

        # Summary output (minimal)
        print(f"✓ Cluster accessible")
        print(f"✓ Nodes: {ready_nodes}/{total_nodes} ready")
        if system_pods_healthy:
            print(f"✓ System pods: healthy")
        else:
            print(f"⚠ System pods: check kube-system namespace")

        return 0

    except subprocess.TimeoutExpired:
        print(f"❌ Timeout connecting to cluster")
        print(f"→ Check: Cluster is running and accessible")
        return 1
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing kubectl output: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(check_cluster_health())
