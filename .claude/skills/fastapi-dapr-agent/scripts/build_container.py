#!/usr/bin/env python3
"""Build Docker container for FastAPI service."""
import subprocess, sys, argparse
from pathlib import Path

def build_container(service_dir, tag):
    """Build Docker image for service."""
    service_path = Path(service_dir)

    if not service_path.exists():
        print(f"❌ Service directory not found: {service_dir}")
        return 1

    dockerfile = service_path / "Dockerfile"
    if not dockerfile.exists():
        print(f"❌ Dockerfile not found: {dockerfile}")
        return 1

    # Get service name
    service_name = service_path.name
    image_name = f"{service_name}:{tag}"

    print(f"→ Building Docker image: {image_name}")

    # Build image
    result = subprocess.run(
        ["docker", "build", "-t", image_name, "."],
        cwd=service_path,
        capture_output=True,
        text=True,
        timeout=300
    )

    if result.returncode != 0:
        print(f"❌ Build failed: {result.stderr.strip()}")
        return 1

    # Get image size
    result = subprocess.run(
        ["docker", "images", image_name, "--format", "{{.Size}}"],
        capture_output=True,
        text=True
    )

    size = result.stdout.strip() if result.returncode == 0 else "unknown"

    print(f"✓ Docker image built: {image_name}")
    print(f"  Size: {size}")
    print(f"\\n→ Test locally:")
    print(f"  docker run -p 8000:8000 {image_name}")
    print(f"\\n→ Deploy to K8s:")
    print(f"  python scripts/deploy_service.py --service-dir {service_dir}")

    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--service-dir", required=True, help="Service directory")
    parser.add_argument("--tag", default="latest", help="Image tag")
    args = parser.parse_args()
    sys.exit(build_container(args.service_dir, args.tag))
