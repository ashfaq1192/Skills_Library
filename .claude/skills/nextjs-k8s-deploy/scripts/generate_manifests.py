#!/usr/bin/env python3
"""Generate Kubernetes manifests for Next.js deployment."""
import sys, argparse
from pathlib import Path

DEPLOYMENT_YAML = '''apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: nextjs
        image: {image_tag}
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 3000
        env:
        - name: NODE_ENV
          value: "production"
        - name: NEXT_PUBLIC_API_URL
          value: "http://api-gateway.{namespace}.svc.cluster.local"
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: frontend
spec:
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 3000
  type: ClusterIP
'''

INGRESS_YAML = '''apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: frontend-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: {domain}
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 80
'''

def generate_manifests(image_tag, namespace, domain=None, output_dir=None):
    """Generate K8s manifests for Next.js deployment."""

    # Create output directory
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = Path("./k8s-manifests")

    output_path.mkdir(parents=True, exist_ok=True)

    # Generate deployment
    deployment = DEPLOYMENT_YAML.format(
        image_tag=image_tag,
        namespace=namespace
    )

    deployment_file = output_path / "deployment.yaml"
    deployment_file.write_text(deployment)

    print(f"✓ Manifests generated: {output_path}")
    print(f"  - deployment.yaml (3 replicas)")
    print(f"  - service (ClusterIP)")

    # Generate ingress if domain provided
    if domain:
        ingress = INGRESS_YAML.format(domain=domain)
        ingress_file = output_path / "ingress.yaml"
        ingress_file.write_text(ingress)
        print(f"  - ingress.yaml (domain: {domain})")

    print(f"\n→ Deploy:")
    print(f"  python scripts/deploy_frontend.py --namespace {namespace}")

    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True, help="Docker image tag")
    parser.add_argument("--namespace", required=True, help="Kubernetes namespace")
    parser.add_argument("--domain", help="Domain for ingress")
    parser.add_argument("--output", help="Output directory for manifests")
    args = parser.parse_args()
    sys.exit(generate_manifests(args.image, args.namespace, args.domain, args.output))
