#!/usr/bin/env python3
"""Deploy FastAPI service to Kubernetes."""
import subprocess, sys, argparse
from pathlib import Path

def deploy_service(service_dir, namespace):
    """Deploy service to Kubernetes with Dapr sidecar."""
    service_path = Path(service_dir)

    if not service_path.exists():
        print(f"❌ Service directory not found: {service_dir}")
        return 1

    k8s_dir = service_path / "k8s"
    if not k8s_dir.exists():
        print(f"❌ k8s/ directory not found")
        print(f"→ Configure first: python scripts/configure_dapr.py --service-dir {service_dir}")
        return 1

    # Verify kubectl
    result = subprocess.run(["which", "kubectl"], capture_output=True)
    if result.returncode != 0:
        print("❌ kubectl not installed")
        return 1

    # Create namespace if needed
    subprocess.run(
        ["kubectl", "create", "namespace", namespace],
        capture_output=True
    )

    # Get service name
    service_name = service_path.name

    print(f"→ Deploying {service_name} to namespace '{namespace}'...")

    # Apply all manifests in k8s/
    for manifest in k8s_dir.glob("*.yaml"):
        result = subprocess.run(
            ["kubectl", "apply", "-f", str(manifest), "-n", namespace],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"❌ Failed to apply {manifest.name}: {result.stderr.strip()}")
            return 1

        print(f"  ✓ Applied: {manifest.name}")

    print(f"\\n✓ Service deployed: {service_name}")
    print(f"  Namespace: {namespace}")

    # Wait a moment for pods to start
    import time
    time.sleep(2)

    # Check deployment status
    result = subprocess.run(
        ["kubectl", "get", "pods", "-n", namespace, "-l", f"app={service_name}"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print(f"\\n→ Pod status:")
        for line in result.stdout.strip().split('\\n'):
            print(f"  {line}")

    print(f"\\n→ Verify Dapr sidecar:")
    print(f"  kubectl logs -n {namespace} -l app={service_name} -c daprd --tail=10")
    print(f"\\n→ Test service:")
    print(f"  kubectl port-forward -n {namespace} svc/{service_name} 8000:80")
    print(f"  curl http://localhost:8000/health")

    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--service-dir", required=True, help="Service directory")
    parser.add_argument("--namespace", required=True, help="Kubernetes namespace")
    args = parser.parse_args()
    sys.exit(deploy_service(args.service_dir, args.namespace))
