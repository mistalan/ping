# Copilot Instructions for ping Repository

## Overview

Network monitoring tools for ping problems and disconnect analysis. **Very small repo** (3 source files, ~200 lines):
- **NetWatch.ps1** - Windows PowerShell network monitor (continuous ping, DNS, adapter status)
- **fritzlog_pull.py** - Python FRITZ!Box router logger (TR-064 API)

**Tech:** PowerShell 5+ (Windows-only), Python 3.10+ (requires `fritzconnection`)

⚠️ **NetWatch.ps1 is Windows-only** - uses `Get-NetAdapter`, `Get-NetIPAddress`, `Get-NetRoute` (unavailable on Linux/macOS). Only syntax validation possible on non-Windows.

## Structure

```
├── README.md (3 lines)
├── NetWatch.ps1 (77 lines)
├── fritzlog_pull.py (119 lines)
└── .github/copilot-instructions.md
```
**No tests, no CI/CD, no build configs.**

## Dependencies

**Python:** `pip install fritzconnection` (v1.15.0+)
**PowerShell:** Windows PowerShell 5+ or PowerShell Core 7+

## Validation Commands

### NetWatch.ps1
Monitors adapter status, pings targets (8.8.8.8, 1.1.1.1, 192.168.178.1, www.riotgames.com), checks DNS, logs to CSV.

**Syntax check (Linux-safe):**
```powershell
pwsh -Command '$ast = [System.Management.Automation.Language.Parser]::ParseFile("./NetWatch.ps1", [ref]$null, [ref]$null); if ($ast) { "Syntax OK" }'
```

**Lint:**
```powershell
pwsh -Command "Invoke-ScriptAnalyzer -Path ./NetWatch.ps1"
```
Expected warnings (acceptable): PSUseBOMForUnicodeEncodedFile, PSUseSingularNouns

**Run (Windows only):**
```powershell
pwsh -File ./NetWatch.ps1 -IntervalSeconds 30 -OutCsv "C:\temp\test.csv"
```
Runs indefinitely; Ctrl+C to stop. Params: `-IntervalSeconds`, `-OutCsv`, `-PingTargets`

### fritzlog_pull.py
Logs FRITZ!Box WAN status, uptime, IP, traffic, DSL to CSV via TR-064.

**Always install dependency first:** `pip install fritzconnection`

**Validation:**
```bash
python3 -m py_compile fritzlog_pull.py
python3 -c "import fritzlog_pull; print('Imports OK')"
python3 fritzlog_pull.py --help
```

**Run (needs FRITZ!Box):**
```bash
python3 fritzlog_pull.py --host 192.168.178.1 --password <pw> --interval 30 --out /tmp/test.csv
```
Required: `--password`. Optional: `--host`, `--user`, `--interval`, `--out`. Runs indefinitely; Ctrl+C to stop.

## Making Changes

**Before changes:** `pip install fritzconnection`

**Python validation workflow:**
```bash
pip install fritzconnection
python3 -m py_compile fritzlog_pull.py
python3 -c "import fritzlog_pull"
python3 fritzlog_pull.py --help
```

**PowerShell validation (Linux):**
```bash
pwsh -Command '$ast = [System.Management.Automation.Language.Parser]::ParseFile("./NetWatch.ps1", [ref]$null, [ref]$null); if ($ast) { "Syntax OK" }'
pwsh -Command "Invoke-ScriptAnalyzer -Path ./NetWatch.ps1"
```

**PowerShell validation (Windows):**
```powershell
pwsh -File ./NetWatch.ps1 -IntervalSeconds 5 -OutCsv "C:\temp\test.csv"
# Run 10-15s, Ctrl+C, verify CSV created
```

### Common Issues

1. **ModuleNotFoundError: fritzconnection** → `pip install fritzconnection` (always required)
2. **Get-NetAdapter not recognized (Linux)** → Expected; Windows-only cmdlets. Use syntax check only.
3. **PSScriptAnalyzer warnings** → Acceptable; script functions correctly

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

**Python validation (always run in order):**
```bash
pip install fritzconnection
python3 -m py_compile fritzlog_pull.py
python3 -c "import fritzlog_pull"
python3 fritzlog_pull.py --help
```

**PowerShell validation (Linux-safe):**
```bash
pwsh -Command '$ast = [System.Management.Automation.Language.Parser]::ParseFile("./NetWatch.ps1", [ref]$null, [ref]$null); if ($ast) { "Syntax OK" }'
pwsh -Command "Invoke-ScriptAnalyzer -Path ./NetWatch.ps1"
```

## Critical Notes
- **Trust these instructions** - thoroughly tested
- **NetWatch.ps1 is Windows-only** - don't make it cross-platform
- **Always `pip install fritzconnection` first** for Python changes
- **No CI/CD, no tests** - validation is manual only
- **Both scripts run indefinitely** - designed for continuous monitoring
- **.gitignore excludes** `__pycache__/`, `*.csv`, `*.log`
