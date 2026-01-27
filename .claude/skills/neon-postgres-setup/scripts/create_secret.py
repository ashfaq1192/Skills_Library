#!/usr/bin/env python3
"""Create Kubernetes secret with Neon database credentials."""
import subprocess, sys, argparse, base64

def create_secret(namespace, connection_string, secret_name="postgres-credentials"):
    # Verify kubectl is available
    result = subprocess.run(["which", "kubectl"], capture_output=True)
    if result.returncode != 0:
        print("❌ kubectl not installed")
        print("→ Install: https://kubernetes.io/docs/tasks/tools/")
        return 1

    # Create namespace if it doesn't exist
    subprocess.run(
        ["kubectl", "create", "namespace", namespace],
        capture_output=True
    )

    # Delete existing secret if present
    subprocess.run(
        ["kubectl", "delete", "secret", secret_name, "-n", namespace],
        capture_output=True
    )

    # Create secret with connection string
    result = subprocess.run(
        [
            "kubectl", "create", "secret", "generic", secret_name,
            "-n", namespace,
            f"--from-literal=DATABASE_URL={connection_string}"
        ],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"❌ Failed to create secret: {result.stderr.strip()}")
        return 1

    print(f"✓ Kubernetes secret created: {secret_name}")
    print(f"  Namespace: {namespace}")
    print(f"\n→ Use in pod spec:")
    print(f"  env:")
    print(f"    - name: DATABASE_URL")
    print(f"      valueFrom:")
    print(f"        secretKeyRef:")
    print(f"          name: {secret_name}")
    print(f"          key: DATABASE_URL")
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--namespace", required=True, help="Kubernetes namespace")
    parser.add_argument("--connection-string", required=True, help="Neon connection string")
    parser.add_argument("--secret-name", default="postgres-credentials", help="Secret name")
    args = parser.parse_args()
    sys.exit(create_secret(args.namespace, args.connection_string, args.secret_name))
