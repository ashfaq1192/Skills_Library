#!/usr/bin/env python3
"""Initialize Dapr on Kubernetes cluster."""
import subprocess, sys, argparse

def init_dapr(namespace="dapr-system"):
    # Check if dapr CLI installed
    result = subprocess.run(["which", "dapr"], capture_output=True)
    if result.returncode != 0:
        print("❌ Dapr CLI not installed")
        print("→ Install: curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | /bin/bash")
        return 1

    # Initialize Dapr on K8s
    result = subprocess.run(
        ["dapr", "init", "--kubernetes", "--wait"],
        capture_output=True, text=True, timeout=300
    )

    if result.returncode != 0:
        print(f"❌ Dapr initialization failed: {result.stderr.strip()}")
        return 1

    print("✓ Dapr initialized on Kubernetes")
    print(f"  Namespace: {namespace}")

    # Verify components
    result = subprocess.run(
        ["kubectl", "get", "pods", "-n", "dapr-system"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        lines = result.stdout.strip().split('\n')
        print(f"  Components: {len(lines)-1} pods running")

    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--namespace", default="dapr-system")
    args = parser.parse_args()
    sys.exit(init_dapr(args.namespace))
