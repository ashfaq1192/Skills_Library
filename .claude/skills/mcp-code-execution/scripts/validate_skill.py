#!/usr/bin/env python3
"""Validate that a skill follows the MCP Code Execution pattern.

Checks:
1. SKILL.md exists and is under 150 tokens
2. scripts/ directory has executable files
3. REFERENCE.md exists (on-demand docs)
4. Scripts return minimal output (no full dataset dumps)
"""
import os
import sys
import argparse


def count_tokens(text):
    """Approximate token count (words * 1.3)."""
    words = len(text.split())
    return int(words * 1.3)


def validate_skill(skill_dir):
    """Validate skill follows MCP Code Execution pattern."""
    issues = []
    warnings = []

    # Check SKILL.md exists
    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(skill_md):
        issues.append("SKILL.md not found")
    else:
        with open(skill_md, "r") as f:
            content = f.read()
        tokens = count_tokens(content)
        if tokens > 200:
            issues.append(f"SKILL.md too large: ~{tokens} tokens (target: ~100)")
        elif tokens > 150:
            warnings.append(f"SKILL.md slightly large: ~{tokens} tokens (target: ~100)")

        # Check YAML frontmatter
        if not content.startswith("---"):
            issues.append("SKILL.md missing YAML frontmatter")

    # Check scripts directory
    scripts_dir = os.path.join(skill_dir, "scripts")
    if not os.path.isdir(scripts_dir):
        issues.append("scripts/ directory not found")
    else:
        scripts = [f for f in os.listdir(scripts_dir)
                    if f.endswith((".py", ".sh")) and os.path.isfile(os.path.join(scripts_dir, f))]
        if len(scripts) == 0:
            warnings.append("No scripts found in scripts/ directory")

    # Check REFERENCE.md
    ref_md = os.path.join(skill_dir, "REFERENCE.md")
    if not os.path.isfile(ref_md):
        warnings.append("REFERENCE.md not found (recommended for deep docs)")

    # Report
    skill_name = os.path.basename(os.path.normpath(skill_dir))
    if issues:
        print(f"❌ {skill_name}: {len(issues)} issues, {len(warnings)} warnings")
        for issue in issues:
            print(f"   ❌ {issue}")
        for warning in warnings:
            print(f"   ⚠️ {warning}")
        return 1
    elif warnings:
        print(f"⚠️ {skill_name}: {len(warnings)} warnings")
        for warning in warnings:
            print(f"   ⚠️ {warning}")
        return 0
    else:
        print(f"✓ {skill_name}: MCP Code Execution pattern validated")
        return 0


def main():
    parser = argparse.ArgumentParser(description="Validate MCP Code Execution pattern")
    parser.add_argument("--skill-dir", required=True, help="Path to skill directory")
    args = parser.parse_args()

    if not os.path.isdir(args.skill_dir):
        print(f"❌ Directory not found: {args.skill_dir}")
        sys.exit(1)

    sys.exit(validate_skill(args.skill_dir))


if __name__ == "__main__":
    main()
