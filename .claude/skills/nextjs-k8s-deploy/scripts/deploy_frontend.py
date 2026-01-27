#!/usr/bin/env python3
"""Deploy Next.js frontend to Kubernetes."""
import subprocess, sys, argparse
from pathlib import Path

def deploy_frontend(namespace, manifests_dir=None, domain=None):
    """Deploy Next.js app to K8s."""

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

    # Find manifests
    if manifests_dir:
        manifests_path = Path(manifests_dir)
    else:
        manifests_path = Path("./k8s-manifests")

    if not manifests_path.exists():
        print(f"❌ Manifests directory not found: {manifests_path}")
        print(f"→ Generate first: python scripts/generate_manifests.py")
        return 1

    print(f"→ Deploying Next.js frontend to '{namespace}'...")

    # Apply all manifests
    for manifest in manifests_path.glob("*.yaml"):
        result = subprocess.run(
            ["kubectl", "apply", "-f", str(manifest), "-n", namespace],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"❌ Failed to apply {manifest.name}: {result.stderr.strip()}")
            return 1

        print(f"  ✓ Applied: {manifest.name}")

    print(f"\n✓ Frontend deployed to namespace '{namespace}'")

    # Wait for pods
    import time
    time.sleep(2)

    # Check deployment status
    result = subprocess.run(
        ["kubectl", "get", "pods", "-n", namespace, "-l", "app=frontend"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print(f"\n→ Pod status:")
        for line in result.stdout.strip().split('\n'):
            print(f"  {line}")

    # Show access instructions
    print(f"\n→ Access frontend:")

    if domain:
        print(f"  External: http://{domain}")
    else:
        print(f"  Port-forward: kubectl port-forward -n {namespace} svc/frontend 3000:80")
        print(f"  Then open: http://localhost:3000")

    print(f"\n→ Check logs:")
    print(f"  kubectl logs -n {namespace} -l app=frontend --tail=50")

    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--namespace", required=True, help="Kubernetes namespace")
    parser.add_argument("--manifests-dir", help="Manifests directory")
    parser.add_argument("--domain", help="Domain for access")
    args = parser.parse_args()
    sys.exit(deploy_frontend(args.namespace, args.manifests_dir, args.domain))
