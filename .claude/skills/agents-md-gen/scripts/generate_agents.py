#!/usr/bin/env python3
"""
AGENTS.md Generator for agents-md-gen skill

Reads .agents_analysis.json and generates AGENTS.md following AAIF standards.

Usage:
    python generate_agents.py [--input FILE] [--output FILE] [--template FILE]

Exit Codes:
    0 - Success
    1 - Analysis file not found/invalid
    2 - Template file not found
    3 - Unable to write AGENTS.md
"""

import argparse
import json
import sys
from pathlib import Path


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate AGENTS.md from repository analysis JSON"
    )
    parser.add_argument(
        "--input",
        default=".agents_analysis.json",
        help="Input analysis JSON file (default: .agents_analysis.json)"
    )
    parser.add_argument(
        "--output",
        default="AGENTS.md",
        help="Output markdown file (default: AGENTS.md)"
    )
    parser.add_argument(
        "--template",
        default=None,
        help="Template file (default: scripts/templates/agents_template.md)"
    )
    return parser.parse_args()


def generate_project_overview(analysis):
    """T025: Generate Project Overview section (2-4 sentences)."""
    patterns = analysis.get("patterns", {})
    metadata = analysis.get("metadata", {})
    key_files = analysis.get("key_files", {})

    language = patterns.get("primary_language", "unknown")
    project_type = patterns.get("project_type", "unknown")
    has_tests = patterns.get("has_tests", False)
    test_framework = patterns.get("test_framework", "unknown")

    # Build description
    overview_parts = []

    # Sentence 1: What is this repository
    if project_type != "unknown":
        type_desc = {
            "web-app": "a web application",
            "api": "an API service",
            "library": "a software library",
            "cli-tool": "a command-line tool",
            "monorepo": "a monorepo",
            "single-project": "a software project"
        }.get(project_type, "a software project")
        overview_parts.append(f"This repository contains {type_desc}")
    else:
        overview_parts.append("This repository contains a software project")

    # Sentence 2: Primary language and tech
    if language != "unknown":
        overview_parts.append(f" built with {language.capitalize()}")

    # Sentence 3: Testing info
    if has_tests and test_framework != "unknown":
        overview_parts.append(f". Testing is implemented using {test_framework}")
    elif has_tests:
        overview_parts.append(". The project includes automated tests")

    # Sentence 4: Additional context
    if patterns.get("has_docker"):
        overview_parts.append(" and includes Docker containerization")
    if patterns.get("has_ci"):
        overview_parts.append(" with continuous integration configured")

    overview_parts.append(".")

    return "".join(overview_parts)


def generate_structure_tree(analysis):
    """T026: Generate Project Structure section (ASCII tree)."""
    root_dirs = analysis.get("structure", {}).get("root_directories", [])

    if not root_dirs:
        return "```\n(Empty or minimal repository structure)\n```"

    lines = [f"{analysis['metadata']['repo_root'].split('/')[-1]}/"]

    for i, dir_info in enumerate(root_dirs[:15]):  # Limit to first 15 for readability
        is_last = (i == len(root_dirs) - 1) or (i == 14)
        prefix = "└── " if is_last else "├── "
        dir_name = dir_info["name"]
        file_count = dir_info.get("file_count", 0)

        if file_count > 0:
            lines.append(f"{prefix}{dir_name}/  ({file_count} files)")
        else:
            lines.append(f"{prefix}{dir_name}/")

        # Show subdirectories if present
        subdirs = dir_info.get("subdirs", [])[:5]  # Limit subdirs shown
        if subdirs:
            for j, subdir in enumerate(subdirs):
                is_last_sub = (j == len(subdirs) - 1) or (j == 4)
                continuation = "    " if is_last else "│   "
                sub_prefix = "└── " if is_last_sub else "├── "
                lines.append(f"{continuation}{sub_prefix}{subdir}/")

    if len(root_dirs) > 15:
        lines.append(f"... ({len(root_dirs) - 15} more directories)")

    return "```\n" + "\n".join(lines) + "\n```"


