#!/usr/bin/env python3
"""Generate token usage report for all skills in a directory.

Scans .claude/skills/ and reports token consumption for each SKILL.md,
identifying skills that exceed the ~100 token target.
"""
import os
import sys
import argparse


def count_tokens(text):
    """Approximate token count (words * 1.3)."""
    return int(len(text.split()) * 1.3)


def generate_report(skills_root):
    """Generate token usage report for all skills."""
    if not os.path.isdir(skills_root):
        print(f"❌ Skills directory not found: {skills_root}")
        return 1

    skills = sorted([
        d for d in os.listdir(skills_root)
        if os.path.isdir(os.path.join(skills_root, d))
    ])

    if not skills:
        print(f"❌ No skills found in {skills_root}")
        return 1

    total_tokens = 0
    over_budget = 0

    print(f"{'Skill':<30} {'Tokens':>8} {'Status':>8}")
    print("-" * 50)

    for skill in skills:
        skill_md = os.path.join(skills_root, skill, "SKILL.md")
        if not os.path.isfile(skill_md):
            print(f"{skill:<30} {'N/A':>8} {'❌':>8}")
            continue

        with open(skill_md, "r") as f:
            tokens = count_tokens(f.read())

        total_tokens += tokens
        status = "✓"
        if tokens > 200:
            status = "❌"
            over_budget += 1
        elif tokens > 150:
            status = "⚠️"

        print(f"{skill:<30} {f'~{tokens}':>8} {status:>8}")

    print("-" * 50)
    print(f"{'Total':<30} {f'~{total_tokens}':>8}")
    print(f"{'Average':<30} {f'~{total_tokens // len(skills)}':>8}")
    print(f"\n✓ {len(skills) - over_budget}/{len(skills)} skills within budget")

    return 1 if over_budget > 0 else 0


def main():
    parser = argparse.ArgumentParser(description="Token usage report for skills")
    parser.add_argument("--skills-dir", default=".claude/skills",
                        help="Path to skills directory")
    args = parser.parse_args()
    sys.exit(generate_report(args.skills_dir))


if __name__ == "__main__":
    main()
