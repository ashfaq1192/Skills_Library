#!/usr/bin/env python3
"""
Repository Structure Analyzer for agents-md-gen skill

Analyzes repository structure and generates .agents_analysis.json with:
- Directory structure (up to max_depth levels)
- Key files (documentation, configuration, infrastructure, CI/CD)
- Detected patterns (language, test framework, project type)
- Conventions (naming patterns, structure)

Usage:
    python analyze_repo.py [repository_path] [--max-depth N] [--output FILE]

Exit Codes:
    0 - Success
    1 - Invalid repository path
    2 - Unable to write output file
"""

import argparse
import json
import os
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path


VERSION = "1.0.0"

# Directories to ignore during analysis
IGNORE_DIRS = {
    "node_modules", "venv", ".venv", "__pycache__", ".git",
    ".specify", "dist", "build", ".eggs", "eggs", "lib", "lib64",
    ".tox", ".pytest_cache", ".mypy_cache", "htmlcov", "coverage",
    ".idea", ".vscode", "target", "bin", "obj", ".gradle", "vendor"
}

# Key files to detect
KEY_FILES = {
    "documentation": ["README.md", "CONTRIBUTING.md", "LICENSE", "CHANGELOG.md", "AUTHORS"],
    "configuration": ["package.json", "requirements.txt", ".env.example", "pyproject.toml",
                     "setup.py", "setup.cfg", "Cargo.toml", "go.mod", "pom.xml", "build.gradle"],
    "infrastructure": ["Dockerfile", "docker-compose.yml", "docker-compose.yaml",
                      "kubernetes.yml", "kubernetes.yaml"],
    "ci_cd": [".github", ".gitlab-ci.yml", ".circleci", "Jenkinsfile", ".travis.yml"]
}

# Language detection patterns
LANGUAGE_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".rb": "ruby",
    ".php": "php",
    ".cpp": "cpp",
    ".c": "c",
    ".cs": "csharp",
    ".swift": "swift"
}


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Analyze repository structure and generate analysis JSON"
    )
    parser.add_argument(
        "repository_path",
        nargs="?",
        default=".",
        help="Path to repository root (default: current directory)"
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=5,
        help="Maximum directory depth to traverse (default: 5)"
    )
    parser.add_argument(
        "--output",
        default=".agents_analysis.json",
        help="Output file path (default: .agents_analysis.json)"
    )
    return parser.parse_args()


def traverse_directory(repo_path, max_depth, warnings):
    """Traverse directory structure up to max_depth levels."""
    root_directories = []
    all_files = []
    dir_count = 0
    file_count = 0

    for root, dirs, files in os.walk(repo_path):
        # Calculate current depth
        depth = root[len(str(repo_path)):].count(os.sep)

        if depth >= max_depth:
            dirs[:] = []  # Don't recurse deeper
            if depth == max_depth:
                warnings.append(f"Max depth {max_depth} reached at: {root}")
            continue

        # Filter ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        # Handle permission errors gracefully
        try:
            # Count directories
            dir_count += len(dirs)

            # Track root-level directories
            if depth == 0:
                for d in dirs:
                    dir_path = Path(root) / d
                    subdir_count = sum(1 for _ in dir_path.rglob('*') if _.is_dir())
                    file_count_in_dir = sum(1 for _ in dir_path.rglob('*') if _.is_file())

                    root_directories.append({
                        "name": d,
                        "path": d,
                        "file_count": file_count_in_dir,
                        "subdirs": [sd for sd in os.listdir(dir_path) if (dir_path / sd).is_dir() and sd not in IGNORE_DIRS]
                    })

            # Collect files
            for f in files:
                file_path = Path(root) / f
                try:
                    if file_path.is_file():
                        all_files.append(file_path.relative_to(repo_path))
                        file_count += 1
                except (PermissionError, OSError) as e:
                    warnings.append(f"Skipped file due to permission error: {file_path}")

        except (PermissionError, OSError) as e:
            warnings.append(f"Skipped directory due to permission error: {root}")
            continue

    return root_directories, all_files, file_count, dir_count


