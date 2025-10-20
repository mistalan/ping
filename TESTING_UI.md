# NetWatchUI.ps1 Testing Guide

This guide describes how to test the Windows Forms UI for network monitoring.

## Prerequisites

- Windows OS (Windows 10/11 or Windows Server)
- PowerShell 5+ or PowerShell Core 7+
- Python 3.10+ installed and accessible via `python3` command
- Python packages: `fritzconnection`, `pandas`, `matplotlib`

## Installation

1. Install Python dependencies:
   ```powershell
   pip install fritzconnection pandas matplotlib
   ```

2. Ensure PowerShell execution policy allows running scripts:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

## Manual Testing Checklist

### 1. Launch Test

- [ ] Run `.\NetWatchUI.ps1`
- [ ] Verify UI window opens with "Network Monitor Control Panel" title
- [ ] Verify two tabs are visible: "Configuration" and "Control"

### 2. Configuration Tab Tests

- [ ] Verify all NetWatch.ps1 settings are visible:
  - [ ] Interval (seconds) - default: 30
  - [ ] Output CSV Path - default: ~/Documents/Ping/Log/netwatch_log.csv
  - [ ] Ping Targets - default: 8.8.8.8,1.1.1.1,192.168.178.1,www.riotgames.com
  - [ ] Browse button works for NetWatch output path

- [ ] Verify all fritzlog_pull.py settings are visible:
  - [ ] FRITZ!Box Host - default: 192.168.178.1
  - [ ] Username - empty by default
  - [ ] Password - masked input
  - [ ] Interval (sec) - default: 30
  - [ ] Output CSV Path - default: ~/Documents/Ping/Log/fritz_status_log.csv
  - [ ] Enable FRITZ!Box logging checkbox - checked by default
  - [ ] Browse button works for FRITZ output path

- [ ] Verify all analyze_netlogs.py settings are visible:
  - [ ] Incidents Output CSV - default: ~/Documents/Ping/Log/incidents.csv
  - [ ] Latency Threshold (ms) - default: 20
  - [ ] Loss Threshold (%) - default: 1.0
  - [ ] Generate plots checkbox - unchecked by default
  - [ ] Browse button works for incidents output path

### 3. Control Tab Tests

- [ ] Verify status shows "Ready to start tracking"
- [ ] Verify "Start Tracking" button is enabled and green
- [ ] Verify "Stop Tracking" button is disabled and red
- [ ] Verify "Analyze Logs" button is enabled and blue
- [ ] Verify Activity Log textbox is empty
- [ ] Verify "Clear Log" button is present
- [ ] Verify "Open Log Folder" button is present

### 4. Start Tracking Tests

**Test 4.1: Start without FRITZ!Box**
- [ ] Uncheck "Enable FRITZ!Box logging" in Configuration tab
- [ ] Switch to Control tab
- [ ] Click "Start Tracking"
- [ ] Verify status changes to "Tracking in progress..." (green)
- [ ] Verify Activity Log shows "Started NetWatch.ps1 (PID: ...)"
- [ ] Verify "Start Tracking" button becomes disabled
- [ ] Verify "Stop Tracking" button becomes enabled
- [ ] Open Task Manager and verify `powershell.exe` process is running
- [ ] Wait 1 minute and verify CSV file is being created at configured path
- [ ] Open CSV file and verify data is being logged

**Test 4.2: Start with FRITZ!Box (if available)**
- [ ] Check "Enable FRITZ!Box logging" in Configuration tab
- [ ] Enter valid FRITZ!Box password
- [ ] Switch to Control tab
- [ ] Click "Start Tracking"
- [ ] Verify status changes to "Tracking in progress..." (green)
- [ ] Verify Activity Log shows both:
  - [ ] "Started NetWatch.ps1 (PID: ...)"
  - [ ] "Started fritzlog_pull.py (PID: ...)"
- [ ] Verify both `powershell.exe` and `python3` processes are running in Task Manager
- [ ] Wait 1 minute and verify both CSV files are being created

