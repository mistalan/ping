# NetWatchUI.ps1 - UI Mockup

Since we cannot run the Windows Forms UI on Linux, here is a text-based representation of what the UI looks like:

## Configuration Tab View

```
╔═══════════════════════════════════════════════════════════════════════╗
║ Network Monitor Control Panel                                  [_][□][X] ║
╠═══════════════════════════════════════════════════════════════════════╣
║  ┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓                                        ║
║  ┃ Configuration ┃  Control  ┃                                        ║
║  ┗━━━━━━━━━━━━━━━┻━━━━━━━━━━━┛                                        ║
║                                                                         ║
║  ┌─ NetWatch.ps1 Settings ────────────────────────────────────────┐  ║
║  │                                                                  │  ║
║  │  Interval (seconds):         ┌───────┐                          │  ║
║  │                              │  30   │                          │  ║
║  │                              └───────┘                          │  ║
║  │                                                                  │  ║
║  │  Output CSV Path:            ┌─────────────────────────┐ ┌───┐ │  ║
║  │                              │ ~/Documents/Ping/Log... │ │...│ │  ║
║  │                              └─────────────────────────┘ └───┘ │  ║
║  │                                                                  │  ║
║  │  Ping Targets (comma-sep):   ┌─────────────────────────────┐  │  ║
║  │                              │ 8.8.8.8,1.1.1.1,192.16...│  │  ║
║  │                              └─────────────────────────────┘  │  ║
║  └──────────────────────────────────────────────────────────────────┘  ║
║                                                                         ║
║  ┌─ fritzlog_pull.py Settings ─────────────────────────────────────┐  ║
║  │                                                                  │  ║
║  │  FRITZ!Box Host:    ┌───────────────┐  Username: ┌──────────┐  │  ║
║  │                     │ 192.168.178.1 │            │          │  │  ║
║  │                     └───────────────┘            └──────────┘  │  ║
║  │                                                                  │  ║
║  │  Password:          ┌───────────────┐  Interval: ┌──────────┐  │  ║
║  │                     │ ************* │  (sec)     │    30    │  │  ║
║  │                     └───────────────┘            └──────────┘  │  ║
║  │                                                                  │  ║
║  │  Output CSV Path:   ┌─────────────────────────┐ ┌───┐         │  ║
║  │                     │ ~/Documents/Ping/Log... │ │...│         │  ║
║  │                     └─────────────────────────┘ └───┘         │  ║
║  │                                                                  │  ║
║  │  ☑ Enable FRITZ!Box logging (uncheck if you don't have...)    │  ║
║  │                                                                  │  ║
║  └──────────────────────────────────────────────────────────────────┘  ║
║                                                                         ║
║  ┌─ analyze_netlogs.py Settings ───────────────────────────────────┐  ║
║  │                                                                  │  ║
║  │  Incidents Output:  ┌─────────────────────────┐ ┌───┐         │  ║
║  │  CSV:               │ ~/Documents/Ping/Log... │ │...│         │  ║
║  │                     └─────────────────────────┘ └───┘         │  ║
║  │                                                                  │  ║
║  │  Latency Threshold: ┌────┐  Loss Threshold: ┌──────┐          │  ║
║  │  (ms):              │ 20 │  (%):             │ 1.0  │          │  ║
║  │                     └────┘                   └──────┘          │  ║
║  │                                                                  │  ║
║  │  ☐ Generate plots (requires matplotlib and pandas)             │  ║
║  │                                                                  │  ║
║  └──────────────────────────────────────────────────────────────────┘  ║
║                                                                         ║
╚═══════════════════════════════════════════════════════════════════════╝
```

## Control Tab View

```
╔═══════════════════════════════════════════════════════════════════════╗
║ Network Monitor Control Panel                                  [_][□][X] ║
╠═══════════════════════════════════════════════════════════════════════╣
║  ┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓                                        ║
║  ┃ Configuration ┃  Control  ┃                                        ║
║  ┗━━━━━━━━━━━━━━━┻━━━━━━━━━━━┛                                        ║
║                                                                         ║
║  ┌─ Status ─────────────────────────────────────────────────────────┐ ║
║  │                                                                   │ ║
║  │  Ready to start tracking                                         │ ║
║  │                                                                   │ ║
║  └───────────────────────────────────────────────────────────────────┘ ║
║                                                                         ║
║  ┌─ Tracking Control ───────────────────────────────────────────────┐ ║
║  │                                                                   │ ║
║  │  ┌───────────────────────────┐  ┌─────────────────────────────┐ │ ║
║  │  │                           │  │                             │ │ ║
║  │  │     Start Tracking        │  │      Stop Tracking          │ │ ║
║  │  │                           │  │                             │ │ ║
║  │  └───────────────────────────┘  └─────────────────────────────┘ │ ║
║  │         (Green)                          (Red, Disabled)         │ ║
║  │                                                                   │ ║
║  └───────────────────────────────────────────────────────────────────┘ ║
║                                                                         ║
║  ┌─ Analysis ───────────────────────────────────────────────────────┐ ║
║  │                                                                   │ ║
║  │  ┌───────────────────────────────────────────────────────────┐  │ ║
║  │  │                                                            │  │ ║
║  │  │                 Analyze Logs                              │  │ ║
║  │  │                                                            │  │ ║
║  │  └───────────────────────────────────────────────────────────┘  │ ║
║  │                        (Blue)                                    │ ║
║  │                                                                   │ ║
║  └───────────────────────────────────────────────────────────────────┘ ║
║                                                                         ║
║  ┌─ Activity Log ───────────────────────────────────────────────────┐ ║
║  │                                                                   │ ║
║  │  ┌───────────────────────────────────────────────────────────┐  │ ║
║  │  │                                                            │  │ ║
║  │  │                                                            │  │ ║
║  │  │                                                            │  │ ║
║  │  │                                                            │  │ ║
║  │  │                                                            │  │ ║
║  │  │                                                            │  │ ║
║  │  │                                                            │  │ ║
║  │  └───────────────────────────────────────────────────────────┘  │ ║
║  │                                                                   │ ║
║  │  ┌─────────────┐  ┌──────────────────┐                          │ ║
║  │  │  Clear Log  │  │ Open Log Folder  │                          │ ║
║  │  └─────────────┘  └──────────────────┘                          │ ║
║  │                                                                   │ ║
║  └───────────────────────────────────────────────────────────────────┘ ║
║                                                                         ║
╚═══════════════════════════════════════════════════════════════════════╝
```

