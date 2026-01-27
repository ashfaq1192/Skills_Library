# agents-md-gen Reference Documentation

**Version**: 1.0.0
**Created**: 2026-01-27
**Purpose**: Generate AGENTS.md files for repositories following AAIF standards

## Overview

The `agents-md-gen` skill automatically generates AGENTS.md files by analyzing repository structure, identifying key conventions, and producing a standardized document that helps AI agents (Claude Code and Goose) understand how to work with the codebase.

### Key Features

- **Automated Analysis**: Scans repository structure up to 5 directory levels
- **Smart Detection**: Identifies key files (README, config, infrastructure, CI/CD)
- **Convention Recognition**: Detects language, test framework, project type
- **Standards Compliance**: Generates AGENTS.md following AAIF format
- **Cross-Agent Compatible**: Works with both Claude Code and Goose
- **Validation Built-in**: Verifies output quality with exit codes

## Architecture

This skill follows the **MCP Code Execution pattern**:
- **SKILL.md**: ~100 tokens of instructions (loaded into agent context)
- **Scripts**: Heavy logic executed outside context (0 tokens loaded)
- **Minimal Output**: Scripts return concise status messages

### Components

1. **analyze_repo.py**: Repository structure analyzer
   - Input: Repository path
   - Output: `.agents_analysis.json` (intermediate data)
   - Performance: <5 seconds for repos with up to 1,000 files

2. **generate_agents.py**: AGENTS.md generator
   - Input: `.agents_analysis.json`
   - Output: `AGENTS.md` at repository root
   - Template: Uses `scripts/templates/agents_template.md`

3. **validate.py**: Quality validator
   - Input: `AGENTS.md` file path
   - Output: Pass/fail with exit codes
   - Checks: Required sections, content size, format

## Usage

### Single Command Workflow

```bash
# From repository root
python .claude/skills/agents-md-gen/scripts/analyze_repo.py && \
python .claude/skills/agents-md-gen/scripts/generate_agents.py && \
python .claude/skills/agents-md-gen/scripts/validate.py
```

### With Claude Code or Goose

```bash
# Simple prompt
"Use agents-md-gen to generate AGENTS.md"
```

### Detailed Usage

#### 1. Analyze Repository

```bash
python scripts/analyze_repo.py [OPTIONS]

Options:
  [repository_path]     Path to repository (default: current directory)
  --max-depth N         Maximum directory depth (default: 5)
  --output FILE         Output file path (default: .agents_analysis.json)

Exit Codes:
  0 - Success
  1 - Invalid repository path
  2 - Unable to write output file

Example:
  python scripts/analyze_repo.py /path/to/repo --max-depth 6
```

#### 2. Generate AGENTS.md

```bash
python scripts/generate_agents.py [OPTIONS]

Options:
  --input FILE          Analysis JSON file (default: .agents_analysis.json)
  --output FILE         Output markdown file (default: AGENTS.md)
  --template FILE       Template file (default: scripts/templates/agents_template.md)

Exit Codes:
  0 - Success
  1 - Analysis file not found/invalid
  2 - Template file not found
  3 - Unable to write AGENTS.md

Example:
  python scripts/generate_agents.py --input my_analysis.json
```

#### 3. Validate Output

```bash
python scripts/validate.py [OPTIONS]

Options:
  --file FILE           File to validate (default: AGENTS.md)
  --verbose             Show detailed validation results

Exit Codes:
  0 - Pass (all checks successful)
  1 - Fail (validation errors detected)

Example:
  python scripts/validate.py --verbose
```

## Configuration

### Analysis Behavior

The analyzer excludes common directories automatically:
- `node_modules/` - Node.js dependencies
- `venv/`, `.venv/` - Python virtual environments
- `__pycache__/` - Python bytecode
- `.git/` - Git metadata
- `.specify/` - SpecKit Plus files
- `dist/`, `build/` - Build artifacts

### Detection Patterns

**Key Files Detected**:
- Documentation: `README.md`, `CONTRIBUTING.md`, `LICENSE`
- Configuration: `package.json`, `requirements.txt`, `.env.example`, `pyproject.toml`
- Infrastructure: `Dockerfile`, `docker-compose.yml`, `kubernetes.yml`, `k8s/`
- CI/CD: `.github/workflows/`, `.gitlab-ci.yml`, `.circleci/`

**Language Detection** (by file extension count):
- Python: `.py`
- JavaScript: `.js`
- TypeScript: `.ts`
- Go: `.go`
- Rust: `.rs`
- Java: `.java`

**Test Framework Detection**:
- Python: `tests/` directory, `test_*.py` files → pytest
- JavaScript: `*.test.js`, `*.spec.js` → jest/mocha
- Go: `*_test.go` → go test
- Rust: `tests/` in Cargo.toml → cargo test

**Project Type Inference**:
- Monorepo: Multiple package.json or multiple src/ directories
- Web App: Frontend + backend directories
- API: FastAPI/Express/Gin imports detected
- Library: setup.py or Cargo.toml with lib section
- CLI Tool: bin/ directory or console_scripts in setup.py

## Troubleshooting

### Issue: Analysis takes too long

**Cause**: Large repository or deep directory structure

**Solutions**:
1. Reduce max depth: `--max-depth 3`
2. Check for symbolic link cycles
3. Ensure excluded directories (node_modules) aren't symlinked

### Issue: "Repository path does not exist" error

**Cause**: Invalid path or permission issue

