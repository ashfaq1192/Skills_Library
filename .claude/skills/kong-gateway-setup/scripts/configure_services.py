#!/usr/bin/env python3
"""Configure Kong services and routes for microservices."""
import subprocess, sys, argparse, json
from pathlib import Path

# Example services configuration
SERVICES_CONFIG = {
    "services": [
        {
            "name": "triage-service",
            "host": "triage-service.learnflow.svc.cluster.local",
            "port": 80,
            "path": "/triage"
        },
        {
            "name": "concepts-service",
            "host": "concepts-service.learnflow.svc.cluster.local",
            "port": 80,
            "path": "/concepts"
        },
        {
            "name": "exercise-service",
            "host": "exercise-service.learnflow.svc.cluster.local",
            "port": 80,
            "path": "/exercises"
        },
        {
            "name": "code-execution-service",
            "host": "code-execution-service.learnflow.svc.cluster.local",
            "port": 80,
            "path": "/execute"
        }
    ]
}

def configure_services(kong_namespace, app_namespace, config_file=None):
    """Configure Kong services via Admin API."""

    # Port-forward Kong Admin API
    print("→ Configuring Kong services...")

    # Get Kong Admin API endpoint
    admin_url = "http://localhost:8001"

    # Load services config
    if config_file and Path(config_file).exists():
        import yaml
        with open(config_file) as f:
            config = yaml.safe_load(f)
    else:
        config = SERVICES_CONFIG

    # Configure each service
    import requests

    configured = 0
    for svc in config["services"]:
        service_name = svc["name"]
        upstream_url = f"http://{svc['host']}:{svc['port']}"
        route_path = svc["path"]

        # Create/Update service
        service_data = {
            "name": service_name,
            "url": upstream_url
        }

        try:
            # Try to create service
            response = requests.post(f"{admin_url}/services", json=service_data)

            if response.status_code == 409:
                # Service exists, update it
                response = requests.patch(
                    f"{admin_url}/services/{service_name}",
                    json=service_data
                )

            if response.status_code not in [200, 201]:
                print(f"  ⚠ Failed to configure {service_name}: {response.text}")
                continue

            # Create route for service
            route_data = {
                "name": f"{service_name}-route",
                "paths": [route_path],
                "strip_path": True
            }

            response = requests.post(
                f"{admin_url}/services/{service_name}/routes",
                json=route_data
            )

            if response.status_code in [200, 201]:
                print(f"  ✓ Configured: {service_name} → {route_path}")
                configured += 1
            elif response.status_code == 409:
                print(f"  ✓ Already configured: {service_name}")
                configured += 1
            else:
                print(f"  ⚠ Failed to create route for {service_name}")

        except Exception as e:
            print(f"  ❌ Error configuring {service_name}: {e}")

    if configured == 0:
        print(f"\n❌ No services configured")
        print(f"→ Make sure Kong Admin API is accessible:")
        print(f"  kubectl port-forward -n {kong_namespace} svc/kong-kong-admin 8001:8001")
        return 1

    print(f"\n✓ Configured {configured} services")
    print(f"\n→ Test routes:")
    print(f"  Port-forward proxy: kubectl port-forward -n {kong_namespace} svc/kong-kong-proxy 8000:80")
    print(f"  curl http://localhost:8000/triage/health")

    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--kong-namespace", default="kong", help="Kong namespace")
    parser.add_argument("--app-namespace", default="learnflow", help="Application namespace")
    parser.add_argument("--config", help="Services configuration YAML file")
    args = parser.parse_args()

    # Note: This script requires Kong Admin API to be port-forwarded
    print("⚠ Ensure Kong Admin API is accessible:")
    print("  kubectl port-forward -n kong svc/kong-kong-admin 8001:8001")
    print()

    sys.exit(configure_services(args.kong_namespace, args.app_namespace, args.config))
