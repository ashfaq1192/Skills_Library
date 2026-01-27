#!/usr/bin/env python3
"""Get Neon database connection string."""
import subprocess, sys, argparse, os, json

def get_connection(project_id):
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

    # Get connection string
    result = subprocess.run(
        ["neonctl", "connection-string", "--project-id", project_id],
        capture_output=True, text=True, timeout=30
    )

    if result.returncode != 0:
        print(f"❌ Failed to get connection string: {result.stderr.strip()}")
        print(f"→ Check project ID is valid: neonctl projects list")
        return 1

    conn_string = result.stdout.strip()
    print(f"✓ Connection string retrieved")
    print(f"\n{conn_string}\n")
    print("→ Save to .env: DATABASE_URL=\"{conn_string}\"")
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True, help="Neon project ID")
    args = parser.parse_args()
    sys.exit(get_connection(args.project))
