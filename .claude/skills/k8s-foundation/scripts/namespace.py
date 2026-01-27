#!/usr/bin/env python3
"""
Create or verify Kubernetes namespace.
Returns minimal status summary.
"""

import subprocess
import sys
import argparse

def manage_namespace(name, create=False):
    """Create namespace if it doesn't exist, or verify existing."""
    try:
        # Check if namespace exists
        result = subprocess.run(
            ["kubectl", "get", "namespace", name],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            print(f"✓ Namespace '{name}' exists")
            return 0

        # Namespace doesn't exist
        if not create:
            print(f"❌ Namespace '{name}' not found")
            print(f"→ Create with: python scripts/namespace.py --name {name} --create")
            return 1

        # Create namespace
        result = subprocess.run(
            ["kubectl", "create", "namespace", name],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            print(f"❌ Failed to create namespace '{name}'")
            print(f"→ Error: {result.stderr.strip()}")
            return 1

        print(f"✓ Namespace '{name}' created")
        return 0

    except subprocess.TimeoutExpired:
        print(f"❌ Timeout managing namespace")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage Kubernetes namespace")
    parser.add_argument("--name", required=True, help="Namespace name")
    parser.add_argument("--create", action="store_true", help="Create if doesn't exist")
    args = parser.parse_args()

    sys.exit(manage_namespace(args.name, args.create))