def detect_key_files(all_files, repo_path):
    """Detect key files in repository."""
    key_files = {
        "documentation": [],
        "configuration": [],
        "infrastructure": [],
        "ci_cd": [],
        "other": []
    }

    for file_path in all_files:
        file_name = file_path.name
        file_str = str(file_path)

        # Documentation
        if any(file_name == doc_file for doc_file in KEY_FILES["documentation"]):
            key_files["documentation"].append(file_str)

        # Configuration
        elif any(file_name == config_file for config_file in KEY_FILES["configuration"]):
            key_files["configuration"].append(file_str)

        # Infrastructure
        elif any(file_name.startswith(infra_file) for infra_file in KEY_FILES["infrastructure"]):
            key_files["infrastructure"].append(file_str)

        # CI/CD (check directory names too)
        elif any(ci_name in file_str for ci_name in KEY_FILES["ci_cd"]):
            key_files["ci_cd"].append(file_str)

        # Other important files
        elif file_name in [".gitignore", ".dockerignore", "Makefile", ".editorconfig"]:
            key_files["other"].append(file_str)

    return key_files


def detect_language(all_files):
    """Detect primary programming language by counting file extensions."""
    language_counts = defaultdict(int)

    for file_path in all_files:
        ext = file_path.suffix.lower()
        if ext in LANGUAGE_EXTENSIONS:
            language_counts[LANGUAGE_EXTENSIONS[ext]] += 1

    if not language_counts:
        return "unknown"

    # Return language with most files
    return max(language_counts.items(), key=lambda x: x[1])[0]


def detect_test_framework(all_files, primary_language):
    """Detect test framework based on files and language."""
    has_tests = False
    test_framework = "unknown"

    for file_path in all_files:
        file_str = str(file_path).lower()
        file_name = file_path.name.lower()

        # Check for test directories or files
        if "test" in file_str or "spec" in file_str:
            has_tests = True

            # Python: pytest
            if primary_language == "python" and (file_name.startswith("test_") or "pytest" in file_str):
                test_framework = "pytest"

            # JavaScript/TypeScript: jest, mocha
            elif primary_language in ["javascript", "typescript"]:
                if ".test." in file_name or ".spec." in file_name:
                    if "jest" in file_str:
                        test_framework = "jest"
                    else:
                        test_framework = "jest"  # Default for JS/TS

            # Go
            elif primary_language == "go" and file_name.endswith("_test.go"):
                test_framework = "go-test"

            # Rust
            elif primary_language == "rust" and ("tests/" in file_str or file_name == "lib.rs"):
                test_framework = "cargo-test"

            # Java
            elif primary_language == "java" and ("junit" in file_str.lower() or "test" in file_str):
                test_framework = "junit"

    return has_tests, test_framework


def detect_project_type(key_files, root_directories):
    """Infer project type from structure and files."""
    has_frontend = any(d["name"] in ["frontend", "client", "web", "ui"] for d in root_directories)
    has_backend = any(d["name"] in ["backend", "server", "api"] for d in root_directories)
    has_multiple_packages = len([f for f in key_files["configuration"] if "package.json" in f]) > 1
    has_src = any(d["name"] == "src" for d in root_directories)

    # Docker/K8s presence
    has_docker = bool(key_files["infrastructure"])
    has_kubernetes = any("kubernetes" in f or "k8s" in f for f in key_files["infrastructure"])
    has_ci = bool(key_files["ci_cd"])

    # Infer type
    if has_frontend and has_backend:
        project_type = "web-app"
    elif has_multiple_packages:
        project_type = "monorepo"
    elif "setup.py" in str(key_files["configuration"]) or "Cargo.toml" in str(key_files["configuration"]):
        project_type = "library"
    elif has_backend or any("api" in f for f in key_files["configuration"]):
        project_type = "api"
    elif has_src:
        project_type = "single-project"
    else:
        project_type = "unknown"

    return project_type, has_docker, has_kubernetes, has_ci


