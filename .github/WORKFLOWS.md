# GitHub Actions Workflows

This repository uses GitHub Actions for continuous integration, deployment, and release automation.

## Workflow Status

[![CI](https://github.com/mistalan/ping/actions/workflows/ci.yml/badge.svg)](https://github.com/mistalan/ping/actions/workflows/ci.yml)
[![Deploy](https://github.com/mistalan/ping/actions/workflows/deploy.yml/badge.svg)](https://github.com/mistalan/ping/actions/workflows/deploy.yml)
[![CodeQL](https://github.com/mistalan/ping/actions/workflows/codeql.yml/badge.svg)](https://github.com/mistalan/ping/actions/workflows/codeql.yml)
[![Windows Testing](https://github.com/mistalan/ping/actions/workflows/windows-testing.yml/badge.svg)](https://github.com/mistalan/ping/actions/workflows/windows-testing.yml)

## Available Workflows

### CI (Continuous Integration)
- **Trigger**: Push to main/master, Pull Requests
- **Platform**: Windows only
- **Purpose**: Validates code quality and runs tests
- **Jobs**:
  - PowerShell syntax validation and linting with PSScriptAnalyzer
  - Pester unit tests for NetWatch.ps1
  - Python 3.12 validation
  - Python imports and CLI tests
  - Python linting with flake8
  - Security scanning with Trivy

### Deploy
- **Trigger**: Push to main/master, Manual
- **Platform**: Windows only
- **Purpose**: Creates deployment packages with latest code
- **Artifacts**:
  - `ping-latest.zip` - Complete package (ZIP format)
  - `ping-latest.tar.gz` - Complete package (tarball)
  - `checksums-latest.txt` - SHA256 checksums
- **Retention**: 90 days

### Release
- **Trigger**: Git tags matching `v*.*.*` (e.g., v1.0.0), Manual
- **Platform**: Windows only
- **Purpose**: Creates official releases with versioned packages
- **Features**:
  - Runs full test suite before release
  - Creates GitHub Release with release notes
  - Generates ZIP and tarball archives
  - Includes checksums for verification
  - Automatically generates release notes

### CodeQL Security Analysis
- **Trigger**: Push to main/master, Pull Requests, Weekly schedule, Manual
- **Purpose**: Advanced security scanning for vulnerabilities
- **Language**: Python
- **Queries**: Security and quality rules

### Windows Testing
- **Trigger**: Push to main/master, Pull Requests, Daily schedule, Manual
- **Platform**: Windows only
- **Purpose**: Tests scripts on Windows with Python 3.12
- **Tests**:
  - PowerShell syntax and Pester tests
  - Python 3.12 validation
  - Integration testing

## Using the Workflows

### Running Tests Locally

Before pushing code, validate it locally:

**PowerShell:**
```powershell
# Install dependencies
Install-Module -Name PSScriptAnalyzer -Force -Scope CurrentUser
Install-Module -Name Pester -Force -Scope CurrentUser

# Validate syntax
$ast = [System.Management.Automation.Language.Parser]::ParseFile("./NetWatch.ps1", [ref]$null, [ref]$null)

# Run linter
Invoke-ScriptAnalyzer -Path ./NetWatch.ps1

# Run tests
Invoke-Pester ./NetWatch.Tests.ps1
```

**Python:**
```bash
# Install dependencies
pip install fritzconnection flake8

# Validate syntax
python -m py_compile fritzlog_pull.py
python -m py_compile analyze_netlogs.py

# Test imports
python -c "import fritzlog_pull"
python -c "import analyze_netlogs"

# Lint code
flake8 *.py
```

### Creating a Release

1. **Option 1: Using Git Tags (Recommended)**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **Option 2: Manual Workflow Dispatch**
   - Go to Actions → Release
   - Click "Run workflow"
   - Enter version (e.g., v1.0.0)
   - Click "Run workflow"

### Downloading Artifacts

**Latest Build (from Deploy workflow):**
- Go to Actions → Deploy → Latest successful run
- Download `ping-latest-zip` or `ping-latest-tarball`

**Release Builds:**
- Go to Releases
- Download the latest release package

## Workflow Dependencies

The workflows use the following GitHub Actions from the marketplace:

- **actions/checkout@v4** - Check out repository code
- **actions/setup-python@v5** - Set up Python environment
- **actions/upload-artifact@v4** - Upload build artifacts
- **github/codeql-action@v3** - CodeQL security analysis
- **aquasecurity/trivy-action** - Trivy vulnerability scanner
- **softprops/action-gh-release@v1** - Create GitHub releases

All dependencies are automatically kept up to date by Dependabot.

## Security

- **CodeQL** scans for security vulnerabilities in Python code
- **Trivy** scans for vulnerabilities in dependencies and filesystem
- Security scan results are uploaded to GitHub Security tab
- Scans run on every push, PR, and weekly via scheduled jobs

## Troubleshooting

### Python Version Compatibility
The scripts require Python 3.12. All workflows are optimized for Windows with Python 3.12.

### Artifact Download Issues
Artifacts from the Deploy workflow expire after 90 days. For permanent downloads, use Releases instead.
