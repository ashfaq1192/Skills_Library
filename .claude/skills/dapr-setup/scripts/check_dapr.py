#!/usr/bin/env python3
"""Check Dapr installation and health."""
import subprocess, sys

def check_dapr():
    # Check CLI version
    result = subprocess.run(["dapr", "version"], capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ Dapr CLI not found")
        print("→ Install: python scripts/install_dapr_cli.py")
        return 1

    print("✓ Dapr CLI version:")
    for line in result.stdout.strip().split('\n')[:2]:
        print(f"  {line}")

    # Check Dapr status on K8s
    result = subprocess.run(
        ["dapr", "status", "-k"],
        capture_output=True, text=True, timeout=30
    )

    if result.returncode != 0:
        print("\n❌ Dapr not initialized on Kubernetes")
        print("→ Initialize: python scripts/init_dapr.py")
        return 1

    print("\n✓ Dapr control plane status:")
    lines = result.stdout.strip().split('\n')
    for line in lines:
        if 'NAME' in line or 'Running' in line or 'dapr-' in line:
            print(f"  {line}")

    # Check pods in detail
    result = subprocess.run(
        ["kubectl", "get", "pods", "-n", "dapr-system"],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        lines = [l for l in result.stdout.strip().split('\n') if 'Running' in l]
        total = len(lines)
        print(f"\n✓ Dapr pods: {total} running in dapr-system namespace")

        # Check for common components
        components = ['dapr-sidecar-injector', 'dapr-operator', 'dapr-placement', 'dapr-sentry']
        for component in components:
            found = any(component in l for l in lines)
            status = "✓" if found else "⚠"
            print(f"  {status} {component}")

        return 0
    else:
        print("\n⚠ Could not verify Dapr pods")
        return 1

if __name__ == "__main__":
    sys.exit(check_dapr())