## Control Tab - Active Tracking

```
╔═══════════════════════════════════════════════════════════════════════╗
║ Network Monitor Control Panel                                  [_][□][X] ║
╠═══════════════════════════════════════════════════════════════════════╣
║  ┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓                                        ║
║  ┃ Configuration ┃  Control  ┃                                        ║
║  ┗━━━━━━━━━━━━━━━┻━━━━━━━━━━━┛                                        ║
║                                                                         ║
║  ┌─ Status ─────────────────────────────────────────────────────────┐ ║
║  │                                                                   │ ║
║  │  Tracking in progress...                           [GREEN TEXT]  │ ║
║  │                                                                   │ ║
║  └───────────────────────────────────────────────────────────────────┘ ║
║                                                                         ║
║  ┌─ Tracking Control ───────────────────────────────────────────────┐ ║
║  │                                                                   │ ║
║  │  ┌───────────────────────────┐  ┌─────────────────────────────┐ │ ║
║  │  │                           │  │                             │ │ ║
║  │  │     Start Tracking        │  │      Stop Tracking          │ │ ║
║  │  │                           │  │                             │ │ ║
║  │  └───────────────────────────┘  └─────────────────────────────┘ │ ║
║  │      (Green, Disabled)                  (Red, Enabled)          │ ║
║  │                                                                   │ ║
║  └───────────────────────────────────────────────────────────────────┘ ║
║                                                                         ║
║  ┌─ Analysis ───────────────────────────────────────────────────────┐ ║
║  │                                                                   │ ║
║  │  ┌───────────────────────────────────────────────────────────┐  │ ║
║  │  │                                                            │  │ ║
║  │  │                 Analyze Logs                              │  │ ║
║  │  │                                                            │  │ ║
║  │  └───────────────────────────────────────────────────────────┘  │ ║
║  │                        (Blue)                                    │ ║
║  │                                                                   │ ║
║  └───────────────────────────────────────────────────────────────────┘ ║
║                                                                         ║
║  ┌─ Activity Log ───────────────────────────────────────────────────┐ ║
║  │                                                                   │ ║
║  │  ┌───────────────────────────────────────────────────────────┐  │ ║
║  │  │ [2025-10-20 18:37:03] Started NetWatch.ps1 (PID: 12345)  │  │ ║
║  │  │ [2025-10-20 18:37:04] Started fritzlog_pull.py (PID:... │  │ ║
║  │  │                                                            │  │ ║
║  │  │                                                            │  │ ║
║  │  │                                                            │  │ ║
║  │  │                                                            │  │ ║
║  │  │                                                            │  │ ║
║  │  └───────────────────────────────────────────────────────────┘  │ ║
║  │                                                                   │ ║
║  │  ┌─────────────┐  ┌──────────────────┐                          │ ║
║  │  │  Clear Log  │  │ Open Log Folder  │                          │ ║
║  │  └─────────────┘  └──────────────────┘                          │ ║
║  │                                                                   │ ║
║  └───────────────────────────────────────────────────────────────────┘ ║
║                                                                         ║
╚═══════════════════════════════════════════════════════════════════════╝
```

## Key Features Illustrated

### Color Coding
- **Green**: Start Tracking button (active when ready)
- **Red**: Stop Tracking button (active when tracking)
- **Blue**: Analyze Logs button
- **Green Text**: "Tracking in progress..." status message
- **Red Text**: "Tracking stopped" status message (after stopping)

### Button States
- Disabled buttons appear grayed out
- Active buttons are fully visible with proper color
- Start and Stop buttons toggle states based on tracking status

### Activity Log
- Shows timestamped entries
- Displays process IDs for transparency
- Scrollable for long sessions
- Can be cleared with "Clear Log" button

### File Browsers
- "..." buttons open Windows file dialogs
- Allow custom path selection
- Pre-populate with default values

### Checkboxes
- "Enable FRITZ!Box logging" - can disable FRITZ!Box monitoring
- "Generate plots" - optional plot generation during analysis

## Window Properties
- **Size**: 700x650 pixels
- **Style**: Fixed dialog (non-resizable)
- **Position**: Center screen on launch
- **Icon**: Windows default
- **Minimize/Maximize**: Can minimize, cannot maximize

## Technical Notes

This is a pure Windows Forms application created with PowerShell. It:
- Uses `System.Windows.Forms` assembly
- Requires Windows OS
- No external dependencies beyond PowerShell 5+
- Launches child processes for monitoring
- Tracks PIDs for proper cleanup
- Handles form closing gracefully