def generate_key_files_section(analysis):
    """Generate key files listing."""
    key_files = analysis.get("key_files", {})
    sections = []

    if key_files.get("documentation"):
        docs = ", ".join(key_files["documentation"][:5])
        sections.append(f"**Documentation**: {docs}")

    if key_files.get("configuration"):
        configs = ", ".join(key_files["configuration"][:5])
        sections.append(f"**Configuration**: {configs}")

    if key_files.get("infrastructure"):
        infra = ", ".join(key_files["infrastructure"][:5])
        sections.append(f"**Infrastructure**: {infra}")

    if key_files.get("ci_cd"):
        ci = ", ".join([f.split('/')[-1] for f in key_files["ci_cd"][:3]])
        sections.append(f"**CI/CD**: {ci}")

    return "\n\n".join(sections) if sections else "*No key files detected*"


def generate_conventions(analysis):
    """T027: Generate Key Conventions section."""
    conventions = analysis.get("conventions", {})
    patterns = conventions.get("detected_patterns", [])

    if not patterns:
        return "*No specific conventions detected. Follow standard practices for the detected language.*"

    lines = []
    for pattern in patterns:
        lines.append(f"- {pattern}")

    return "\n".join(lines)


def generate_getting_started(analysis):
    """T028: Generate Getting Started section."""
    patterns = analysis.get("patterns", {})
    key_files = analysis.get("key_files", {})

    steps = []

    # Step 1: Clone
    steps.append("1. **Clone the repository**:")
    steps.append("   ```bash")
    steps.append("   git clone <repository-url>")
    steps.append("   cd <repository-name>")
    steps.append("   ```")
    steps.append("")

    # Step 2: Setup based on detected files
    steps.append("2. **Install dependencies**:")

    has_setup = False
    if "package.json" in str(key_files.get("configuration", [])):
        steps.append("   ```bash")
        steps.append("   npm install")
        steps.append("   ```")
        has_setup = True
    elif "requirements.txt" in str(key_files.get("configuration", [])):
        steps.append("   ```bash")
        steps.append("   pip install -r requirements.txt")
        steps.append("   ```")
        has_setup = True
    elif "Cargo.toml" in str(key_files.get("configuration", [])):
        steps.append("   ```bash")
        steps.append("   cargo build")
        steps.append("   ```")
        has_setup = True
    elif "go.mod" in str(key_files.get("configuration", [])):
        steps.append("   ```bash")
        steps.append("   go mod download")
        steps.append("   ```")
        has_setup = True

    if not has_setup:
        steps.append("   *Refer to project documentation for setup instructions*")

    steps.append("")

    # Step 3: Run tests if present
    if patterns.get("has_tests"):
        steps.append("3. **Run tests**:")
        test_framework = patterns.get("test_framework", "unknown")

        if test_framework == "pytest":
            steps.append("   ```bash")
            steps.append("   pytest")
            steps.append("   ```")
        elif test_framework == "jest":
            steps.append("   ```bash")
            steps.append("   npm test")
            steps.append("   ```")
        elif test_framework == "go-test":
            steps.append("   ```bash")
            steps.append("   go test ./...")
            steps.append("   ```")
        elif test_framework == "cargo-test":
            steps.append("   ```bash")
            steps.append("   cargo test")
            steps.append("   ```")
        else:
            steps.append("   *Run tests according to project documentation*")

    return "\n".join(steps)


