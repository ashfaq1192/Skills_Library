#!/usr/bin/env python3
"""
Check status of Kubernetes resources.
Returns minimal status summary.
"""

import subprocess
import sys
import argparse
import json

def check_status(namespace, resource_type="pods"):
    """Check status of specified resources."""
    try:
        # Get resources
        result = subprocess.run(
            ["kubectl", "get", resource_type, "-n", namespace, "-o", "json"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            print(f"❌ Cannot get {resource_type} in namespace '{namespace}'")
            print(f"→ Check: Namespace exists and has resources")
            return 1

        data = json.loads(result.stdout)
        items = data.get("items", [])

        if not items:
            print(f"⚠ No {resource_type} found in namespace '{namespace}'")
            return 0

        # Analyze status based on resource type
        if resource_type == "pods" or resource_type == "pod":
            running = sum(1 for item in items if item.get("status", {}).get("phase") == "Running")
            pending = sum(1 for item in items if item.get("status", {}).get("phase") == "Pending")
            failed = sum(1 for item in items if item.get("status", {}).get("phase") == "Failed")
            total = len(items)

            print(f"✓ Pods in '{namespace}':")
            print(f"  Running: {running}/{total}")
            if pending > 0:
                print(f"  Pending: {pending} (may be starting)")
            if failed > 0:
                print(f"  Failed: {failed} (check logs)")

            # Check for problem pods
            problems = [
                item["metadata"]["name"]
                for item in items
                if item.get("status", {}).get("phase") in ["Failed", "Unknown"]
                or any(
                    cs.get("state", {}).get("waiting", {}).get("reason") in
                    ["CrashLoopBackOff", "ImagePullBackOff", "ErrImagePull"]
                    for cs in item.get("status", {}).get("containerStatuses", [])
                )
            ]

            if problems:
                print(f"  ⚠ Problem pods: {', '.join(problems[:3])}")
                if len(problems) > 3:
                    print(f"    ... and {len(problems) - 3} more")

        elif resource_type in ["deployments", "deployment"]:
            total = len(items)
            ready = sum(
                1 for item in items
                if item.get("status", {}).get("availableReplicas", 0) ==
                   item.get("spec", {}).get("replicas", 0)
            )
            print(f"✓ Deployments in '{namespace}': {ready}/{total} ready")

        elif resource_type in ["services", "service", "svc"]:
            total = len(items)
            print(f"✓ Services in '{namespace}': {total} found")

        else:
            total = len(items)
            print(f"✓ {resource_type} in '{namespace}': {total} found")

        return 0

    except json.JSONDecodeError as e:
        print(f"❌ Error parsing kubectl output: {e}")
        return 1
    except subprocess.TimeoutExpired:
        print(f"❌ Timeout checking status")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check Kubernetes resource status")
    parser.add_argument("--namespace", required=True, help="Namespace to check")
    parser.add_argument("--resource", default="pods", help="Resource type (pods, deployments, services, etc.)")
    args = parser.parse_args()

    sys.exit(check_status(args.namespace, args.resource))
