#!/usr/bin/env python3
"""Build Next.js application for production."""
import subprocess, sys, argparse
from pathlib import Path

def build_nextjs(project_dir, output_dir):
    """Build Next.js app."""
    project_path = Path(project_dir)

    if not project_path.exists():
        print(f"❌ Project directory not found: {project_dir}")
        return 1

    # Check for package.json
    package_json = project_path / "package.json"
    if not package_json.exists():
        print(f"❌ Not a valid Next.js project: package.json missing")
        return 1

    print(f"✓ Building Next.js from: {project_dir}")

    # Install dependencies if needed
    node_modules = project_path / "node_modules"
    if not node_modules.exists():
        print("→ Installing dependencies...")
        result = subprocess.run(
            ["npm", "install"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode != 0:
            print(f"❌ Failed to install dependencies: {result.stderr.strip()}")
            return 1

    # Build Next.js
    print("→ Building Next.js application...")
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=project_path,
        capture_output=True,
        text=True,
        timeout=300
    )

    if result.returncode != 0:
        print(f"❌ Build failed: {result.stderr.strip()}")
        return 1

    # Check .next directory
    next_dir = project_path / ".next"
    if next_dir.exists():
        # Count files
        file_count = len(list(next_dir.rglob('*')))
        print(f"✓ Next.js built successfully")
        print(f"  Output: {next_dir}")
        print(f"  Files: {file_count}")
        print(f"\n→ Next: python scripts/containerize.py --project-dir {project_dir}")
        return 0
    else:
        print(f"❌ Build output not found: {next_dir}")
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", required=True, help="Next.js project directory")
    parser.add_argument("--output-dir", help="Output directory (deprecated, build goes to .next)")
    args = parser.parse_args()
    sys.exit(build_nextjs(args.project_dir, args.output_dir))
