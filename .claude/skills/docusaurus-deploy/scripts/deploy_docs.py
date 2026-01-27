#!/usr/bin/env python3
"""Deploy Docusaurus site to Kubernetes."""
import subprocess, sys, argparse
from pathlib import Path
import tempfile

NGINX_CONFIG = """apiVersion: v1
kind: ConfigMap
metadata:
  name: docs-nginx-config
data:
  default.conf: |
    server {
      listen 80;
      server_name _;
      root /usr/share/nginx/html;
      index index.html;

      location / {
        try_files $uri $uri/ /index.html;
      }
    }
"""

DEPLOYMENT_YAML = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: docs-deployment
spec:
  replicas: 2
  selector:
    matchLabels:
      app: docs
  template:
    metadata:
      labels:
        app: docs
    spec:
      containers:
      - name: nginx
        image: nginx:alpine
        ports:
        - containerPort: 80
        volumeMounts:
        - name: docs
          mountPath: /usr/share/nginx/html
        - name: nginx-config
          mountPath: /etc/nginx/conf.d
      volumes:
      - name: docs
        emptyDir: {}
      - name: nginx-config
        configMap:
          name: docs-nginx-config
---
apiVersion: v1
kind: Service
metadata:
  name: docs-service
spec:
  selector:
    app: docs
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
"""

def deploy_docs(namespace, docs_dir, domain=None):
    # Verify docs built
    build_dir = Path(docs_dir) / "build"
    if not build_dir.exists():
        print(f"❌ Build directory not found: {build_dir}")
        print("→ Build first: python scripts/build_docs.py")
        return 1

    # Verify kubectl
    result = subprocess.run(["which", "kubectl"], capture_output=True)
    if result.returncode != 0:
        print("❌ kubectl not installed")
        return 1

    # Create namespace if needed
    subprocess.run(
        ["kubectl", "create", "namespace", namespace],
        capture_output=True
    )

    # Create temporary manifests
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Write ConfigMap
        config_file = tmpdir / "nginx-config.yaml"
        config_file.write_text(NGINX_CONFIG)

        # Write Deployment
        deploy_file = tmpdir / "deployment.yaml"
        deploy_file.write_text(DEPLOYMENT_YAML)

        # Apply ConfigMap
        result = subprocess.run(
            ["kubectl", "apply", "-f", str(config_file), "-n", namespace],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"❌ Failed to create ConfigMap: {result.stderr.strip()}")
            return 1

        print(f"✓ Nginx ConfigMap created")

        # Apply Deployment
        result = subprocess.run(
            ["kubectl", "apply", "-f", str(deploy_file), "-n", namespace],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"❌ Failed to create Deployment: {result.stderr.strip()}")
            return 1

        print(f"✓ Docs deployment created")
        print(f"  Namespace: {namespace}")
        print(f"  Replicas: 2")

    # Note: In production, you would copy build files to pods using:
    # kubectl cp or by building a custom Docker image with docs
    print(f"\n⚠ Note: Build files need to be copied to pods")
    print(f"→ Option 1: Build Docker image with docs and update deployment")
    print(f"→ Option 2: Use kubectl cp to copy files to running pods")

    if domain:
        print(f"\n→ Configure Ingress for domain: {domain}")

    # Verify deployment
    result = subprocess.run(
        ["kubectl", "get", "deployment", "docs-deployment", "-n", namespace],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        print(f"\n✓ Deployment verified")
        print(f"→ Access via: kubectl port-forward -n {namespace} svc/docs-service 8080:80")
        print(f"→ Then open: http://localhost:8080")
        return 0
    else:
        print(f"\n⚠ Could not verify deployment")
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--namespace", required=True, help="Kubernetes namespace")
    parser.add_argument("--docs-dir", required=True, help="Docusaurus project directory")
    parser.add_argument("--domain", help="Optional domain for Ingress")
    args = parser.parse_args()
    sys.exit(deploy_docs(args.namespace, args.docs_dir, args.domain))
