#!/usr/bin/env python3
"""
Deploy Kubernetes resources from manifest file.
Returns minimal deployment summary.
"""

import subprocess
import sys
import argparse
from pathlib import Path

def deploy_resources(file_path, namespace="default"):
    """Apply Kubernetes manifest with validation."""
    try:
        # Verify file exists
        manifest = Path(file_path)
        if not manifest.exists():
            print(f"❌ Manifest file not found: {file_path}")
            return 1

        # Apply manifest
        cmd = ["kubectl", "apply", "-f", file_path]
        if namespace != "default":
            cmd.extend(["-n", namespace])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            print(f"❌ Deployment failed")
            print(f"→ Error: {result.stderr.strip()}")
            return 1

        # Parse output to count resources
        output_lines = result.stdout.strip().split('\n')
        created = sum(1 for line in output_lines if 'created' in line.lower())
        configured = sum(1 for line in output_lines if 'configured' in line.lower())
        unchanged = sum(1 for line in output_lines if 'unchanged' in line.lower())

        print(f"✓ Deployment successful: {manifest.name}")
        if created > 0:
            print(f"  Created: {created} resource(s)")
        if configured > 0:
            print(f"  Configured: {configured} resource(s)")
        if unchanged > 0:
            print(f"  Unchanged: {unchanged} resource(s)")

        return 0

    except subprocess.TimeoutExpired:
        print(f"❌ Deployment timeout (>30s)")
        print(f"→ Check: Large resources or cluster connectivity issues")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy Kubernetes resources")
    parser.add_argument("--file", required=True, help="Manifest file path")
    parser.add_argument("--namespace", default="default", help="Target namespace")
    args = parser.parse_args()

    sys.exit(deploy_resources(args.file, args.namespace))
