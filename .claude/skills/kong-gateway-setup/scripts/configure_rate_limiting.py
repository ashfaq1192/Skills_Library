#!/usr/bin/env python3
"""Configure rate limiting plugin in Kong."""
import subprocess, sys, argparse
import requests

def configure_rate_limiting(requests_limit, time_period, kong_namespace):
    """Configure rate limiting for Kong."""

    admin_url = "http://localhost:8001"

    print(f"→ Configuring rate limiting...")
    print(f"  Limit: {requests_limit} requests per {time_period}")

    # Create rate limiting plugin
    rate_limit_config = {
        "name": "rate-limiting",
        "config": {
            time_period: requests_limit,
            "policy": "local"  # Use "redis" for distributed rate limiting
        }
    }

    try:
        response = requests.post(f"{admin_url}/plugins", json=rate_limit_config)

        if response.status_code in [200, 201]:
            print(f"  ✓ Rate limiting enabled")
        elif response.status_code == 409:
            print(f"  ✓ Rate limiting already configured")
        else:
            print(f"  ❌ Failed: {response.text}")
            return 1

    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"\n→ Make sure Kong Admin API is accessible:")
        print(f"  kubectl port-forward -n {kong_namespace} svc/kong-kong-admin 8001:8001")
        return 1

    # Enable CORS plugin
    print(f"\n→ Enabling CORS...")

    cors_config = {
        "name": "cors",
        "config": {
            "origins": ["*"],
            "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            "headers": ["Accept", "Authorization", "Content-Type"],
            "exposed_headers": ["X-Auth-Token"],
            "credentials": True,
            "max_age": 3600
        }
    }

    try:
        response = requests.post(f"{admin_url}/plugins", json=cors_config)

        if response.status_code in [200, 201]:
            print(f"  ✓ CORS enabled")
        elif response.status_code == 409:
            print(f"  ✓ CORS already enabled")

    except Exception as e:
        print(f"  ⚠ CORS warning: {e}")

    print(f"\n✓ Kong plugins configured")
    print(f"\n→ Verify:")
    print(f"  curl -I http://localhost:8000/triage/health")
    print(f"  Check headers: X-RateLimit-Limit, X-RateLimit-Remaining")

    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--requests", type=int, default=100, help="Request limit")
    parser.add_argument("--per", choices=["second", "minute", "hour", "day"],
                       default="minute", help="Time period")
    parser.add_argument("--kong-namespace", default="kong", help="Kong namespace")
    args = parser.parse_args()

    print("⚠ Ensure Kong Admin API is accessible:")
    print("  kubectl port-forward -n kong svc/kong-kong-admin 8001:8001")
    print()

    sys.exit(configure_rate_limiting(args.requests, args.per, args.kong_namespace))
