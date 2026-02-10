#!/usr/bin/env python3
"""Generate Kong Kubernetes Ingress resources for LearnFlow services.

Matches actual LearnFlow production patterns:
- 3 separate Ingress resources: frontend, API (9 routes), docs
- Kong ingress class with konghq.com annotations
- strip-path: false (services handle their own paths)
- ImplementationSpecific pathType for API routes
"""
import sys, argparse
from pathlib import Path

# All LearnFlow API routes - matches actual ingress.yaml
LEARNFLOW_ROUTES = [
    {"path": "/api/triage", "service": "triage-service", "port": 80},
    {"path": "/api/concepts", "service": "concepts-service", "port": 80},
    {"path": "/api/exercises", "service": "exercise-service", "port": 80},
    {"path": "/api/execute", "service": "code-execution-service", "port": 80},
    {"path": "/api/debug", "service": "debug-service", "port": 80},
    {"path": "/api/review", "service": "code-review-service", "port": 80},
    {"path": "/api/progress", "service": "progress-service", "port": 80},
    {"path": "/api/curriculum", "service": "progress-service", "port": 80},
    {"path": "/api/quizzes", "service": "exercise-service", "port": 80},
]

INGRESS_TEMPLATE = '''apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: learnflow-frontend-ingress
  namespace: {namespace}
  annotations:
    konghq.com/strip-path: "false"
    konghq.com/protocols: "http"
spec:
  ingressClassName: kong
  rules:
    - http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: learnflow-frontend
                port:
                  number: 80
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: learnflow-api-ingress
  namespace: {namespace}
  annotations:
    konghq.com/strip-path: "false"
    konghq.com/protocols: "http"
spec:
  ingressClassName: kong
  rules:
    - http:
        paths:
{api_routes}
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: learnflow-docs-ingress
  namespace: {namespace}
  annotations:
    konghq.com/strip-path: "false"
    konghq.com/protocols: "http"
spec:
  ingressClassName: kong
  rules:
    - http:
        paths:
          - path: /docs
            pathType: Prefix
            backend:
              service:
                name: learnflow-docs
                port:
                  number: 80
'''


def configure_services(namespace, output_dir=None):
    """Generate Kong Kubernetes Ingress YAML for LearnFlow services."""

    print(f"Generating Kong Ingress resources for namespace: {namespace}...")

    # Build API route entries
    route_lines = []
    for route in LEARNFLOW_ROUTES:
        route_lines.append(f"          - path: {route['path']}")
        route_lines.append(f"            pathType: ImplementationSpecific")
        route_lines.append(f"            backend:")
        route_lines.append(f"              service:")
        route_lines.append(f"                name: {route['service']}")
        route_lines.append(f"                port:")
        route_lines.append(f"                  number: {route['port']}")

    api_routes = "\n".join(route_lines)

    ingress_yaml = INGRESS_TEMPLATE.format(
        namespace=namespace,
        api_routes=api_routes,
    )

    # Write to output directory
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = Path(f"./k8s/kong")

    output_path.mkdir(parents=True, exist_ok=True)
    ingress_file = output_path / "ingress.yaml"
    ingress_file.write_text(ingress_yaml)

    print(f"  Created: {ingress_file}")
    print(f"\n  3 Ingress resources:")
    print(f"    1. learnflow-frontend-ingress -> learnflow-frontend:80 (path: /)")
    print(f"    2. learnflow-api-ingress -> 9 API routes:")
    for route in LEARNFLOW_ROUTES:
        print(f"       {route['path']} -> {route['service']}:{route['port']}")
    print(f"    3. learnflow-docs-ingress -> learnflow-docs:80 (path: /docs)")

    print(f"\n✓ Kong Ingress configuration generated")
    print(f"  Annotations: strip-path=false, protocols=http")
    print(f"  IngressClass: kong")
    print(f"\n  Apply: kubectl apply -f {ingress_file}")
    print(f"  Access: kubectl port-forward -n kong svc/kong-kong-proxy 8080:80")
    print(f"  Test: curl http://localhost:8080/api/triage/health")

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Kong Ingress for LearnFlow")
    parser.add_argument("--namespace", default="learnflow", help="Application namespace")
    parser.add_argument("--output", help="Output directory for ingress YAML")
    args = parser.parse_args()
    sys.exit(configure_services(args.namespace, args.output))
