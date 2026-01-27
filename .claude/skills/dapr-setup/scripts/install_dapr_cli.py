#!/usr/bin/env python3
"""Install Dapr CLI."""
import subprocess, sys, platform, os

def install_dapr_cli():
    # Check if already installed
    result = subprocess.run(["which", "dapr"], capture_output=True)
    if result.returncode == 0:
        # Get version
        result = subprocess.run(["dapr", "version"], capture_output=True, text=True)
        version = result.stdout.strip().split('\n')[0] if result.returncode == 0 else "unknown"
        print(f"✓ Dapr CLI already installed: {version}")
        return 0

    print("→ Installing Dapr CLI...")

    # Install using official installer
    result = subprocess.run(
        ["bash", "-c", "curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | /bin/bash"],
        capture_output=True, text=True, timeout=120
    )

    if result.returncode != 0:
        print(f"❌ Failed to install Dapr CLI: {result.stderr.strip()}")
        print("→ Try manual installation: https://docs.dapr.io/getting-started/install-dapr-cli/")
        return 1

    # Verify installation
    result = subprocess.run(["dapr", "version"], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✓ Dapr CLI installed successfully")
        print(f"  {result.stdout.strip().split(chr(10))[0]}")
        return 0
    else:
        print(f"⚠ Dapr CLI installed but verification failed")
        print(f"→ Check PATH includes: $HOME/.dapr/bin")
        return 1

if __name__ == "__main__":
    sys.exit(install_dapr_cli())
