# CI/CD Quick Reference Guide

## Pipeline Status

Check pipeline status: [GitHub Actions](https://github.com/duthaho/pulsewatch/actions)

## Jobs Overview

| Job | Duration | Purpose |
|-----|----------|---------|
| **Lint** | ~2-3 min | Code formatting, linting, type checking |
| **Test (3.11)** | ~5-8 min | Unit, integration, contract tests |
| **Test (3.12)** | ~5-8 min | Unit, integration, contract tests |
| **Docker** | ~3-5 min | Build verification |
| **Security** | ~3-4 min | Vulnerability scanning |

**Total**: ~8-10 minutes (parallel)

## Quick Commands

### Before Committing
```bash
make check              # Run lint + test locally
```

### Before Pushing
```bash
make pre-commit-ci      # Run comprehensive checks
```

### Fix Formatting Issues
```bash
make format             # Auto-fix black + isort
```

### Run Specific Checks
```bash
make lint               # All linting
make test               # All tests
make test-unit          # Unit tests only
make test-integration   # Integration tests only
```

## Required Checks for Merge

- ✅ Lint (Python 3.12)
- ✅ Test (Python 3.11)
- ✅ Test (Python 3.12)
- ✅ Docker Build
- ✅ CI Success
- ✅ Coverage ≥80%

## Skipping CI (Emergency Only)

```bash
git commit -m "fix: emergency hotfix [skip ci]"
```

**Warning**: Only use `[skip ci]` for documentation-only changes or emergencies.

## Re-running Failed Jobs

1. Go to **Actions** tab
2. Click failed workflow
3. Click **Re-run jobs**
4. Choose:
   - **Re-run failed jobs** (faster)
   - **Re-run all jobs** (comprehensive)

## Common Failures

### Lint Failures

**Black formatting**:
```bash
make format
git add .
git commit --amend --no-edit
git push --force-with-lease
```

**Import sorting**:
```bash
isort .
git add .
git commit --amend --no-edit
git push --force-with-lease
```

**Flake8 violations**:
```bash
flake8 .  # Check errors
# Fix manually
git add .
git commit -m "fix: resolve linting issues"
git push
```

### Test Failures

**Run specific test**:
```bash
pytest tests/path/to/test.py::test_name -v
```

**Check coverage**:
```bash
pytest --cov=. --cov-report=term-missing
```

**Database issues**:
```bash
# Check migrations
python manage.py makemigrations --check
python manage.py migrate
```

### Docker Failures

**Test build locally**:
```bash
docker build -t pulsewatch:test .
docker run --rm pulsewatch:test python --version
docker run --rm pulsewatch:test python manage.py check
```

## Branch Protection

### Status Check Requirements

To merge to `main`:
1. All required checks must pass
2. Branch must be up to date
3. Conversations must be resolved

### Override (Admin Only)

Admins can override in emergencies:
1. Go to PR
2. Click "Merge" dropdown
3. Select "Merge without waiting for checks"

**Warning**: Only use for critical hotfixes.

## Coverage Reports

### Viewing Coverage

1. Go to **Actions** tab
2. Click workflow run
3. Scroll to **Artifacts** section
4. Download `coverage-report-python-3.12`
5. Extract and open `htmlcov/index.html`

### Coverage Targets

- **Minimum**: 80% (CI fails below this)
- **Target**: 85%
- **Ideal**: 90%+

## Pipeline Optimization Tips

### Faster Feedback

1. **Run checks locally first**:
   ```bash
   make check  # Catch issues before CI
   ```

2. **Use pre-commit hooks**:
   ```bash
   pre-commit install  # Auto-check on commit
   ```

3. **Push smaller commits**:
   - Faster to review
   - Easier to fix if CI fails
   - Better git history

### Cache Warming

First push after cache clear is slower (~10-15 min). Subsequent pushes are faster (~8-10 min).

## Debugging CI

### View Job Logs

1. Go to **Actions** tab
2. Click workflow run
3. Click job name
4. Expand step to see logs

### Enable Debug Logging

Re-run with debug logging:
1. Go to workflow run
2. Click **Re-run jobs**
3. Check **Enable debug logging**
4. Click **Re-run jobs**

### Common Issues

**Job stuck/timeout**:
- GitHub Actions issue
- Re-run the job

**Service containers not ready**:
- Wait steps should handle this
- Check service logs in CI output

**Cache corruption**:
- Clear cache and re-run
- Contact admin if persists

## Best Practices

### Commit Messages

Follow Conventional Commits:
```bash
git commit -m "feat: add new feature"
git commit -m "fix: resolve bug"
git commit -m "docs: update README"
git commit -m "test: add unit tests"
git commit -m "ci: update workflow"
```

### PR Workflow

1. Create feature branch: `feature/my-feature`
2. Make changes and commit
3. Run `make check` locally
4. Push to GitHub
5. Create pull request
6. Wait for CI to pass
7. Request code review
8. Address feedback
9. Merge when CI passes and approved

### Handling Failures

1. **Don't panic**: CI failures are normal
2. **Read the logs**: Error messages are usually clear
3. **Fix locally**: Test the fix before pushing
4. **Push fix**: CI will re-run automatically
5. **Ask for help**: If stuck, ask the team

## Getting Help

### Documentation

- Pipeline overview: `.github/workflows/README.md`
- Pre-commit optimization: `docs/pre-commit-performance.md`
- Phase 5 summary: `docs/phase5-cicd-summary.md`

### Resources

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [pytest Documentation](https://docs.pytest.org/)
- [Black Documentation](https://black.readthedocs.io/)
- [Django Testing](https://docs.djangoproject.com/en/stable/topics/testing/)

### Team Support

- Check project documentation first
- Search existing issues
- Ask in team chat
- Create GitHub issue if needed

---

**Last Updated**: October 31, 2025
