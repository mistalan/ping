# NetWatchUI.ps1 - User Interface Reference

## Overview

NetWatchUI.ps1 provides a Windows Forms graphical user interface for managing network monitoring tools. The UI consists of two main tabs:

## UI Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Network Monitor Control Panel                                      [_][□][X] │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌────────────────┬────────────────┐                                    │
│  │ Configuration  │    Control     │                                    │
│  └────────────────┴────────────────┘                                    │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │ [Active Tab Content]                                               │ │
│  │                                                                     │ │
│  │                                                                     │ │
│  │                                                                     │ │
│  │                                                                     │ │
│  │                                                                     │ │
│  │                                                                     │ │
│  │                                                                     │ │
│  │                                                                     │ │
│  │                                                                     │ │
│  │                                                                     │ │
│  │                                                                     │ │
│  │                                                                     │ │
│  │                                                                     │ │
│  └───────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

## Configuration Tab

The Configuration tab contains three grouped sections:

### 1. NetWatch.ps1 Settings
```
┌─ NetWatch.ps1 Settings ────────────────────────────────────────────┐
│                                                                     │
│  Interval (seconds):        [30        ]                           │
│                                                                     │
│  Output CSV Path:           [~/Documents/Ping/Log/netwatch...] [...] │
│                                                                     │
│  Ping Targets (comma-sep):  [8.8.8.8,1.1.1.1,192.168.178...]     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Fields:**
- **Interval (seconds)**: How often to check network status (default: 30)
- **Output CSV Path**: Where to save NetWatch logs (default: ~/Documents/Ping/Log/netwatch_log.csv)
- **Ping Targets**: Comma-separated list of hosts/IPs to ping (default: 8.8.8.8,1.1.1.1,192.168.178.1,www.riotgames.com)

### 2. fritzlog_pull.py Settings
```
┌─ fritzlog_pull.py Settings ────────────────────────────────────────┐
│                                                                     │
│  FRITZ!Box Host:       [192.168.178.1   ] Username:  [          ] │
│                                                                     │
│  Password:             [**************   ] Interval:  [30        ] │
│                                                                     │
│  Output CSV Path:      [~/Documents/Ping/Log/fritz_sta...   ] [...] │
│                                                                     │
│  ☑ Enable FRITZ!Box logging (uncheck if you don't have...)        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Fields:**
- **FRITZ!Box Host**: IP address or hostname of your FRITZ!Box router (default: 192.168.178.1)
- **Username**: FRITZ!Box username (optional, often not needed for older setups)
- **Password**: FRITZ!Box password (required if FRITZ!Box logging is enabled)
- **Interval (sec)**: How often to poll FRITZ!Box status (default: 30)
- **Output CSV Path**: Where to save FRITZ!Box logs (default: ~/Documents/Ping/Log/fritz_status_log.csv)
- **Enable FRITZ!Box logging**: Checkbox to enable/disable FRITZ!Box monitoring

### 3. analyze_netlogs.py Settings
```
┌─ analyze_netlogs.py Settings ──────────────────────────────────────┐
│                                                                     │
│  Incidents Output CSV: [~/Documents/Ping/Log/incidents...  ] [...] │
│                                                                     │
│  Latency Threshold (ms):  [20        ] Loss Threshold (%): [1.0  ] │
│                                                                     │
│  ☐ Generate plots (requires matplotlib and pandas)                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Fields:**
- **Incidents Output CSV**: Where to save analysis results (default: ~/Documents/Ping/Log/incidents.csv)
- **Latency Threshold (ms)**: Alert on ping times above this value (default: 20ms)
- **Loss Threshold (%)**: Alert on packet loss above this percentage (default: 1.0%)
- **Generate plots**: Checkbox to enable plot generation (requires matplotlib)

## Control Tab

The Control tab provides runtime controls and monitoring:

### 1. Status Section
```
┌─ Status ────────────────────────────────────────────────────────────┐
│                                                                     │
│  Ready to start tracking                                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

Shows current tracking status:
- "Ready to start tracking" - Initial state
- "Tracking in progress..." (green) - When monitoring is running
- "Tracking stopped" (red) - After stopping tracking

### 2. Tracking Control Section
```
┌─ Tracking Control ──────────────────────────────────────────────────┐
│                                                                     │
│  ┌───────────────────────────────┐  ┌───────────────────────────┐ │
│  │      Start Tracking           │  │      Stop Tracking        │ │
│  └───────────────────────────────┘  └───────────────────────────┘ │
│          (Green Button)                    (Red Button)            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Buttons:**
- **Start Tracking** (Green): Launches NetWatch.ps1 and fritzlog_pull.py (if enabled) in background
- **Stop Tracking** (Red): Terminates all running monitoring processes

### 3. Analysis Section
```
┌─ Analysis ──────────────────────────────────────────────────────────┐
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                    Analyze Logs                               │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                     (Blue Button)                                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Button:**
- **Analyze Logs** (Blue): Runs analyze_netlogs.py to detect network incidents in collected logs

### 4. Activity Log Section
```
┌─ Activity Log ──────────────────────────────────────────────────────┐
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ [2025-10-20 18:37:03] Started NetWatch.ps1 (PID: 1234)     │  │
│  │ [2025-10-20 18:37:04] Started fritzlog_pull.py (PID: 5678) │  │
│  │ [2025-10-20 18:42:15] Stopped NetWatch.ps1                  │  │
│  │ [2025-10-20 18:42:15] Stopped fritzlog_pull.py             │  │
│  │ [2025-10-20 18:43:00] Starting analysis...                  │  │
│  │                                                               │  │
│  │                                                               │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  [Clear Log]  [Open Log Folder]                                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Features:**
- **Activity Log**: Read-only text area showing all actions and messages
- **Clear Log**: Button to clear the activity log display
- **Open Log Folder**: Button to open Windows Explorer to the log output folder

## Usage Flow

### Starting Monitoring

1. Open **Configuration** tab
2. Adjust settings as needed (or keep defaults)
3. Switch to **Control** tab
4. Click **Start Tracking**
5. Monitor status and activity log
6. Let it run for desired duration

### Stopping Monitoring

1. In **Control** tab
2. Click **Stop Tracking**
3. Verify processes stopped in activity log

### Analyzing Logs

1. After collecting data (can be done while tracking or after stopping)
2. In **Control** tab
3. Click **Analyze Logs**
4. Wait for analysis to complete
5. Check activity log for results path
6. Review incidents.csv file

## Keyboard Shortcuts

- **Tab**: Navigate between controls
- **Space/Enter**: Activate focused button
- **Alt+F4**: Close window (with confirmation if tracking is running)

## Background Process Management

When tracking starts:
- NetWatch.ps1 runs in a minimized PowerShell window
- fritzlog_pull.py runs in a minimized Python console window
- Both processes continue running independently
- UI tracks process IDs for proper termination

When tracking stops:
- UI sends termination signal to all tracked processes
- Background windows close automatically

## Error Handling

The UI displays error messages via:
- **Message Boxes**: For critical errors (missing password, file not found, etc.)
- **Activity Log**: For detailed error messages and stack traces

Common error scenarios:
- Missing FRITZ!Box password when enabled
- Python not in PATH
- Log files not found when analyzing
- Permission denied when writing to files

## File Paths

Default paths use Windows standard locations:
- Log files: `%USERPROFILE%\Documents\Ping\Log\`
- Auto-created if they don't exist
- Can be customized using Browse (...) buttons

## Integration with Existing Scripts

The UI is a wrapper that:
- Calls existing scripts with appropriate parameters
- Does NOT modify script behavior
- Scripts can still be used standalone from command line
- Configuration changes in UI don't affect default script behavior

## Limitations

1. **Windows-only**: Uses Windows Forms, requires Windows OS
2. **No real-time log viewing**: Must open CSV files manually to see live data
3. **No background minimization**: UI window must remain open (can be minimized)
4. **Single instance**: Running multiple UI instances may conflict
5. **No scheduling**: Cannot schedule automatic start/stop times (use Task Scheduler separately)

## Tips

- **Save configurations**: Settings persist during session but not across UI restarts
- **Log rotation**: Scripts don't rotate logs automatically; manage file sizes manually
- **Resource usage**: Monitor CPU/memory if running for extended periods
- **FRITZ!Box optional**: Can disable FRITZ!Box logging if you don't have one
- **Test first**: Run for a short period first to verify everything works
