#!/usr/bin/env python3
"""Build Docusaurus documentation site."""
import subprocess, sys, argparse
from pathlib import Path

def build_docs(docs_dir):
    # Verify docs directory exists
    docs_path = Path(docs_dir)
    if not docs_path.exists():
        print(f"❌ Documentation directory not found: {docs_dir}")
        print("→ Initialize first: python scripts/init_docusaurus.py")
        return 1

    # Check for package.json
    package_json = docs_path / "package.json"
    if not package_json.exists():
        print(f"❌ Not a valid Docusaurus project: package.json missing")
        return 1

    print(f"✓ Building documentation from: {docs_dir}")

    # Install dependencies if node_modules missing
    node_modules = docs_path / "node_modules"
    if not node_modules.exists():
        print("→ Installing dependencies...")
        result = subprocess.run(
            ["npm", "install"],
            cwd=docs_path,
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode != 0:
            print(f"❌ Failed to install dependencies: {result.stderr.strip()}")
            return 1

    # Build the site
    print("→ Building Docusaurus site...")
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=docs_path,
        capture_output=True,
        text=True,
        timeout=300
    )

    if result.returncode != 0:
        print(f"❌ Build failed: {result.stderr.strip()}")
        return 1

    # Check build output
    build_dir = docs_path / "build"
    if build_dir.exists():
        # Count files in build directory
        file_count = len(list(build_dir.rglob('*')))
        print(f"✓ Documentation built successfully")
        print(f"  Output: {build_dir}")
        print(f"  Files: {file_count}")
        print(f"\n→ Test locally: npm run serve (in {docs_dir})")
        print(f"→ Deploy: python scripts/deploy_docs.py --docs-dir {docs_dir}")
        return 0
    else:
        print(f"❌ Build directory not found: {build_dir}")
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--docs-dir", required=True, help="Docusaurus project directory")
    args = parser.parse_args()
    sys.exit(build_docs(args.docs_dir))
