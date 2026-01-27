#!/usr/bin/env python3
"""Configure Dapr components for FastAPI service."""
import sys, argparse
from pathlib import Path

DEPLOYMENT_YAML = '''apiVersion: apps/v1
kind: Deployment
metadata:
  name: {service_name}
spec:
  replicas: 2
  selector:
    matchLabels:
      app: {service_name}
  template:
    metadata:
      labels:
        app: {service_name}
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "{service_name}"
        dapr.io/app-port: "8000"
        dapr.io/log-level: "info"
    spec:
      containers:
      - name: {service_name}
        image: {service_name}:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8000
        env:
        - name: DAPR_HTTP_PORT
          value: "3500"
        - name: DAPR_GRPC_PORT
          value: "50001"
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: openai-credentials
              key: OPENAI_API_KEY
              optional: true
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: DATABASE_URL
              optional: true
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: {service_name}
spec:
  selector:
    app: {service_name}
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
'''

def configure_dapr(service_dir):
    """Generate Kubernetes manifests with Dapr annotations."""
    service_path = Path(service_dir)

    if not service_path.exists():
        print(f"❌ Service directory not found: {service_dir}")
        return 1

    # Get service name from directory
    service_name = service_path.name

    # Create k8s directory
    k8s_dir = service_path / "k8s"
    k8s_dir.mkdir(exist_ok=True)

    # Generate deployment with Dapr annotations
    deployment = DEPLOYMENT_YAML.format(service_name=service_name)

    deployment_file = k8s_dir / "deployment.yaml"
    deployment_file.write_text(deployment)

    print(f"✓ Dapr configuration created")
    print(f"  Deployment: {deployment_file}")
    print(f"  Dapr enabled: true")
    print(f"  App ID: {service_name}")
    print(f"  App port: 8000")
    print(f"\\n→ Dapr features available:")
    print(f"  - State management: http://localhost:3500/v1.0/state/statestore")
    print(f"  - Pub/Sub: http://localhost:3500/v1.0/publish/pubsub/<topic>")
    print(f"  - Service invocation: http://localhost:3500/v1.0/invoke/<app-id>/method/<method>")

    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--service-dir", required=True, help="Service directory")
    args = parser.parse_args()
    sys.exit(configure_dapr(args.service_dir))
