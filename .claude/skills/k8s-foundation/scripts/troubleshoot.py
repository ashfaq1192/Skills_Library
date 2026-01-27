#!/usr/bin/env python3
"""
Automated troubleshooting of Kubernetes deployments.
Returns diagnostic summary and recommendations.
"""

import subprocess
import sys
import argparse
import json

def troubleshoot(namespace):
    """Run automated diagnostics on namespace."""
    try:
        issues = []
        warnings = []

        # Check pods
        result = subprocess.run(
            ["kubectl", "get", "pods", "-n", namespace, "-o", "json"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            print(f"❌ Cannot access namespace '{namespace}'")
            return 1

        pods = json.loads(result.stdout).get("items", [])

        if not pods:
            warnings.append(f"No pods found in namespace '{namespace}'")

        # Check for common pod issues
        for pod in pods:
            pod_name = pod["metadata"]["name"]
            phase = pod.get("status", {}).get("phase", "Unknown")

            if phase == "Pending":
                # Check pending reasons
                conditions = pod.get("status", {}).get("conditions", [])
                for condition in conditions:
                    if condition.get("status") == "False":
                        reason = condition.get("reason", "Unknown")
                        message = condition.get("message", "")
                        issues.append(f"Pod '{pod_name}': {reason} - {message}")

            elif phase == "Failed":
                issues.append(f"Pod '{pod_name}': Failed state - check logs")

            # Check container statuses
            container_statuses = pod.get("status", {}).get("containerStatuses", [])
            for cs in container_statuses:
                waiting = cs.get("state", {}).get("waiting", {})
                if waiting:
                    reason = waiting.get("reason", "Unknown")
                    if reason in ["CrashLoopBackOff", "ImagePullBackOff", "ErrImagePull"]:
                        message = waiting.get("message", "")
                        issues.append(f"Pod '{pod_name}': {reason} - {message}")

        # Check services
        result = subprocess.run(
            ["kubectl", "get", "services", "-n", namespace, "-o", "json"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            services = json.loads(result.stdout).get("items", [])
            for svc in services:
                svc_name = svc["metadata"]["name"]
                svc_type = svc.get("spec", {}).get("type", "ClusterIP")

                # Check if service has endpoints
                result_ep = subprocess.run(
                    ["kubectl", "get", "endpoints", svc_name, "-n", namespace, "-o", "json"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result_ep.returncode == 0:
                    ep_data = json.loads(result_ep.stdout)
                    subsets = ep_data.get("subsets", [])
                    if not subsets or not any(s.get("addresses") for s in subsets):
                        warnings.append(f"Service '{svc_name}': No endpoints (check selector)")

        # Print summary
        print(f"✓ Troubleshooting namespace '{namespace}'")
        print()

        if issues:
            print(f"❌ Critical Issues ({len(issues)}):")
            for issue in issues[:5]:  # Show top 5
                print(f"  • {issue}")
            if len(issues) > 5:
                print(f"  ... and {len(issues) - 5} more issues")
            print()

        if warnings:
            print(f"⚠ Warnings ({len(warnings)}):")
            for warning in warnings[:5]:
                print(f"  • {warning}")
            if len(warnings) > 5:
                print(f"  ... and {len(warnings) - 5} more warnings")
            print()

        if not issues and not warnings:
            print("✓ No issues detected")

        # Recommendations
        print("Recommendations:")
        if any("ImagePull" in issue for issue in issues):
            print("  → Check image names and registry access")
            print("  → Verify imagePullSecrets if using private registry")
        if any("CrashLoopBackOff" in issue for issue in issues):
            print("  → Check pod logs: python scripts/logs.py --pod <name> --namespace", namespace)
            print("  → Verify application configuration and dependencies")
        if any("No endpoints" in warning for warning in warnings):
            print("  → Verify service selector matches pod labels")
            print("  → Check pod status to ensure they're running")

        return 0 if not issues else 1

    except json.JSONDecodeError as e:
        print(f"❌ Error parsing kubectl output: {e}")
        return 1
    except subprocess.TimeoutExpired:
        print(f"❌ Timeout during troubleshooting")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Troubleshoot Kubernetes namespace")
    parser.add_argument("--namespace", required=True, help="Namespace to troubleshoot")
    args = parser.parse_args()

    sys.exit(troubleshoot(args.namespace))
