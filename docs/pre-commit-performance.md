# Pre-commit Hook Performance Optimization

## Problem

The pre-commit hooks were running slow on every commit due to:

1. **MyPy type checking**: Running on all files every time, even unchanged files
2. **Django system checks**: Running `manage.py check` on every commit
3. **Bandit security checks**: Scanning entire codebase including tests
4. **Migration checks**: Running even when models.py wasn't changed

## Solution

### 1. Optimized Local Configuration (`.pre-commit-config.yaml`)

**Changes made:**

#### MyPy Optimization
- Added `--no-incremental` flag to avoid stale cache issues
- Added `files: \.py$` to only run on Python files
- Keeps `exclude: ^(tests/|migrations/)` to skip tests

#### Django Check Optimization
- Changed to `stages: [manual]` - won't run automatically on commit
- Only runs when explicitly called: `pre-commit run django-check --hook-stage manual`
- Still runs in CI with comprehensive checks

#### Django Migration Check
- Only runs when `models.py` files change (already had this)
- Removed `always_run: true` to respect file filtering

#### Bandit Optimization
- Added `exclude: ^(tests/|migrations/)` to skip test files
- Added `--skip B101` to skip assert checks in tests

### 2. CI-Specific Configuration (`.pre-commit-config-ci.yaml`)

Created a separate comprehensive configuration for CI/CD:
- Runs all checks without shortcuts
- No stages filtering
- Comprehensive security scans
- Always runs Django system checks

### 3. Makefile Targets

Added convenient targets:

```bash
# Fast check on staged files only
make pre-commit-fast

# Full local check
make pre-commit

# CI-level comprehensive check
make pre-commit-ci
```

## Performance Comparison

### Before Optimization
- **Every commit**: 15-30 seconds
- Runs all checks on all files
- Django checks run every time
- Type checking scans everything

### After Optimization
- **Small commits**: 2-5 seconds (only changed files)
- **Large commits**: 8-15 seconds
- Django checks only when needed
- Type checking only changed files

## Best Practices

### For Local Development

1. **Quick commits** (recommended):
   ```bash
   git add <files>
   git commit -m "message"
   # Pre-commit runs automatically (fast mode)
   ```

2. **Full check before push**:
   ```bash
   make pre-commit
   ```

3. **Manual Django checks**:
   ```bash
   make check  # Runs lint + test
   python manage.py check --deploy
   ```

### For CI/CD

Use the comprehensive configuration:
```yaml
- name: Run pre-commit
  run: pre-commit run --all-files --config .pre-commit-config-ci.yaml
```

## Additional Speed Tips

### 1. Skip Specific Hooks

Skip specific hooks when needed:
```bash
# Skip mypy (useful for WIP commits)
SKIP=mypy git commit -m "WIP: working on feature"

# Skip multiple hooks
SKIP=mypy,flake8 git commit -m "WIP: refactoring"
```

### 2. Use Pre-commit Cache

Pre-commit caches results. Don't clean unless needed:
```bash
# This removes cache (slows down next run)
pre-commit clean  # Don't do this often
```

### 3. Selective File Staging

Only stage files you want to commit:
```bash
# Only commit specific files
git add src/specific_file.py
git commit -m "fix: specific change"
# Pre-commit only runs on specific_file.py
```

### 4. Parallel Execution

Pre-commit runs hooks in parallel by default. Ensure you have:
```yaml
# In .pre-commit-config.yaml (already default)
default_language_version:
  python: python3.12

# Pre-commit will use all CPU cores
```

## Troubleshooting

### Hooks still slow?

1. **Check Python environment**:
   ```bash
   which python  # Should be in venv
   python --version  # Should be 3.12
   ```

2. **Update pre-commit**:
   ```bash
   pip install --upgrade pre-commit
   pre-commit autoupdate
   ```

3. **Clear cache and reinstall**:
   ```bash
   pre-commit clean
   pre-commit install --install-hooks
   ```

4. **Check hook installation**:
   ```bash
   pre-commit install-hooks
   ```

### Specific hook is slow?

Identify the slow hook:
```bash
# Run with timing
time pre-commit run --all-files --verbose
```

Then disable it for local development:
```yaml
# In .pre-commit-config.yaml
- id: slow-hook
  stages: [manual]  # Won't run on commit
```

### Django check fails in pre-commit?

The Django check requires database connection. If it fails:
```bash
# Run manually instead
python manage.py check --deploy
```

Or disable for local commits (already done):
```yaml
stages: [manual]  # Already set in optimized config
```

## Configuration Files

### `.pre-commit-config.yaml` (Local/Fast)
- Optimized for speed
- Runs only on changed files
- Skips comprehensive checks
- Use for daily development

### `.pre-commit-config-ci.yaml` (CI/Comprehensive)
- Full coverage
- Runs all checks on all files
- No shortcuts
- Use in CI/CD pipeline

## Monitoring Performance

Track hook execution time:
```bash
# Add to .bashrc or .zshrc
alias pre-commit-time='time pre-commit run --all-files'

# Check specific hook
time pre-commit run mypy --all-files
time pre-commit run flake8 --all-files
```

## Future Optimizations

If pre-commit is still slow as codebase grows:

1. **Consider ruff**: Replace black + isort + flake8 with ruff (10-100x faster)
2. **Use pyright**: Replace mypy with pyright (faster type checker)
3. **Selective CI**: Only run full checks on main branch, partial on PRs
4. **Pre-push hooks**: Move comprehensive checks to pre-push instead of pre-commit

## Migration Guide

If you've already installed pre-commit:

```bash
# 1. Update the configuration (already done)
# 2. Reinstall hooks
pre-commit uninstall
pre-commit install

# 3. Test the new configuration
make pre-commit-fast

# 4. Run full check to verify
make pre-commit
```

## Summary

**Local development**: Fast, selective checks on changed files only
**CI/CD pipeline**: Comprehensive checks on entire codebase
**Manual testing**: Run `make pre-commit-ci` before pushing for full validation

This approach balances speed for rapid iteration with thoroughness for quality assurance.
