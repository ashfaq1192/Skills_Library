#!/usr/bin/env python3
"""
Get logs from Kubernetes pods.
Returns filtered log output.
"""

import subprocess
import sys
import argparse

def get_logs(pod_name, namespace, tail=50, follow=False):
    """Retrieve logs from pod."""
    try:
        cmd = ["kubectl", "logs", pod_name, "-n", namespace]

        if tail:
            cmd.extend(["--tail", str(tail)])

        if follow:
            cmd.append("-f")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30 if not follow else None
        )

        if result.returncode != 0:
            print(f"❌ Cannot get logs for pod '{pod_name}'")
            print(f"→ Error: {result.stderr.strip()}")
            print(f"→ Check: Pod exists and is not in Pending state")
            return 1

        print(f"✓ Logs from pod '{pod_name}' (last {tail} lines):")
        print("-" * 60)
        print(result.stdout)
        print("-" * 60)

        return 0

    except subprocess.TimeoutExpired:
        print(f"❌ Timeout getting logs (>30s)")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get Kubernetes pod logs")
    parser.add_argument("--pod", required=True, help="Pod name")
    parser.add_argument("--namespace", required=True, help="Namespace")
    parser.add_argument("--tail", type=int, default=50, help="Number of lines to show")
    parser.add_argument("--follow", action="store_true", help="Follow log output")
    args = parser.parse_args()

    sys.exit(get_logs(args.pod, args.namespace, args.tail, args.follow))
