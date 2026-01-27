#!/usr/bin/env python3
"""Install Better Auth in Next.js project."""
import subprocess, sys, argparse
from pathlib import Path

def install_better_auth(project_dir):
    """Install Better Auth package."""
    project_path = Path(project_dir)

    if not project_path.exists():
        print(f"❌ Project directory not found: {project_dir}")
        return 1

    # Check for package.json
    package_json = project_path / "package.json"
    if not package_json.exists():
        print(f"❌ Not a valid Next.js project: package.json missing")
        return 1

    print(f"→ Installing Better Auth in: {project_dir}")

    # Install better-auth and dependencies
    packages = [
        "better-auth",
        "@better-auth/react",
        "jose",  # JWT library
        "bcryptjs",  # Password hashing
    ]

    result = subprocess.run(
        ["npm", "install"] + packages,
        cwd=project_path,
        capture_output=True,
        text=True,
        timeout=120
    )

    if result.returncode != 0:
        print(f"❌ Installation failed: {result.stderr.strip()}")
        return 1

    print(f"✓ Better Auth installed")
    print(f"  Packages: {', '.join(packages)}")
    print(f"\n→ Next: python scripts/configure_auth.py --project-dir {project_dir}")

    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", required=True, help="Next.js project directory")
    args = parser.parse_args()
    sys.exit(install_better_auth(args.project_dir))
