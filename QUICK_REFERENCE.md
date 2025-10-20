# Quick Reference - CI/CD Pipeline Usage

## For Developers

### Running Tests Locally

Before pushing code, validate locally to catch issues early:

**PowerShell validation:**
```powershell
# Install dependencies (one time)
Install-Module -Name PSScriptAnalyzer -Force -Scope CurrentUser
Install-Module -Name Pester -Force -Scope CurrentUser

# Validate syntax
$ast = [System.Management.Automation.Language.Parser]::ParseFile("./NetWatch.ps1", [ref]$null, [ref]$null)
if ($ast) { "✓ Syntax OK" }

# Run linter (check for errors only)
Invoke-ScriptAnalyzer -Path ./NetWatch.ps1 -Severity Error

# Run tests
Invoke-Pester ./NetWatch.Tests.ps1 -Output Detailed
```

**Python validation:**
```bash
# Install dependencies
pip install fritzconnection flake8

# Validate syntax
python -m py_compile fritzlog_pull.py
python -m py_compile analyze_netlogs.py

# Test imports
python -c "import fritzlog_pull"
python -c "import analyze_netlogs"

# Lint (critical errors only)
flake8 *.py --select=E9,F63,F7,F82
```

### Triggering CI

CI runs automatically on:
- Every push to main/master
- Every pull request to main/master

To manually trigger CI:
1. Go to Actions → CI
2. Click "Run workflow"
3. Select branch
4. Click "Run workflow"

## For Maintainers

### Creating a Release

**Method 1: Git Tags (Recommended)**
```bash
# Tag the release
git tag v1.0.0

# Push the tag
git push origin v1.0.0

# The Release workflow triggers automatically
# Check Actions tab for progress
```

**Method 2: Manual Workflow Dispatch**
1. Go to Actions → Release
2. Click "Run workflow"
3. Enter version (e.g., v1.0.0)
4. Click "Run workflow"
5. Wait for completion
6. Check Releases tab for the new release

### Release Checklist

- [ ] Update version number if needed
- [ ] Update CHANGELOG (if exists)
- [ ] Run tests locally
- [ ] Create and push tag
- [ ] Wait for Release workflow to complete
- [ ] Verify release on GitHub Releases page
- [ ] Test downloaded packages
- [ ] Announce release to users

### Downloading Latest Build

1. Go to Actions → Deploy
2. Click the latest successful run
3. Scroll to "Artifacts" section
4. Download `ping-latest-zip` or `ping-latest-tarball`

### Verifying Package Integrity

After downloading a release:
```bash
# Download the checksums file from the release

# Verify ZIP
sha256sum ping-v1.0.0.zip
# Compare with checksums.txt

# Verify tarball  
sha256sum ping-v1.0.0.tar.gz
# Compare with checksums.txt
```

## For Users

### Downloading Releases

**Option 1: GitHub Releases (Stable)**
1. Go to https://github.com/mistalan/ping/releases
2. Download the latest release ZIP or tarball
3. Extract the archive
4. Follow INSTALL.md instructions

**Option 2: Latest Build (Development)**
1. Go to https://github.com/mistalan/ping/actions/workflows/deploy.yml
2. Click the latest successful run
3. Download artifacts from "Artifacts" section
4. Note: Requires GitHub login

### Installation from Release Package

```bash
# Extract the package
unzip ping-v1.0.0.zip
cd ping-v1.0.0

# Install Python dependencies
pip install -r requirements.txt

# Run the tools
python3 fritzlog_pull.py --password YOUR_PASSWORD
python3 analyze_netlogs.py --netwatch LOG1.csv --fritz LOG2.csv

# On Windows
.\NetWatch.ps1
```

## Workflow Status Badges

Add to your documentation:

```markdown
[![CI](https://github.com/mistalan/ping/actions/workflows/ci.yml/badge.svg)](https://github.com/mistalan/ping/actions/workflows/ci.yml)
[![Deploy](https://github.com/mistalan/ping/actions/workflows/deploy.yml/badge.svg)](https://github.com/mistalan/ping/actions/workflows/deploy.yml)
[![CodeQL](https://github.com/mistalan/ping/actions/workflows/codeql.yml/badge.svg)](https://github.com/mistalan/ping/actions/workflows/codeql.yml)
```

## Troubleshooting

### Workflow Fails on Pull Request

1. Check the Actions tab for error details
2. Review the specific failed job
3. Fix the issue locally
4. Push the fix
5. Workflow runs automatically on push

### Release Workflow Fails

Common issues:
- **Tests fail**: Run tests locally first
- **Tag already exists**: Use a new version number
- **Permission error**: Check repository settings → Actions → General → Workflow permissions

### Artifact Not Found

- Deploy artifacts expire after 90 days
- Use Releases for permanent downloads
- Releases never expire

### Security Alerts

1. Check Security tab for details
2. Review CodeQL or Trivy findings
3. Fix vulnerabilities in code
4. Push fixes
5. Verify alert resolution in next scan

## Advanced Usage

### Customizing Workflows

Edit workflow files in `.github/workflows/`:
- `ci.yml` - CI configuration
- `deploy.yml` - Deployment settings
- `release.yml` - Release process
- `codeql.yml` - Security scanning
- `multi-platform.yml` - Platform testing

After editing, commit and push to apply changes.

### Adding New Tests

1. Add tests to `NetWatch.Tests.ps1` (PowerShell)
2. Create test files for Python scripts (if needed)
3. Update workflow files to run new tests
4. Test locally before committing

### Scheduling Workflows

Workflows can run on schedule:
```yaml
on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight
```

Edit workflow files to add/modify schedules.

## Getting Help

- **Workflow documentation**: See `.github/WORKFLOWS.md`
- **Pipeline overview**: See `PIPELINE_SUMMARY.md`
- **GitHub Actions docs**: https://docs.github.com/actions
- **Issues**: Open an issue on GitHub

## Quick Links

- 📊 [Actions](https://github.com/mistalan/ping/actions)
- 🏷️ [Releases](https://github.com/mistalan/ping/releases)
- 🔒 [Security](https://github.com/mistalan/ping/security)
- 📦 [Packages](https://github.com/mistalan/ping/actions/workflows/deploy.yml)
