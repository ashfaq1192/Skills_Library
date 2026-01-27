#!/usr/bin/env python3
"""Create Neon PostgreSQL project."""
import subprocess, sys, argparse, os, json

def create_project(name, region="aws-us-east-1"):
    api_key = os.getenv("NEON_API_KEY")
    if not api_key:
        print("❌ NEON_API_KEY environment variable not set")
        print("→ Get API key from: https://console.neon.tech/app/settings/api-keys")
        return 1

    # Using neon CLI
    result = subprocess.run(["which", "neonctl"], capture_output=True)
    if result.returncode != 0:
        print("❌ neonctl CLI not installed")
        print("→ Install: npm install -g neonctl")
        return 1

    # Create project
    result = subprocess.run(
        ["neonctl", "projects", "create", "--name", name, "--region", region],
        capture_output=True, text=True, timeout=30
    )

    if result.returncode != 0:
        print(f"❌ Failed to create project: {result.stderr.strip()}")
        return 1

    print(f"✓ Neon project '{name}' created")
    print(f"  Region: {region}")
    print(result.stdout.strip())
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--region", default="aws-us-east-1")
    args = parser.parse_args()
    sys.exit(create_project(args.name, args.region))