**Solutions**:
1. Verify path: `ls -la /path/to/repo`
2. Use absolute paths instead of relative
3. Check read permissions: `ls -ld /path/to/repo`

### Issue: Missing sections in generated AGENTS.md

**Cause**: Insufficient repository content or analysis data

**Solutions**:
1. Verify `.agents_analysis.json` contains expected data
2. Re-run analysis: `python scripts/analyze_repo.py`
3. Check template file exists: `ls scripts/templates/agents_template.md`

### Issue: Validation fails on valid file

**Cause**: Section headers don't match expected format

**Solutions**:
1. Run with `--verbose` to see which checks fail
2. Verify section headers use `#` or `##` markdown format
3. Ensure minimum 100 bytes content requirement met

### Issue: Permission denied during analysis

**Cause**: Restricted directory access

**Solutions**:
- This is expected behavior - analyzer logs warning and continues
- Check warnings in `.agents_analysis.json` under `warnings` array
- Inaccessible directories are skipped gracefully

### Issue: Empty repository generates minimal AGENTS.md

**Cause**: Repository has no structure to analyze

**Solutions**:
- This is expected for new/empty repositories
- Generated AGENTS.md will have placeholder content
- Add content to repository and regenerate

## Regeneration Workflow

When repository structure changes:

```bash
# 1. Backup existing (optional)
cp AGENTS.md AGENTS.md.backup

# 2. Re-analyze
python scripts/analyze_repo.py

# 3. Regenerate
python scripts/generate_agents.py

# 4. Validate
python scripts/validate.py

# 5. Compare (optional)
diff AGENTS.md.backup AGENTS.md
```

## Performance Expectations

| Repository Size | Analysis Time | Generation Time | Total Time |
|-----------------|---------------|-----------------|------------|
| Small (<100 files) | <1 second | <0.5 seconds | <2 seconds |
| Medium (100-1,000 files) | 1-3 seconds | <1 second | <5 seconds |
| Large (1,000-10,000 files) | 3-10 seconds | 1-2 seconds | <15 seconds |
| Very Large (>10,000 files) | 10-30 seconds* | 1-2 seconds | <35 seconds* |

*May hit depth limit at 5 levels, which reduces time

## Integration with Claude Code

When Claude Code encounters:
```
"Use agents-md-gen to generate AGENTS.md"
```

It will:
1. Locate skill at `.claude/skills/agents-md-gen/`
2. Read SKILL.md (108 tokens loaded)
3. Execute scripts in sequence
4. Report minimal output to user

## Integration with Goose

Same behavior as Claude Code:
1. Skill placed in `.claude/skills/` directory
2. YAML frontmatter recognized
3. Scripts executed via Python interpreter
4. Exit codes respected for success/failure

## Edge Cases

### Empty or Minimal Repositories
- **Behavior**: Generates minimal AGENTS.md with placeholder sections
- **Example**: Repository with only README.md → includes getting started section

### Very Large Repositories (10,000+ files)
- **Behavior**: Depth limit prevents full traversal
- **Warning**: Logged in `.agents_analysis.json` warnings array
- **Impact**: Some deep directories excluded from structure tree

### Hidden Directories
- **Behavior**: `.git`, `.specify`, `.claude` excluded from tree output
- **Note**: Presence is noted but not included in structure section

### Symbolic Links
- **Behavior**: Followed but cycles detected
- **Protection**: Tracks visited inodes to prevent infinite loops

### Non-UTF-8 Filenames
- **Behavior**: Uses error-tolerant encoding
- **Fallback**: Skips files that can't be decoded, logs warning

### Permission Denied
- **Behavior**: Skips inaccessible directories
- **Logging**: Adds warning to `.agents_analysis.json` warnings array
- **Continuation**: Analysis continues with accessible portions

## Best Practices

1. **Run after major changes**: Regenerate AGENTS.md when:
   - Adding new top-level directories
   - Changing project structure
   - Adding new configuration files
   - Switching languages or frameworks

2. **Commit analysis JSON** (optional):
   - Speeds up regeneration (skip analysis step)
   - Provides historical snapshot
   - Add to `.gitignore` if preferred temporary-only

3. **Validate before committing**:
   - Always run `validate.py` before git commit
   - Fix any reported issues
   - Use `--verbose` to understand failures

4. **Customize template** (advanced):
   - Copy `scripts/templates/agents_template.md`
   - Modify sections for project-specific needs
   - Use `--template` flag with custom path

5. **Automate regeneration** (CI/CD):
   ```yaml
   # .github/workflows/agents-md.yml
   name: Update AGENTS.md
   on:
     push:
       branches: [main]
   jobs:
     update:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - name: Regenerate AGENTS.md
           run: |
             python .claude/skills/agents-md-gen/scripts/analyze_repo.py
             python .claude/skills/agents-md-gen/scripts/generate_agents.py
             python .claude/skills/agents-md-gen/scripts/validate.py
   ```

## Security Considerations

- **No Network Access**: Scripts operate entirely offline
- **Read-Only Analysis**: Never modifies repository (except writing output files)
- **No Code Execution**: Only reads file metadata, not content
- **Standard Library Only**: No external dependencies to vet
- **Permission Respecting**: Gracefully handles denied access

## License and Attribution

Part of Hackathon III: Reusable Intelligence project.
Follows AAIF (AI Agent Integration Format) standards.

## Support

For issues or questions:
1. Check this REFERENCE.md troubleshooting section
2. Review `.agents_analysis.json` warnings array
3. Run validate.py with `--verbose` flag
4. Check repository issues at project source
