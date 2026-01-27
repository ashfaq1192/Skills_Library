#!/usr/bin/env python3
"""
AGENTS.md Validator for agents-md-gen skill

Validates AGENTS.md file meets quality standards:
- File exists and has sufficient content (>100 bytes)
- Contains required sections (Project Overview, Project Structure, etc.)

Usage:
    python validate.py [--file FILE] [--verbose]

Exit Codes:
    0 - Pass (all checks successful)
    1 - Fail (validation errors detected)
"""

import argparse
import sys
from pathlib import Path


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Validate AGENTS.md file quality"
    )
    parser.add_argument(
        "--file",
        default="AGENTS.md",
        help="File to validate (default: AGENTS.md)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed validation results"
    )
    return parser.parse_args()


def main():
    """Main entry point for AGENTS.md validator."""
    args = parse_arguments()

    file_path = Path(args.file)

    # T041: Verbose mode output
    if args.verbose:
        print(f"Validating: {file_path}")

    checks_passed = 0
    checks_failed = 0
    errors = []

    # T034: Check 1 - File exists
    if file_path.exists():
        checks_passed += 1
        if args.verbose:
            print("✓ File exists")
    else:
        checks_failed += 1
        errors.append("File does not exist")
        if args.verbose:
            print("✗ File does not exist")
        else:
            print(f"✗ AGENTS.md validation failed: File not found")
        sys.exit(1)

    # Read file content for subsequent checks
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        checks_failed += 1
        errors.append(f"Unable to read file: {e}")
        if args.verbose:
            print(f"✗ Unable to read file: {e}")
        else:
            print(f"✗ AGENTS.md validation failed: Unable to read file")
        sys.exit(1)

    content_lower = content.lower()

    # T035: Check 2 - File size validation
    file_size = file_path.stat().st_size
    if file_size > 100:
        checks_passed += 1
        if args.verbose:
            print(f"✓ File size: {file_size} bytes (minimum: 100)")
    else:
        checks_failed += 1
        errors.append(f"File too small: {file_size} bytes (minimum: 100)")
        if args.verbose:
            print(f"✗ File size: {file_size} bytes (minimum: 100)")

    # T036: Check 3 - Required section: Project Overview
    if "# project overview" in content_lower or "## project overview" in content_lower:
        checks_passed += 1
        if args.verbose:
            print("✓ Required section: Project Overview")
    else:
        checks_failed += 1
        errors.append("Missing section: Project Overview")
        if args.verbose:
            print("✗ Missing section: Project Overview")

    # T037: Check 4 - Required section: Project Structure
    if "# project structure" in content_lower or "## project structure" in content_lower:
        checks_passed += 1
        if args.verbose:
            print("✓ Required section: Project Structure")
    else:
        checks_failed += 1
        errors.append("Missing section: Project Structure")
        if args.verbose:
            print("✗ Missing section: Project Structure")

    # T038: Check 5 - Section containing "convention"
    if "convention" in content_lower:
        checks_passed += 1
        if args.verbose:
            print("✓ Required section: Conventions found")
    else:
        checks_failed += 1
        errors.append("Missing section containing 'convention'")
        if args.verbose:
            print("✗ Missing section containing 'convention'")

    # T039: Check 6 - Section containing "getting started" or "setup"
    if "getting started" in content_lower or "setup" in content_lower:
        checks_passed += 1
        if args.verbose:
            print("✓ Required section: Getting Started or Setup found")
    else:
        checks_failed += 1
        errors.append("Missing section containing 'getting started' or 'setup'")
        if args.verbose:
            print("✗ Missing section containing 'getting started' or 'setup'")

    # T040: Check 7 - Section containing "agent"
    if "agent" in content_lower:
        checks_passed += 1
        if args.verbose:
            print("✓ Required section: Agent guidelines found")
    else:
        checks_failed += 1
        errors.append("Missing section containing 'agent'")
        if args.verbose:
            print("✗ Missing section containing 'agent'")

    # T042: Report results with appropriate exit codes
    total_checks = checks_passed + checks_failed
    if checks_failed == 0:
        if args.verbose:
            print(f"✓ Validation passed ({checks_passed}/{total_checks} checks)")
        else:
            print(f"✓ AGENTS.md validation passed ({checks_passed}/{total_checks} checks)")
        sys.exit(0)  # Exit code 0 for pass
    else:
        if not args.verbose:
            print(f"✗ AGENTS.md validation failed ({checks_failed}/{total_checks} checks)")
            for error in errors:
                print(f"  - {error}")
        sys.exit(1)  # Exit code 1 for fail


if __name__ == "__main__":
    main()