def detect_conventions(all_files, primary_language, root_directories):
    """Detect coding conventions and patterns."""
    patterns = []
    notable_files = []

    # Test naming patterns
    test_files = [f for f in all_files if "test" in str(f).lower()]
    if test_files:
        if any(str(f).startswith("tests/") for f in test_files):
            patterns.append("Tests in tests/ directory")
        if primary_language == "python" and any(f.name.startswith("test_") for f in test_files):
            patterns.append("Python test files use test_*.py naming")
        if primary_language in ["javascript", "typescript"] and any(".test." in f.name or ".spec." in f.name for f in test_files):
            patterns.append("JavaScript test files use *.test.js or *.spec.js naming")

    # Source structure patterns
    if any(d["name"] == "src" for d in root_directories):
        patterns.append("Source code in src/ directory")
    if any(d["name"] == "lib" for d in root_directories):
        patterns.append("Library code in lib/ directory")
    if any(d["name"] == "scripts" for d in root_directories):
        patterns.append("Utility scripts in scripts/ directory")
    if any(d["name"] == "docs" for d in root_directories):
        patterns.append("Documentation in docs/ directory")

    # Notable configuration files
    for file_path in all_files:
        if file_path.name in ["CODE_OF_CONDUCT.md", "SECURITY.md", ".editorconfig", "tsconfig.json"]:
            notable_files.append({
                "path": str(file_path),
                "significance": f"Project standard: {file_path.name}"
            })

    return patterns, notable_files


def main():
    """Main entry point for repository analyzer."""
    start_time = time.time()
    args = parse_arguments()

    # Validate repository path (T020)
    repo_path = Path(args.repository_path).resolve()
    if not repo_path.exists() or not repo_path.is_dir():
        print(f"Error: Repository path does not exist: {repo_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Analyzing repository: {repo_path}")

    warnings = []

    # T009: Traverse directory structure with max_depth
    # T010: Filter ignored directories
    # T022: Handle permission errors gracefully
    root_directories, all_files, file_count, dir_count = traverse_directory(
        repo_path, args.max_depth, warnings
    )

    # T011-T014: Detect key files
    key_files = detect_key_files(all_files, repo_path)

    # T015: Detect primary language
    primary_language = detect_language(all_files)

    # T016: Detect test framework
    has_tests, test_framework = detect_test_framework(all_files, primary_language)

    # T017: Infer project type
    project_type, has_docker, has_kubernetes, has_ci = detect_project_type(
        key_files, root_directories
    )

    # T018: Detect conventions
    detected_patterns, notable_files = detect_conventions(
        all_files, primary_language, root_directories
    )

    # Calculate duration
    duration_ms = int((time.time() - start_time) * 1000)

    # T019: Build analysis JSON output
    analysis = {
        "metadata": {
            "analyzed_at": datetime.utcnow().isoformat() + "Z",
            "analyzer_version": VERSION,
            "repo_root": str(repo_path),
            "total_files": file_count,
            "total_dirs": dir_count,
            "analysis_duration_ms": duration_ms
        },
        "structure": {
            "root_directories": root_directories,
            "max_depth_reached": args.max_depth,
            "ignored_dirs": sorted(list(IGNORE_DIRS))
        },
        "key_files": key_files,
        "patterns": {
            "primary_language": primary_language,
            "has_tests": has_tests,
            "test_framework": test_framework,
            "has_docker": has_docker,
            "has_kubernetes": has_kubernetes,
            "has_ci": has_ci,
            "project_type": project_type
        },
        "conventions": {
            "detected_patterns": detected_patterns,
            "notable_files": notable_files
        },
        "warnings": warnings
    }

    # Display summary
    print(f"Discovered {file_count} files in {dir_count} directories")
    print(f"Key files found: {sum(len(v) for v in key_files.values())}")
    print(f"Warnings: {len(warnings)}")

    # T021: Write output with error handling
    output_path = Path(args.output)
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2)
        print(f"✓ Analysis complete: {output_path}")
        sys.exit(0)
    except Exception as e:
        print(f"Error: Unable to write analysis file: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
