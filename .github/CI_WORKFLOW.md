# CI Workflow Documentation

## Overview

This repository includes a GitHub Actions CI (Continuous Integration) workflow that automatically checks for errors in all branches whenever code is pushed or pull requests are created.

### Important: Read-Only Checks

The CI workflow is designed to **only check code, never modify it**. It:
- ✅ Validates syntax
- ✅ Runs tests
- ✅ Checks builds
- ✅ Verifies dependencies
- ❌ **Never modifies source files**
- ❌ **Never commits changes**
- ❌ **Never pushes to your repository**

All CI checks are performed in isolated environments that are automatically cleaned up after execution.

## Workflow File Location

The CI workflow is defined in: `.github/workflows/ci.yml`

## What the CI Checks

### 1. Quick Syntax & Lint Checks (`quick-checks`)
- Validates Python syntax in all `.py` files
- Validates frontend `package.json` structure
- Checks basic Python imports
- Provides fast feedback on syntax errors

### 2. Python Backend Tests (`python-backend`)
- Runs on Python 3.8 and 3.9
- Installs all Python dependencies from `requirements.txt`
- Installs system dependencies (OpenBLAS, LAPACK, GTK, etc.)
- Installs optional dependencies gracefully (continues even if dlib fails)
- Runs unit tests from `tests/test_app.py`
- Validates Python syntax in core files
- **Verifies source files remain unchanged** after all checks

### 3. React Frontend Build (`react-frontend`)
- Sets up Node.js 18 environment
- Installs frontend dependencies from `frontend/package.json`
- Attempts to build the React frontend
- **Automatically cleans up build artifacts** (doesn't commit them)
- Validates essential frontend files exist

### 4. CI Summary (`ci-summary`)
- Provides a summary of all check results
- **Final verification that no source files were modified**
- Runs even if some checks fail (`if: always()`)
- Confirms CI was read-only

## When the CI Runs

The workflow is triggered on:
- **Push** to any branch (`*`)
- **Pull Request** to any branch (`*`)

## How CI Ensures Read-Only Behavior

The CI workflow includes multiple safeguards to ensure it never modifies your source code:

1. **Isolated Checkout**: Code is checked out in a fresh, isolated environment each time
2. **Verification Steps**: The workflow includes explicit checks to verify no files were modified:
   ```bash
   git diff --exit-code || (echo "ERROR: Files were modified!" && exit 1)
   ```
3. **Automatic Cleanup**: Temporary build artifacts are automatically removed
4. **Read-Only Operations**: All CI operations are read-only:
   - Syntax checks (compilation without writing)
   - Test execution (read data, write logs only)
   - Build verification (builds in temp directories)
5. **No Commit Permissions**: CI runners don't have permissions to commit changes

## CI Status

You can check the CI status:
- In the GitHub repository under the "Actions" tab
- On pull request pages (shows status checks)
- On commit pages

## Common Issues and Solutions

### dlib Installation Fails
- **Issue**: dlib is a C++ library that can be difficult to install in CI
- **Solution**: The workflow handles this gracefully by attempting installation but continuing if it fails (since tests mock dlib)

### Frontend Build Fails
- **Issue**: React build might fail in CI environment
- **Solution**: Check the logs in the Actions tab for specific error messages. Common issues:
  - Missing dependencies
  - Syntax errors in React components
  - Version conflicts

### Python Tests Fail
- **Issue**: Tests might fail due to missing dependencies or logic errors
- **Solution**: 
  1. Run tests locally: `python -m unittest tests.test_app -v`
  2. Install dependencies: `pip install -r requirements.txt`
  3. Check test output for specific failures

## Running CI Checks Locally

### Python Tests
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python -m unittest tests.test_app -v
# or
python -m pytest tests/test_app.py -v
```

### Frontend Build
```bash
cd frontend
npm install
npm run build
```

### Syntax Check
```bash
# Check all Python files
for file in *.py; do
  python -m py_compile "$file"
done
```

## Customizing the CI

### To modify what gets checked:
1. Edit `.github/workflows/ci.yml`
2. Commit and push changes
3. The workflow will run automatically

### To add more tests:
1. Add test files to `tests/` directory
2. Update the test command in `.github/workflows/ci.yml`
3. The tests will run automatically

### To change Python versions:
Edit the `strategy.matrix` section in `ci.yml`:
```yaml
strategy:
  matrix:
    python-version: ['3.8', '3.9', '3.10']
```

## Branch Protection

Consider setting up branch protection rules in GitHub settings to:
- Require CI to pass before merging
- Block force pushes
- Require pull request reviews

## Workflow Status Badge

Add a status badge to your README:

```markdown
![CI](https://github.com/your-username/Safe_Drive/workflows/CI%20-%20Check%20Changes/badge.svg)
```

Replace `your-username` with your GitHub username.

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Python Testing Best Practices](https://docs.python.org/3/library/unittest.html)
- [React Testing](https://reactjs.org/docs/testing.html)