def generate_agent_guidelines(analysis):
    """T029: Generate AI Agent Guidelines section."""
    patterns = analysis.get("patterns", {})
    conventions = analysis.get("conventions", {})

    guidelines = []

    guidelines.append("### Working with This Codebase")
    guidelines.append("")

    # Language-specific guidance
    language = patterns.get("primary_language", "unknown")
    if language != "unknown":
        guidelines.append(f"- **Primary Language**: {language.capitalize()}")

    # Testing guidance
    if patterns.get("has_tests"):
        guidelines.append(f"- **Testing**: Always run tests before committing changes")
        test_framework = patterns.get("test_framework", "unknown")
        if test_framework != "unknown":
            guidelines.append(f"  - Framework: {test_framework}")

    # Convention guidance
    detected_patterns = conventions.get("detected_patterns", [])
    if detected_patterns:
        guidelines.append("- **Code Conventions**: Follow detected patterns:")
        for pattern in detected_patterns[:3]:  # Show top 3
            guidelines.append(f"  - {pattern}")

    # Project type guidance
    project_type = patterns.get("project_type", "unknown")
    if project_type == "monorepo":
        guidelines.append("- **Monorepo Structure**: This is a monorepo - be mindful of cross-package dependencies")
    elif project_type == "library":
        guidelines.append("- **Library Project**: Maintain backward compatibility and semantic versioning")
    elif project_type == "api":
        guidelines.append("- **API Project**: Follow RESTful/API design principles and document endpoints")

    # Infrastructure guidance
    if patterns.get("has_docker"):
        guidelines.append("- **Docker**: Containerization is configured - test in containers when possible")

    if patterns.get("has_ci"):
        guidelines.append("- **CI/CD**: Automated checks are configured - ensure pipelines pass")

    # General guidance
    guidelines.append("")
    guidelines.append("### Best Practices for AI Agents")
    guidelines.append("")
    guidelines.append("- Read existing code patterns before making changes")
    guidelines.append("- Preserve existing naming conventions and structure")
    guidelines.append("- Add tests for new functionality")
    guidelines.append("- Update documentation when adding features")
    guidelines.append("- Check for similar existing implementations before creating new code")

    return "\n".join(guidelines)


def main():
    """Main entry point for AGENTS.md generator."""
    args = parse_arguments()

    # Set default template path if not provided
    if args.template is None:
        script_dir = Path(__file__).parent
        args.template = script_dir / "templates" / "agents_template.md"

    # T031: Validate input file and handle missing/invalid analysis
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Analysis file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    # T023: Read and parse analysis JSON
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            analysis = json.load(f)
        print(f"Reading analysis: {input_path}")
    except Exception as e:
        print(f"Error: Invalid analysis file: {e}", file=sys.stderr)
        sys.exit(1)

    # T032: Validate template file (optional - we can generate without template)
    template_path = Path(args.template)
    if not template_path.exists():
        print(f"Warning: Template file not found: {template_path}, using built-in template", file=sys.stderr)

    # T024: Template loading (we'll use direct generation instead of template substitution)
    print("Generating sections: ", end="", flush=True)

    # T025: Generate Project Overview
    project_overview = generate_project_overview(analysis)
    print("1", end="/", flush=True)

    # T026: Generate Project Structure tree
    structure_tree = generate_structure_tree(analysis)
    key_files_section = generate_key_files_section(analysis)
    print("2", end="/", flush=True)

    # T027: Generate Key Conventions
    conventions_section = generate_conventions(analysis)
    print("3", end="/", flush=True)

    # T028: Generate Getting Started
    getting_started_section = generate_getting_started(analysis)
    print("4", end="/", flush=True)

    # T029: Generate AI Agent Guidelines
    agent_guidelines_section = generate_agent_guidelines(analysis)
    print("5", end="/", flush=True)

    # Build complete AGENTS.md content
    agents_content = f"""# AGENTS.md

**Generated**: {analysis['metadata']['analyzed_at']}
**Analyzer Version**: {analysis['metadata']['analyzer_version']}

## Project Overview

{project_overview}

## Project Structure

{structure_tree}

### Key Files

{key_files_section}

## Key Conventions

{conventions_section}

## Getting Started

{getting_started_section}

## AI Agent Guidelines

{agent_guidelines_section}

---

*This file was automatically generated by the agents-md-gen skill. To regenerate after structural changes, run the analysis and generation scripts again.*
"""

    print("6/6")

    # T030: Write AGENTS.md to repository root
    # T033: Handle write failures
    output_path = Path(args.output)
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(agents_content)
        print(f"✓ AGENTS.md generated ({len(agents_content)} bytes)")
        sys.exit(0)
    except Exception as e:
        print(f"Error: Unable to write AGENTS.md: {e}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