**Test 4.3: Start without password (should fail)**
- [ ] Check "Enable FRITZ!Box logging"
- [ ] Leave password field empty
- [ ] Click "Start Tracking"
- [ ] Verify error message: "FRITZ!Box password is required!"
- [ ] Verify tracking does not start

### 5. Stop Tracking Tests

**Test 5.1: Stop tracking**
- [ ] With tracking running, click "Stop Tracking"
- [ ] Verify Activity Log shows "Stopped NetWatch.ps1"
- [ ] Verify Activity Log shows "Stopped fritzlog_pull.py" (if FRITZ enabled)
- [ ] Verify status changes to "Tracking stopped" (red)
- [ ] Verify "Start Tracking" button becomes enabled
- [ ] Verify "Stop Tracking" button becomes disabled
- [ ] Verify processes are terminated in Task Manager

**Test 5.2: Stop when not running**
- [ ] Click "Stop Tracking" when tracking is not running
- [ ] Verify warning message: "Tracking is not running!"

### 6. Analyze Logs Tests

**Test 6.1: Analyze without logs**
- [ ] With no log files present, click "Analyze Logs"
- [ ] Verify error message about missing NetWatch log file

**Test 6.2: Analyze with logs**
- [ ] Run tracking for at least 2 minutes to generate data
- [ ] Stop tracking
- [ ] Click "Analyze Logs"
- [ ] Verify Activity Log shows "Starting analysis..."
- [ ] Verify analysis completes successfully
- [ ] Verify success message shows path to incidents.csv
- [ ] Verify incidents.csv file is created at configured path
- [ ] Open incidents.csv and verify it contains detected incidents

**Test 6.3: Analyze with plots**
- [ ] Check "Generate plots" in Configuration tab
- [ ] Click "Analyze Logs"
- [ ] Verify analysis completes
- [ ] Verify .png plot files are created in the current directory

### 7. UI Features Tests

**Test 7.1: Clear Log**
- [ ] With some text in Activity Log, click "Clear Log"
- [ ] Verify Activity Log is cleared

**Test 7.2: Open Log Folder**
- [ ] Click "Open Log Folder"
- [ ] Verify Windows Explorer opens to the log folder
- [ ] If folder doesn't exist yet, verify info message is shown

**Test 7.3: Browse buttons**
- [ ] Click each "..." browse button
- [ ] Verify Save File Dialog opens
- [ ] Select a path and verify textbox is updated

### 8. Form Closing Tests

**Test 8.1: Close with tracking running**
- [ ] Start tracking
- [ ] Click X to close the window
- [ ] Verify confirmation dialog: "Tracking is still running. Do you want to stop it and exit?"
- [ ] Click "No"
- [ ] Verify window stays open
- [ ] Click X again
- [ ] Click "Yes"
- [ ] Verify processes are stopped and window closes

**Test 8.2: Close without tracking**
- [ ] With tracking stopped, click X to close
- [ ] Verify window closes immediately without confirmation

### 9. Integration Test

**Full workflow test:**
1. [ ] Launch UI
2. [ ] Configure all settings in Configuration tab
3. [ ] Start tracking
4. [ ] Let it run for 5 minutes
5. [ ] Verify log files are growing
6. [ ] Stop tracking
7. [ ] Run analysis
8. [ ] Verify incidents.csv is generated
9. [ ] Open log folder and verify all files are present
10. [ ] Close UI

### 10. Edge Cases

- [ ] Test with very long file paths
- [ ] Test with paths containing spaces
- [ ] Test with non-existent directories (should auto-create)
- [ ] Test with read-only directories (should show error)
- [ ] Test with invalid interval values (non-numeric)
- [ ] Test with invalid threshold values (non-numeric)

## Known Limitations

- UI is Windows-only (uses Windows.Forms)
- Requires python3 to be in PATH
- Background processes run minimized but are visible in Task Manager
- No real-time log viewing (check CSV files directly for live updates)

## Reporting Issues

If you find any bugs or issues, please report them with:
- Windows version
- PowerShell version
- Python version
- Steps to reproduce
- Screenshots if applicable
- Error messages from Activity Log
