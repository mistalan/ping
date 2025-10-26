# Copilot Instructions for ping Repository

## Overview

Network monitoring tools for ping problems and disconnect analysis. Multi-language repository with **comprehensive test coverage** (80%+ enforced):
- **NetWatch.ps1** / **NetWatchUI.ps1** - PowerShell network monitor (continuous ping, DNS, adapter status) + GUI
- **fritzlog_pull.py** - Python FRITZ!Box router logger (TR-064 API)
- **fritzbox_restart.py** - Python FRITZ!Box restart tool (TR-064 API)
- **analyze_netlogs.py** - Python log analyzer for incident detection
- **visualize_incidents.py** - Python visualization tool for incident reports
- **FritzBoxRestart/** - Android/Kotlin app for FRITZ!Box restart

**Tech:** PowerShell 5+, Python 3.10+, Kotlin, Android SDK 24+

## Structure

```
├── Python Scripts (87% coverage)
│   ├── fritzlog_pull.py (93% coverage)
│   ├── fritzbox_restart.py (94% coverage)
│   ├── analyze_netlogs.py (77% coverage)
│   ├── visualize_incidents.py (95% coverage)
│   └── verify_android_python_match.py (utility)
├── PowerShell Scripts (coverage enabled)
│   ├── NetWatch.ps1
│   └── NetWatchUI.ps1
├── Test Files
│   ├── test_fritzlog_pull.py (27 tests)
│   ├── test_fritzbox_restart.py (20 tests)
│   ├── test_analyze_netlogs.py (37 tests)
│   ├── test_visualize_incidents.py (19 tests)
│   └── NetWatch.Tests.ps1 (Pester)
├── Android/Kotlin App
│   └── FritzBoxRestart/ (JaCoCo coverage)
└── CI/CD (.github/workflows/ci.yml)

## Dependencies

**Python:** `pip install fritzconnection matplotlib pandas`
**Testing:** `pip install pytest pytest-cov`
**PowerShell:** Windows PowerShell 5+ or PowerShell Core 7+
**PowerShell Testing:** Pester module (auto-installed in CI)
**Android:** JDK 17, Android SDK 24+, Gradle 8+

## Testing and Coverage

### Python Tests (103 tests, 87% coverage)
**Run all tests with coverage:**
```bash
pip install pytest pytest-cov fritzconnection matplotlib pandas
pytest test_*.py --cov=. --cov-report=term --cov-report=html --cov-fail-under=80 -v
```

**Individual test files:**
```bash
pytest test_fritzlog_pull.py -v              # 27 tests
pytest test_fritzbox_restart.py -v           # 20 tests
pytest test_analyze_netlogs.py -v            # 37 tests
pytest test_visualize_incidents.py -v        # 19 tests
```

**Coverage threshold:** 80% enforced in CI via `--cov-fail-under=80`

### PowerShell Tests (Pester with coverage)
**Run tests with coverage:**
```powershell
Install-Module -Name Pester -Force -SkipPublisherCheck
$config = New-PesterConfiguration
$config.Run.Path = './NetWatch.Tests.ps1'
$config.CodeCoverage.Enabled = $true
$config.CodeCoverage.Path = @('./NetWatch.ps1', './NetWatchUI.ps1')
$config.CodeCoverage.OutputFormat = 'JaCoCo'
Invoke-Pester -Configuration $config
```

### Android/Kotlin Tests (JaCoCo coverage)
**Run tests with coverage:**
```bash
cd FritzBoxRestart
./gradlew test jacocoTestReport --stacktrace
# Reports: app/build/reports/jacoco/jacocoTestReport/html/index.html
```

### Coverage Configuration
- **Python:** `.coveragerc` (excludes test files, sets 80% minimum)
- **PowerShell:** Pester built-in (JaCoCo XML output)
- **Kotlin:** `build.gradle` (JaCoCo plugin with exclusions)

## Making Changes

**Before changes:**
```bash
pip install fritzconnection pytest pytest-cov matplotlib pandas
```

**Python workflow:**
```bash
# 1. Make changes
# 2. Run tests
pytest test_*.py --cov=. --cov-report=term -v
# 3. Check coverage (must be >= 80%)
pytest test_*.py --cov=. --cov-fail-under=80
# 4. Validate syntax
python3 -m py_compile <file>.py
```

**PowerShell workflow:**
```powershell
# 1. Make changes
# 2. Run tests
Invoke-Pester .\NetWatch.Tests.ps1
# 3. Check coverage
$config = New-PesterConfiguration
$config.CodeCoverage.Enabled = $true
Invoke-Pester -Configuration $config
# 4. Lint
Invoke-ScriptAnalyzer -Path <file>.ps1
```

**Android workflow:**
```bash
# 1. Make changes
# 2. Run tests with coverage
cd FritzBoxRestart && ./gradlew test jacocoTestReport
```

### Common Issues

1. **ModuleNotFoundError: fritzconnection** → `pip install fritzconnection` (always required)
2. **ModuleNotFoundError: matplotlib/pandas** → `pip install matplotlib pandas` (for analysis/viz)
3. **pytest not found** → `pip install pytest pytest-cov`
4. **Get-NetAdapter not recognized (Linux)** → Expected; Windows-only cmdlets
5. **PSScriptAnalyzer warnings** → Acceptable; script functions correctly
6. **Coverage below 80%** → Add more tests or mark code with `# pragma: no cover`
7. **Pester module not found** → `Install-Module -Name Pester -Force`

## Key Implementation Details

**NetWatch.ps1:**
- Auto-creates output directory; writes CSV header if missing
- Infinite loop with error logging to CSV (no crashes)
- Pings: 8.8.8.8, 1.1.1.1, 192.168.178.1, www.riotgames.com
- Logs: adapter status, IPv4/IPv6, gateway, DNS time, ping avg/loss

**fritzlog_pull.py:**
- Python 3.10+ type hints (`str | None` syntax)
- Required `--password` parameter
- Auto-creates CSV header
- Tries WANIPConnection1 → WANPPPConnection1 fallback
- Services: WANIPConnection1/WANPPPConnection1, WANCommonIFC1, WANDSLLinkC1
- `get_safe()` wrapper for error handling

## Quick Reference

**Python test & coverage (all files):**
```bash
pip install pytest pytest-cov fritzconnection matplotlib pandas
pytest test_*.py --cov=. --cov-report=term --cov-fail-under=80 -v
```

**PowerShell test & coverage:**
```powershell
Install-Module -Name Pester -Force
$config = New-PesterConfiguration
$config.Run.Path = './NetWatch.Tests.ps1'
$config.CodeCoverage.Enabled = $true
Invoke-Pester -Configuration $config
```

**Android test & coverage:**
```bash
cd FritzBoxRestart && ./gradlew test jacocoTestReport
```

## Critical Notes
- **80% code coverage required** - enforced in CI/CD pipeline
- **All tests must pass** before merging to main
- **NetWatch.ps1 is Windows-only** - don't make it cross-platform
- **Always install dependencies first** before running tests
- **CI/CD pipeline** runs all tests automatically on push/PR
- **Coverage reports** uploaded as artifacts in GitHub Actions
- **.gitignore excludes** `__pycache__/`, `*.csv`, `*.log`, `htmlcov/`, `.coverage`
