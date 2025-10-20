# ping

[![CI](https://github.com/mistalan/ping/actions/workflows/ci.yml/badge.svg)](https://github.com/mistalan/ping/actions/workflows/ci.yml)
[![Deploy](https://github.com/mistalan/ping/actions/workflows/deploy.yml/badge.svg)](https://github.com/mistalan/ping/actions/workflows/deploy.yml)
[![CodeQL](https://github.com/mistalan/ping/actions/workflows/codeql.yml/badge.svg)](https://github.com/mistalan/ping/actions/workflows/codeql.yml)

Network monitoring and diagnostics toolkit for discovering ping problems, analyzing disconnects, and logging network status.

## Overview

This repository provides three complementary tools for comprehensive network monitoring:

1. **NetWatch.ps1** - Windows PowerShell script for continuous network monitoring (ping, DNS, adapter status)
2. **fritzlog_pull.py** - Python script for logging FRITZ!Box router status via TR-064 API
3. **analyze_netlogs.py** - Python script for analyzing collected logs and detecting network incidents

## Prerequisites

### For NetWatch.ps1
- Windows PowerShell 5+ or PowerShell Core 7+
- Windows OS (uses Windows-specific networking cmdlets)
- Administrator privileges recommended for full network adapter access

### For Python Scripts
- Python 3.10 or higher
- Required Python packages:
  - `fritzconnection` (for fritzlog_pull.py)
  - `pandas` (optional, for analyze_netlogs.py - improves performance)
  - `matplotlib` (optional, for analyze_netlogs.py plotting features)

## Installation

### Installing Python Dependencies

```bash
# Required for fritzlog_pull.py
pip install fritzconnection

# Optional for analyze_netlogs.py (recommended)
pip install pandas matplotlib
```

### No Installation Needed for NetWatch.ps1
The PowerShell script can be run directly without installation.

## Usage

### NetWatch.ps1 - Network Monitor

Continuously monitors network status by checking adapter state, pinging multiple targets, testing DNS resolution, and logging all data to CSV.

**Basic usage:**
```powershell
.\NetWatch.ps1
```

**With custom parameters:**
```powershell
.\NetWatch.ps1 -IntervalSeconds 60 -OutCsv "C:\Logs\network.csv" -PingTargets @("8.8.8.8", "1.1.1.1")
```

**Parameters:**
- `-IntervalSeconds` - Monitoring interval in seconds (default: 30)
- `-OutCsv` - Output CSV file path (default: `~/Documents/Ping/Log/netwatch_log.csv`)
- `-PingTargets` - Array of targets to ping (default: `@("8.8.8.8","1.1.1.1","192.168.178.1","www.riotgames.com")`)

**What it monitors:**
- Active network adapter status and media connection state
- IPv4/IPv6 configuration
- Default gateway
- DNS resolution (tests www.google.com)
- Ping latency and packet loss to multiple targets

**Output format:**
CSV file with columns: timestamp, adapter, media_status, ipv4, ipv6_enabled, gateway, dns_ok, dns_ms, and ping statistics (avg_ms and loss_pct) for each target.

The script runs indefinitely until stopped with Ctrl+C. Output directory is created automatically if it doesn't exist.

### fritzlog_pull.py - FRITZ!Box Logger

Logs FRITZ!Box router status including WAN connection state, uptime, external IP, traffic counters, and DSL link status.

**Basic usage:**
```bash
python3 fritzlog_pull.py --password YOUR_PASSWORD
```

**With custom parameters:**
```bash
python3 fritzlog_pull.py --host 192.168.178.1 --password YOUR_PASSWORD --interval 60 --out ~/logs/fritz.csv
```

**Parameters:**
- `--host` - FRITZ!Box IP address (default: 192.168.178.1)
- `--user` - FRITZ!Box username (default: None, often not needed for older setups)
- `--password` - FRITZ!Box password (required)
- `--interval` - Logging interval in seconds (default: 30)
- `--out` - Output CSV file path (default: `~/Ping/Log/fritz_status_log.csv`)

**What it logs:**
- WAN connection status
- Connection uptime in seconds
- External IP address
- Last connection error
- Total bytes sent/received
- DSL link status (if available)

**Output format:**
CSV file with columns: timestamp, wan_connection_status, wan_uptime_s, wan_external_ip, wan_last_error, common_bytes_sent, common_bytes_recv, dsl_link_status.

The script runs indefinitely until stopped with Ctrl+C. Output directory is created automatically if it doesn't exist.

### analyze_netlogs.py - Log Analyzer

Analyzes NetWatch and FRITZ!Box logs to detect and report network incidents such as latency spikes, packet loss, disconnects, and configuration changes.

**Basic usage:**
```bash
python3 analyze_netlogs.py --netwatch netwatch_log.csv --fritz fritz_status_log.csv
```

**With custom parameters:**
```bash
python3 analyze_netlogs.py --netwatch netwatch_log.csv --fritz fritz_status_log.csv --out incidents.csv --latency 50 --loss 5.0 --plots
```

**Parameters:**
- `--netwatch` - Path to NetWatch CSV log (required)
- `--fritz` - Path to FRITZ!Box CSV log (required)
- `--out` - Output incidents CSV file (default: incidents.csv)
- `--latency` - Latency spike threshold in ms (default: 20)
- `--loss` - Packet loss spike threshold in percent (default: 1.0)
- `--plots` - Generate latency plots (requires matplotlib and pandas)

**What it detects:**
- DNS resolution failures
- Network adapter status changes
- Media connection state changes
- Latency spikes above threshold
- Packet loss above threshold
- WAN reconnects (uptime resets)
- WAN status changes
- External IP changes
- DSL link abnormalities

**Output format:**
CSV file with columns: source (PC/FRITZ), type (incident type), start, end, duration, details.

The script also prints a summary of detected incidents to the console and optionally generates latency plots for each ping target.

## Example Workflow

1. Start network monitoring on your PC:
   ```powershell
   .\NetWatch.ps1 -IntervalSeconds 30
   ```

2. Start FRITZ!Box logging (in a separate terminal):
   ```bash
   python3 fritzlog_pull.py --password YOUR_PASSWORD --interval 30
   ```

3. Let both scripts run for a period of time (hours or days) to collect data

4. Analyze the collected logs:
   ```bash
   python3 analyze_netlogs.py --netwatch ~/Documents/Ping/Log/netwatch_log.csv --fritz ~/Ping/Log/fritz_status_log.csv --out incidents.csv --plots
   ```

5. Review the generated incidents.csv and plots to identify network problems

## Testing

Run the PowerShell tests:
```powershell
# Install Pester if needed
Install-Module -Name Pester -Force -SkipPublisherCheck

# Run tests
Invoke-Pester .\NetWatch.Tests.ps1
```

## File Descriptions

- **NetWatch.ps1** - PowerShell network monitoring script with CSV logging
- **NetWatch.Tests.ps1** - Pester unit tests for NetWatch.ps1 functions
- **fritzlog_pull.py** - FRITZ!Box TR-064 API logger
- **analyze_netlogs.py** - Log analysis and incident detection tool
- **.gitignore** - Excludes log files, cache, and build artifacts

## Tips

- Run NetWatch.ps1 continuously in the background to build a historical network quality baseline
- Use Task Scheduler (Windows) or systemd (Linux with WSL) to run scripts automatically at system startup
- Adjust thresholds in analyze_netlogs.py based on your network quality expectations
- Default ping targets include Google DNS (8.8.8.8), Cloudflare DNS (1.1.1.1), your router (192.168.178.1), and a game server (www.riotgames.com) - customize as needed
- CSV logs can be imported into Excel or other analysis tools for custom visualizations

## Troubleshooting

**NetWatch.ps1:**
- If you get permission errors, run PowerShell as Administrator
- On non-Windows systems, the script will not work as it uses Windows-specific cmdlets

**fritzlog_pull.py:**
- Ensure TR-064 API is enabled in your FRITZ!Box settings (Home Network > Network > Network Settings)
- Verify correct password and network connectivity to FRITZ!Box
- Some older FRITZ!Box models may not support all queried services

**analyze_netlogs.py:**
- Install pandas for better performance and plotting support
- Ensure timestamp formats in CSV files are consistent
- If no incidents are detected, try lowering the threshold values

## CI/CD and Automation

This repository includes a comprehensive GitHub Actions pipeline for continuous integration, deployment, and releases:

- **Continuous Integration**: Automated testing on every push and pull request
  - PowerShell validation with PSScriptAnalyzer and Pester tests
  - Python validation across versions 3.10, 3.11, and 3.12
  - Multi-platform testing (Ubuntu, Windows, macOS)
  - Security scanning with CodeQL and Trivy

- **Automated Deployment**: Package scripts automatically on every push to main
  - Downloads available as workflow artifacts
  - 90-day retention for latest builds

- **Release Management**: Create versioned releases with git tags
  - Automatic package creation (ZIP and tarball)
  - SHA256 checksums for verification
  - Release notes generation

For detailed information about the CI/CD pipeline, see [.github/WORKFLOWS.md](.github/WORKFLOWS.md).

## License

This project is provided as-is for network monitoring and diagnostics purposes.