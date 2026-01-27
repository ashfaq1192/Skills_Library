#!/usr/bin/env python3
"""Initialize Docusaurus documentation project."""
import subprocess, sys, argparse
from pathlib import Path

def init_docusaurus(project_name, output_dir):
    # Check Node.js installed
    result = subprocess.run(["node", "--version"], capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ Node.js not installed")
        print("→ Install: https://nodejs.org/ (requires Node.js 18+)")
        return 1

    version = result.stdout.strip()
    print(f"✓ Node.js installed: {version}")

    # Create output directory
    output_path = Path(output_dir)
    if output_path.exists():
        print(f"⚠ Directory exists: {output_dir}")
        print("→ Using existing directory")
    else:
        output_path.mkdir(parents=True, exist_ok=True)

    # Initialize Docusaurus using npx
    print(f"→ Initializing Docusaurus project '{project_name}'...")
    result = subprocess.run(
        ["npx", "create-docusaurus@latest", project_name, "classic", "--typescript"],
        cwd=output_path.parent,
        capture_output=True,
        text=True,
        timeout=300
    )

    if result.returncode != 0:
        print(f"❌ Failed to initialize Docusaurus: {result.stderr.strip()}")
        return 1

    print(f"✓ Docusaurus initialized: {output_dir}")
    print(f"  Template: Classic")
    print(f"  TypeScript: Enabled")
    print(f"\n→ Next steps:")
    print(f"  1. Customize docusaurus.config.ts")
    print(f"  2. Add documentation to docs/ directory")
    print(f"  3. Run: python scripts/build_docs.py --docs-dir {output_dir}")

    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-name", required=True, help="Project name")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    args = parser.parse_args()
    sys.exit(init_docusaurus(args.project_name, args.output_dir))
