# Copilot Instructions for ping Repository

## Repository Overview

This repository contains network monitoring tools for checking and logging network traffic, discovering ping problems, and analyzing disconnects. It is a **very small repository** (4 files, ~200 lines of code) with two main monitoring scripts:

1. **NetWatch.ps1** - PowerShell script for continuous network monitoring on Windows
2. **fritzlog_pull.py** - Python script for logging FRITZ!Box router status via TR-064 API

**Languages/Frameworks:**
- PowerShell 5+ (Windows-specific networking cmdlets)
- Python 3.12+ (requires `fritzconnection` package)

**Repository Size:** Minimal - 3 source files, 1 README

## Critical Information: Platform Requirements

⚠️ **NetWatch.ps1 is Windows-only** - It uses Windows-specific PowerShell cmdlets (`Get-NetAdapter`, `Get-NetIPAddress`, `Get-NetRoute`, `Resolve-DnsName`) that are **NOT available on Linux/macOS**. Do not attempt to run or test this script on non-Windows systems. Syntax validation only can be done on Linux with `pwsh`.

## Repository Structure

```
/
├── README.md                  # Brief project description
├── NetWatch.ps1              # Windows network monitoring script (76 lines)
├── fritzlog_pull.py          # FRITZ!Box status logger (118 lines)
└── .github/
    └── copilot-instructions.md
```

**No test files, no CI/CD workflows, no build configuration files exist in this repository.**

## Dependencies

### Python Dependencies
- **Required:** `fritzconnection` (version 1.15.0 or later)
- **Installation:** `pip install fritzconnection`
- The script includes fallback imports for different `fritzconnection` versions

### PowerShell Dependencies
- **Windows PowerShell 5+** or **PowerShell Core 7+**
- Windows-specific networking modules (built-in on Windows)

## Script Usage and Validation

### NetWatch.ps1 (Windows Network Monitor)

**Purpose:** Continuously monitors network adapter status, pings multiple targets, checks DNS, and logs results to CSV.

**Validation Steps (Windows only for full testing):**
1. **Syntax check (works on Linux):**
   ```powershell
   pwsh -Command '$ast = [System.Management.Automation.Language.Parser]::ParseFile("./NetWatch.ps1", [ref]$null, [ref]$null); if ($ast) { "Syntax OK" }'
   ```

2. **Linting (PSScriptAnalyzer):**
   ```powershell
   pwsh -Command "Invoke-ScriptAnalyzer -Path ./NetWatch.ps1"
   ```
   - Expected warnings: PSUseBOMForUnicodeEncodedFile, PSUseSingularNouns
   - These are acceptable and don't indicate broken functionality

3. **Test run (Windows only):**
   ```powershell
   pwsh -File ./NetWatch.ps1 -IntervalSeconds 30 -OutCsv "C:\temp\netwatch_test.csv"
   ```
   - Script runs indefinitely; terminate with Ctrl+C
   - Default interval: 30 seconds
   - Default output: `%USERPROFILE%\Documents\Ping\Log\netwatch_log.csv`

**Parameters:**
- `IntervalSeconds` (int): Polling interval (default: 30)
- `OutCsv` (string): Output CSV path
- `PingTargets` (string[]): Array of hosts/IPs to ping

### fritzlog_pull.py (FRITZ!Box Logger)

**Purpose:** Logs FRITZ!Box WAN status, uptime, external IP, traffic counters, and DSL link status to CSV.

**Validation Steps:**

1. **Syntax check:**
   ```bash
   python3 -m py_compile fritzlog_pull.py
   ```

2. **Import test:**
   ```bash
   python3 -c "import fritzlog_pull; print('Imports OK')"
   ```
   - **IMPORTANT:** This requires `fritzconnection` to be installed first
   - If not installed: `pip install fritzconnection`

3. **Help/usage:**
   ```bash
   python3 fritzlog_pull.py --help
   ```

4. **Test run (requires FRITZ!Box access):**
   ```bash
   python3 fritzlog_pull.py --host 192.168.178.1 --password <password> --interval 30 --out /tmp/fritz_test.csv
   ```
   - Script runs indefinitely; terminate with Ctrl+C
   - **Required parameter:** `--password`
   - Optional: `--host`, `--user`, `--interval`, `--out`

**Key Implementation Details:**
- Uses TR-064 protocol to communicate with FRITZ!Box
- Handles both WANIPConnection1 and WANPPPConnection1 services
- Creates CSV with header on first run
- Runs continuously with specified interval

## Making Changes

### Before Making Changes
1. **Always install Python dependencies first:**
   ```bash
   pip install fritzconnection
   ```

