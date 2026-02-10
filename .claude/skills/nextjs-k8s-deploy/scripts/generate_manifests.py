#!/usr/bin/env python3
"""Generate Kubernetes manifests for Next.js deployment with service rewrite proxy.

Matches actual LearnFlow production patterns:
- Service rewrite proxy env vars for all 7 backend services
- next.config.js rewrites pattern (frontend proxies /api/* to microservices)
- Standalone output mode for K8s
- Health probes and resource limits
"""
import sys, argparse
from pathlib import Path

# LearnFlow service configuration - matches actual next.config.js rewrites
LEARNFLOW_SERVICES = {
    'triage': {'env': 'TRIAGE_SERVICE_URL', 'k8s_name': 'triage-service'},
    'concepts': {'env': 'CONCEPTS_SERVICE_URL', 'k8s_name': 'concepts-service'},
    'exercises': {'env': 'EXERCISE_SERVICE_URL', 'k8s_name': 'exercise-service'},
    'execute': {'env': 'CODE_EXECUTION_SERVICE_URL', 'k8s_name': 'code-execution-service'},
    'debug': {'env': 'DEBUG_SERVICE_URL', 'k8s_name': 'debug-service'},
    'review': {'env': 'CODE_REVIEW_SERVICE_URL', 'k8s_name': 'code-review-service'},
    'progress': {'env': 'PROGRESS_SERVICE_URL', 'k8s_name': 'progress-service'},
}

# next.config.js template with service rewrites
NEXT_CONFIG_TEMPLATE = '''/** @type {{import('next').NextConfig}} */
const nextConfig = {{
  output: 'standalone',
  reactStrictMode: true,
  swcMinify: true,
  experimental: {{
    serverComponentsExternalPackages: ['pg'],
  }},
  async rewrites() {{
{rewrite_vars}

    return [
{rewrite_rules}
    ]
  }},
}}

module.exports = nextConfig
'''

DEPLOYMENT_YAML = '''apiVersion: apps/v1
kind: Deployment
metadata:
  name: learnflow-frontend
  namespace: {namespace}
spec:
  replicas: 2
  selector:
    matchLabels:
      app: learnflow-frontend
  template:
    metadata:
      labels:
        app: learnflow-frontend
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
{service_env_vars}
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
  name: learnflow-frontend
  namespace: {namespace}
spec:
  selector:
    app: learnflow-frontend
  ports:
  - port: 80
    targetPort: 3000
  type: ClusterIP
'''


def generate_manifests(image_tag, namespace, services=None, output_dir=None):
    """Generate K8s manifests for Next.js deployment with service rewrites."""

    # Parse services
    if services:
        service_list = [s.strip() for s in services.split(',')]
    else:
        service_list = list(LEARNFLOW_SERVICES.keys())

    # Create output directory
    output_path = Path(output_dir) if output_dir else Path("./k8s-manifests")
    output_path.mkdir(parents=True, exist_ok=True)

    # Generate service environment variables for K8s deployment
    env_lines = []
    for svc in service_list:
        if svc in LEARNFLOW_SERVICES:
            cfg = LEARNFLOW_SERVICES[svc]
            k8s_url = f"http://{cfg['k8s_name']}.{namespace}.svc.cluster.local:8000"
            env_lines.append(f"        - name: {cfg['env']}")
            env_lines.append(f'          value: "{k8s_url}"')

    service_env_vars = "\n".join(env_lines)

    # Generate deployment
    deployment = DEPLOYMENT_YAML.format(
        image_tag=image_tag,
        namespace=namespace,
        service_env_vars=service_env_vars,
    )

    deployment_file = output_path / "deployment.yaml"
    deployment_file.write_text(deployment)

    # Generate next.config.js template for reference
    rewrite_vars = []
    rewrite_rules = []
    for svc in service_list:
        if svc in LEARNFLOW_SERVICES:
            cfg = LEARNFLOW_SERVICES[svc]
            var_name = f"{svc}Url"
            rewrite_vars.append(
                f"    const {var_name} = process.env.{cfg['env']} || 'http://{cfg['k8s_name']}:8000'"
            )
            rewrite_rules.append(
                f"      {{ source: '/api/{svc}/:path*', destination: `${{{var_name}}}/api/{svc}/:path*` }},"
            )

    next_config = NEXT_CONFIG_TEMPLATE.format(
        rewrite_vars="\n".join(rewrite_vars),
        rewrite_rules="\n".join(rewrite_rules),
    )

    config_file = output_path / "next.config.js.reference"
    config_file.write_text(next_config)

    print(f"✓ Manifests generated: {output_path}")
    print(f"  - deployment.yaml (2 replicas, service env vars)")
    print(f"  - next.config.js.reference (rewrite proxy template)")
    print(f"  Services configured ({len(service_list)}):")
    for svc in service_list:
        if svc in LEARNFLOW_SERVICES:
            cfg = LEARNFLOW_SERVICES[svc]
            print(f"    /api/{svc}/* -> {cfg['k8s_name']}:8000")
    print(f"\n→ Deploy: python scripts/deploy_frontend.py --namespace {namespace}")

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate K8s manifests for Next.js with service rewrites")
    parser.add_argument("--image", required=True, help="Docker image tag")
    parser.add_argument("--namespace", required=True, help="Kubernetes namespace")
    parser.add_argument("--services", help="Comma-separated services (default: all 7 LearnFlow services)")
    parser.add_argument("--output", help="Output directory for manifests")
    args = parser.parse_args()
    sys.exit(generate_manifests(args.image, args.namespace, args.services, args.output))
