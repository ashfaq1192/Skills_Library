#!/usr/bin/env python3
"""Generate API documentation from OpenAPI spec."""
import subprocess, sys, argparse, json
from pathlib import Path

def generate_api_docs(openapi_spec, output_dir):
    # Verify OpenAPI spec exists
    spec_path = Path(openapi_spec)
    if not spec_path.exists():
        print(f"❌ OpenAPI spec not found: {openapi_spec}")
        return 1

    # Load and validate spec
    try:
        with open(spec_path, 'r') as f:
            if spec_path.suffix == '.json':
                spec = json.load(f)
            else:
                import yaml
                spec = yaml.safe_load(f)

        print(f"✓ OpenAPI spec loaded: {spec_path.name}")
        print(f"  Title: {spec.get('info', {}).get('title', 'Unknown')}")
        print(f"  Version: {spec.get('info', {}).get('version', 'Unknown')}")
    except Exception as e:
        print(f"❌ Invalid OpenAPI spec: {e}")
        return 1

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Install docusaurus-plugin-openapi-docs if not present
    print("→ Installing OpenAPI plugin...")
    result = subprocess.run(
        ["npm", "install", "docusaurus-plugin-openapi-docs", "docusaurus-theme-openapi-docs"],
        capture_output=True,
        text=True,
        timeout=120
    )

    if result.returncode != 0:
        print(f"⚠ Plugin installation had warnings, continuing...")

    # Generate markdown from OpenAPI spec
    print("→ Generating API documentation...")

    # Extract endpoints and generate simple markdown
    endpoints = []
    for path, methods in spec.get('paths', {}).items():
        for method, details in methods.items():
            if method in ['get', 'post', 'put', 'delete', 'patch']:
                endpoints.append({
                    'path': path,
                    'method': method.upper(),
                    'summary': details.get('summary', 'No description'),
                    'description': details.get('description', '')
                })

    # Generate markdown
    markdown = f"""# API Reference

Generated from OpenAPI specification: {spec.get('info', {}).get('title', 'API')}

Version: {spec.get('info', {}).get('version', '1.0.0')}

## Endpoints

"""
    for ep in endpoints:
        markdown += f"### `{ep['method']}` {ep['path']}\n\n"
        markdown += f"{ep['summary']}\n\n"
        if ep['description']:
            markdown += f"{ep['description']}\n\n"
        markdown += "---\n\n"

    # Write to output
    api_doc_file = output_path / "api-reference.md"
    api_doc_file.write_text(markdown)

    print(f"✓ API documentation generated: {api_doc_file}")
    print(f"  Endpoints: {len(endpoints)}")

    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--openapi-spec", required=True, help="Path to OpenAPI spec file")
    parser.add_argument("--output", required=True, help="Output directory for API docs")
    args = parser.parse_args()
    sys.exit(generate_api_docs(args.openapi_spec, args.output))
