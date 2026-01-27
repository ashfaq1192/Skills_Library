#!/usr/bin/env python3
"""Enable JWT authentication plugin in Kong."""
import subprocess, sys, argparse
import requests

def enable_jwt_auth(issuer, kong_namespace):
    """Enable JWT authentication for Kong services."""

    admin_url = "http://localhost:8001"

    print(f"→ Enabling JWT authentication...")

    # Create JWT plugin globally
    jwt_config = {
        "name": "jwt",
        "config": {
            "claims_to_verify": ["exp"],
            "key_claim_name": "iss",
            "secret_is_base64": False
        }
    }

    try:
        # Enable JWT plugin
        response = requests.post(f"{admin_url}/plugins", json=jwt_config)

        if response.status_code in [200, 201]:
            print(f"  ✓ JWT plugin enabled")
        elif response.status_code == 409:
            print(f"  ✓ JWT plugin already enabled")
        else:
            print(f"  ❌ Failed to enable JWT: {response.text}")
            return 1

        # Create consumer for Better Auth
        consumer_data = {
            "username": issuer
        }

        response = requests.post(f"{admin_url}/consumers", json=consumer_data)

        if response.status_code in [200, 201, 409]:
            print(f"  ✓ Consumer created: {issuer}")
        else:
            print(f"  ⚠ Consumer creation warning: {response.status_code}")

        # Create JWT credential for consumer
        jwt_credential = {
            "algorithm": "HS256",
            "key": issuer,
            "secret": "your-jwt-secret-change-in-production"
        }

        response = requests.post(
            f"{admin_url}/consumers/{issuer}/jwt",
            json=jwt_credential
        )

        if response.status_code in [200, 201]:
            print(f"  ✓ JWT credential created")
        elif response.status_code == 409:
            print(f"  ✓ JWT credential already exists")
        else:
            print(f"  ⚠ Credential warning: {response.status_code}")

    except Exception as e:
        print(f"❌ Error enabling JWT: {e}")
        print(f"\n→ Make sure Kong Admin API is accessible:")
        print(f"  kubectl port-forward -n {kong_namespace} svc/kong-kong-admin 8001:8001")
        return 1

    print(f"\n✓ JWT authentication enabled")
    print(f"  Issuer: {issuer}")
    print(f"\n⚠ Important:")
    print(f"  1. Update JWT secret in production")
    print(f"  2. Configure Better Auth to include 'iss' claim")
    print(f"  3. Include JWT token in Authorization header:")
    print(f"     Authorization: Bearer <jwt-token>")

    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--issuer", default="better-auth", help="JWT issuer")
    parser.add_argument("--kong-namespace", default="kong", help="Kong namespace")
    args = parser.parse_args()

    print("⚠ Ensure Kong Admin API is accessible:")
    print("  kubectl port-forward -n kong svc/kong-kong-admin 8001:8001")
    print()

    sys.exit(enable_jwt_auth(args.issuer, args.kong_namespace))
