#!/usr/bin/env python3
"""Deploy Kong API Gateway to Kubernetes."""
import subprocess, sys, argparse

def deploy_kong(namespace, database="postgres"):
    """Deploy Kong using Helm."""

    # Check helm installed
    result = subprocess.run(["which", "helm"], capture_output=True)
    if result.returncode != 0:
        print("❌ Helm not installed")
        print("→ Install: https://helm.sh/docs/intro/install/")
        return 1

    # Check kubectl
    result = subprocess.run(["which", "kubectl"], capture_output=True)
    if result.returncode != 0:
        print("❌ kubectl not installed")
        return 1

    # Create namespace
    subprocess.run(
        ["kubectl", "create", "namespace", namespace],
        capture_output=True
    )

    print(f"→ Deploying Kong to namespace '{namespace}'...")

    # Add Kong Helm repo
    result = subprocess.run(
        ["helm", "repo", "add", "kong", "https://charts.konghq.com"],
        capture_output=True,
        text=True
    )

    # Update repo
    subprocess.run(
        ["helm", "repo", "update"],
        capture_output=True
    )

    print(f"  ✓ Kong Helm repo added")

    # Install Kong
    helm_values = [
        "--set", "ingressController.enabled=true",
        "--set", "ingressController.installCRDs=false",
        "--set", "proxy.type=LoadBalancer",
    ]

    if database == "postgres":
        helm_values.extend([
            "--set", "env.database=postgres",
            "--set", "env.pg_host=postgres.default.svc.cluster.local",
            "--set", "env.pg_port=5432",
            "--set", "env.pg_user=kong",
            "--set", "env.pg_password=kong",
            "--set", "env.pg_database=kong",
        ])
    else:
        # DB-less mode
        helm_values.extend([
            "--set", "env.database=off",
        ])

    result = subprocess.run(
        ["helm", "install", "kong", "kong/kong", "-n", namespace] + helm_values,
        capture_output=True,
        text=True,
        timeout=300
    )

    if result.returncode != 0:
        if "already exists" in result.stderr:
            print(f"  ⚠ Kong already installed, upgrading...")
            result = subprocess.run(
                ["helm", "upgrade", "kong", "kong/kong", "-n", namespace] + helm_values,
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode != 0:
                print(f"❌ Upgrade failed: {result.stderr.strip()}")
                return 1
        else:
            print(f"❌ Installation failed: {result.stderr.strip()}")
            return 1

    print(f"\n✓ Kong deployed to '{namespace}'")

    # Wait for pods
    import time
    time.sleep(3)

    # Check status
    result = subprocess.run(
        ["kubectl", "get", "pods", "-n", namespace, "-l", "app.kubernetes.io/name=kong"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print(f"\n→ Pod status:")
        for line in result.stdout.strip().split('\n'):
            print(f"  {line}")

    # Get proxy service
    result = subprocess.run(
        ["kubectl", "get", "svc", "-n", namespace, "kong-kong-proxy", "-o", "jsonpath={.spec.type}"],
        capture_output=True,
        text=True
    )

    service_type = result.stdout.strip() if result.returncode == 0 else "Unknown"

    print(f"\n→ Access Kong:")
    print(f"  Service type: {service_type}")

    if service_type == "LoadBalancer":
        print(f"  Get external IP: kubectl get svc -n {namespace} kong-kong-proxy")
    else:
        print(f"  Port-forward: kubectl port-forward -n {namespace} svc/kong-kong-proxy 8000:80")

    print(f"\n→ Admin API:")
    print(f"  kubectl port-forward -n {namespace} svc/kong-kong-admin 8001:8001")

    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--namespace", default="kong", help="Kubernetes namespace")
    parser.add_argument("--database", default="postgres", choices=["postgres", "dbless"],
                       help="Kong database mode")
    args = parser.parse_args()
    sys.exit(deploy_kong(args.namespace, args.database))