2. **For PowerShell changes:**
   - Test syntax with parser validation (works on Linux)
   - Run `Invoke-ScriptAnalyzer` for linting
   - Full functional testing requires Windows

3. **Understand the platform limitations:**
   - NetWatch.ps1 cannot be functionally tested on Linux
   - fritzlog_pull.py can be tested but needs FRITZ!Box credentials for full validation

### Validation Workflow

**For Python changes:**
```bash
# 1. Install dependencies (if not already installed)
pip install fritzconnection

# 2. Check syntax
python3 -m py_compile fritzlog_pull.py

# 3. Test imports
python3 -c "import fritzlog_pull"

# 4. Verify help works
python3 fritzlog_pull.py --help
```

**For PowerShell changes (on Linux/macOS):**
```bash
# 1. Syntax validation only
pwsh -Command '$ast = [System.Management.Automation.Language.Parser]::ParseFile("./NetWatch.ps1", [ref]$null, [ref]$null); if ($ast) { "Syntax OK" }'

# 2. Run PSScriptAnalyzer
pwsh -Command "Invoke-ScriptAnalyzer -Path ./NetWatch.ps1"
```

**On Windows:**
```powershell
# Full test with short interval
pwsh -File ./NetWatch.ps1 -IntervalSeconds 5 -OutCsv "C:\temp\test.csv"
# Let it run for 10-15 seconds, then Ctrl+C
# Verify CSV was created and contains data
```

### Common Issues and Workarounds

1. **ModuleNotFoundError: No module named 'fritzconnection'**
   - **Solution:** `pip install fritzconnection`
   - This is expected on first run; always install dependencies before testing

2. **"Get-NetAdapter is not recognized" (on Linux)**
   - **This is expected behavior** - NetWatch.ps1 uses Windows-only cmdlets
   - Only syntax and static analysis can be performed on Linux
   - Do not attempt to mock or workaround these cmdlets

3. **PSScriptAnalyzer warnings about plural nouns, unused variables**
   - These are low-severity warnings and acceptable for this codebase
   - The script functions correctly despite these warnings

## File Details

### Root Directory Files
- **README.md** (3 lines): Brief description - "Checks and logs network traffic with tools and scripts to discover ping problems and analyze disconnects"
- **NetWatch.ps1** (77 lines): Windows network monitoring with ping, DNS checks, adapter status
- **fritzlog_pull.py** (119 lines): FRITZ!Box TR-064 API logger
- **.gitignore**: Excludes `__pycache__/`, `*.pyc`, `*.csv`, `*.log`, virtual environments

### Key Code Snippets

**NetWatch.ps1 main loop structure:**
- Requires PowerShell 5+
- Creates output directory automatically
- Writes CSV header if file doesn't exist
- Infinite while loop with configurable interval
- Error handling: logs errors to CSV instead of crashing
- Pings 4 default targets: 8.8.8.8, 1.1.1.1, 192.168.178.1, www.riotgames.com
- Measures: adapter status, IPv4/IPv6, gateway, DNS resolution time, ping avg/loss

**fritzlog_pull.py main features:**
- Python 3.8+ type hints (use `str | None` syntax, requires 3.10+)
- argparse CLI with required `--password` parameter
- Creates CSV header automatically using `ensure_header()`
- Tries WANIPConnection1, falls back to WANPPPConnection1
- Graceful error handling with `get_safe()` wrapper
- TR-064 services: WANIPConnection1/WANPPPConnection1, WANCommonIFC1, WANDSLLinkC1

## Important Reminders

1. **Trust these instructions** - the repository structure and validation steps have been thoroughly tested
2. **Platform awareness** - NetWatch.ps1 is Windows-only; don't try to make it cross-platform
3. **Dependencies matter** - Always install `fritzconnection` before testing Python script
4. **No CI/CD** - There are no automated checks or workflows in this repository
5. **No tests** - There are no unit tests or test frameworks; validation is manual
6. **Scripts run indefinitely** - Both scripts are designed to run continuously until interrupted
7. **CSV output** - Both scripts create CSV files; these are excluded by .gitignore

## Quick Reference Commands

```bash
# Python: Install deps, validate syntax and imports
pip install fritzconnection
python3 -m py_compile fritzlog_pull.py
python3 -c "import fritzlog_pull"
python3 fritzlog_pull.py --help

# PowerShell: Syntax check and lint (Linux-safe)
pwsh -Command '$ast = [System.Management.Automation.Language.Parser]::ParseFile("./NetWatch.ps1", [ref]$null, [ref]$null); if ($ast) { "Syntax OK" }'
pwsh -Command "Invoke-ScriptAnalyzer -Path ./NetWatch.ps1"
```

**Always validate changes using these commands before committing.**
