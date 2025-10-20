#requires -Version 5
<#
.SYNOPSIS
    Simple Windows Forms UI for Network Monitoring Tools
.DESCRIPTION
    Provides a GUI to configure, start, stop, and analyze network monitoring scripts:
    - NetWatch.ps1 (PowerShell network monitor)
    - fritzlog_pull.py (FRITZ!Box logger)
    - analyze_netlogs.py (Log analyzer)
.NOTES
    Requires Windows PowerShell 5+ or PowerShell Core 7+
    Python 3.10+ with fritzconnection package for FRITZ!Box logging
#>

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Global variables for background processes
$script:NetWatchProcess = $null
$script:FritzLogProcess = $null
$script:IsTracking = $false

# Detect available Python command
function Get-PythonCommand {
    # Try python3 first (Linux/WSL style)
    if (Get-Command "python3" -ErrorAction SilentlyContinue) {
        return "python3"
    }
    # Try python (Windows style)
    if (Get-Command "python" -ErrorAction SilentlyContinue) {
        return "python"
    }
    # Try py launcher (Windows Python launcher)
    if (Get-Command "py" -ErrorAction SilentlyContinue) {
        return "py"
    }
    # If none found, default to python and let it fail with a clear error
    return "python"
}

$script:PythonCommand = Get-PythonCommand

# Create the main form
$form = New-Object System.Windows.Forms.Form
$form.Text = "Network Monitor Control Panel"
$form.Size = New-Object System.Drawing.Size(700, 650)
$form.StartPosition = "CenterScreen"
$form.FormBorderStyle = "FixedDialog"
$form.MaximizeBox = $false

# Create TabControl
$tabControl = New-Object System.Windows.Forms.TabControl
$tabControl.Location = New-Object System.Drawing.Point(10, 10)
$tabControl.Size = New-Object System.Drawing.Size(665, 590)

# ===== Configuration Tab =====
$tabConfig = New-Object System.Windows.Forms.TabPage
$tabConfig.Text = "Configuration"
$tabConfig.UseVisualStyleBackColor = $true

$yPos = 10

# NetWatch Configuration Group
$groupNetWatch = New-Object System.Windows.Forms.GroupBox
$groupNetWatch.Location = New-Object System.Drawing.Point(10, $yPos)
$groupNetWatch.Size = New-Object System.Drawing.Size(630, 120)
$groupNetWatch.Text = "NetWatch.ps1 Settings"

$labelInterval = New-Object System.Windows.Forms.Label
$labelInterval.Location = New-Object System.Drawing.Point(10, 25)
$labelInterval.Size = New-Object System.Drawing.Size(150, 20)
$labelInterval.Text = "Interval (seconds):"
$groupNetWatch.Controls.Add($labelInterval)

$textInterval = New-Object System.Windows.Forms.TextBox
$textInterval.Location = New-Object System.Drawing.Point(160, 22)
$textInterval.Size = New-Object System.Drawing.Size(100, 20)
$textInterval.Text = "30"
$groupNetWatch.Controls.Add($textInterval)

$labelNetWatchOut = New-Object System.Windows.Forms.Label
$labelNetWatchOut.Location = New-Object System.Drawing.Point(10, 55)
$labelNetWatchOut.Size = New-Object System.Drawing.Size(150, 20)
$labelNetWatchOut.Text = "Output CSV Path:"
$groupNetWatch.Controls.Add($labelNetWatchOut)

$textNetWatchOut = New-Object System.Windows.Forms.TextBox
$textNetWatchOut.Location = New-Object System.Drawing.Point(160, 52)
$textNetWatchOut.Size = New-Object System.Drawing.Size(400, 20)
$defaultNetWatchPath = [System.IO.Path]::Combine([Environment]::GetFolderPath('MyDocuments'), 'Ping', 'Log', 'netwatch_log.csv')
$textNetWatchOut.Text = $defaultNetWatchPath
$groupNetWatch.Controls.Add($textNetWatchOut)

$btnBrowseNetWatch = New-Object System.Windows.Forms.Button
$btnBrowseNetWatch.Location = New-Object System.Drawing.Point(570, 50)
$btnBrowseNetWatch.Size = New-Object System.Drawing.Size(50, 23)
$btnBrowseNetWatch.Text = "..."
$btnBrowseNetWatch.Add_Click({
    $saveDialog = New-Object System.Windows.Forms.SaveFileDialog
    $saveDialog.Filter = "CSV files (*.csv)|*.csv|All files (*.*)|*.*"
    $saveDialog.FileName = [System.IO.Path]::GetFileName($textNetWatchOut.Text)
    $saveDialog.InitialDirectory = [System.IO.Path]::GetDirectoryName($textNetWatchOut.Text)
    if ($saveDialog.ShowDialog() -eq "OK") {
        $textNetWatchOut.Text = $saveDialog.FileName
    }
})
$groupNetWatch.Controls.Add($btnBrowseNetWatch)

$labelPingTargets = New-Object System.Windows.Forms.Label
$labelPingTargets.Location = New-Object System.Drawing.Point(10, 85)
$labelPingTargets.Size = New-Object System.Drawing.Size(150, 20)
$labelPingTargets.Text = "Ping Targets (comma-sep):"
$groupNetWatch.Controls.Add($labelPingTargets)

$textPingTargets = New-Object System.Windows.Forms.TextBox
$textPingTargets.Location = New-Object System.Drawing.Point(160, 82)
$textPingTargets.Size = New-Object System.Drawing.Size(460, 20)
$textPingTargets.Text = "8.8.8.8,1.1.1.1,192.168.178.1,www.riotgames.com"
$groupNetWatch.Controls.Add($textPingTargets)

$tabConfig.Controls.Add($groupNetWatch)
$yPos += 130

# FRITZ!Box Configuration Group
$groupFritz = New-Object System.Windows.Forms.GroupBox
$groupFritz.Location = New-Object System.Drawing.Point(10, $yPos)
$groupFritz.Size = New-Object System.Drawing.Size(630, 150)
$groupFritz.Text = "fritzlog_pull.py Settings"

$labelFritzHost = New-Object System.Windows.Forms.Label
$labelFritzHost.Location = New-Object System.Drawing.Point(10, 25)
$labelFritzHost.Size = New-Object System.Drawing.Size(150, 20)
$labelFritzHost.Text = "FRITZ!Box Host:"
$groupFritz.Controls.Add($labelFritzHost)

$textFritzHost = New-Object System.Windows.Forms.TextBox
$textFritzHost.Location = New-Object System.Drawing.Point(160, 22)
$textFritzHost.Size = New-Object System.Drawing.Size(200, 20)
$textFritzHost.Text = "192.168.178.1"
$groupFritz.Controls.Add($textFritzHost)

$labelFritzUser = New-Object System.Windows.Forms.Label
$labelFritzUser.Location = New-Object System.Drawing.Point(370, 25)
$labelFritzUser.Size = New-Object System.Drawing.Size(80, 20)
$labelFritzUser.Text = "Username:"
$groupFritz.Controls.Add($labelFritzUser)

$textFritzUser = New-Object System.Windows.Forms.TextBox
$textFritzUser.Location = New-Object System.Drawing.Point(450, 22)
$textFritzUser.Size = New-Object System.Drawing.Size(170, 20)
$textFritzUser.Text = ""
$groupFritz.Controls.Add($textFritzUser)

$labelFritzPassword = New-Object System.Windows.Forms.Label
$labelFritzPassword.Location = New-Object System.Drawing.Point(10, 55)
$labelFritzPassword.Size = New-Object System.Drawing.Size(150, 20)
$labelFritzPassword.Text = "Password:"
$groupFritz.Controls.Add($labelFritzPassword)

$textFritzPassword = New-Object System.Windows.Forms.TextBox
$textFritzPassword.Location = New-Object System.Drawing.Point(160, 52)
$textFritzPassword.Size = New-Object System.Drawing.Size(200, 20)
$textFritzPassword.UseSystemPasswordChar = $true
$groupFritz.Controls.Add($textFritzPassword)

$labelFritzInterval = New-Object System.Windows.Forms.Label
$labelFritzInterval.Location = New-Object System.Drawing.Point(370, 55)
$labelFritzInterval.Size = New-Object System.Drawing.Size(80, 20)
$labelFritzInterval.Text = "Interval (sec):"
$groupFritz.Controls.Add($labelFritzInterval)

$textFritzInterval = New-Object System.Windows.Forms.TextBox
$textFritzInterval.Location = New-Object System.Drawing.Point(450, 52)
$textFritzInterval.Size = New-Object System.Drawing.Size(100, 20)
$textFritzInterval.Text = "30"
$groupFritz.Controls.Add($textFritzInterval)

$labelFritzOut = New-Object System.Windows.Forms.Label
$labelFritzOut.Location = New-Object System.Drawing.Point(10, 85)
$labelFritzOut.Size = New-Object System.Drawing.Size(150, 20)
$labelFritzOut.Text = "Output CSV Path:"
$groupFritz.Controls.Add($labelFritzOut)

$textFritzOut = New-Object System.Windows.Forms.TextBox
$textFritzOut.Location = New-Object System.Drawing.Point(160, 82)
$textFritzOut.Size = New-Object System.Drawing.Size(400, 20)
$defaultFritzPath = [System.IO.Path]::Combine([Environment]::GetFolderPath('MyDocuments'), 'Ping', 'Log', 'fritz_status_log.csv')
$textFritzOut.Text = $defaultFritzPath
$groupFritz.Controls.Add($textFritzOut)

$btnBrowseFritz = New-Object System.Windows.Forms.Button
$btnBrowseFritz.Location = New-Object System.Drawing.Point(570, 80)
$btnBrowseFritz.Size = New-Object System.Drawing.Size(50, 23)
$btnBrowseFritz.Text = "..."
$btnBrowseFritz.Add_Click({
    $saveDialog = New-Object System.Windows.Forms.SaveFileDialog
    $saveDialog.Filter = "CSV files (*.csv)|*.csv|All files (*.*)|*.*"
    $saveDialog.FileName = [System.IO.Path]::GetFileName($textFritzOut.Text)
    $saveDialog.InitialDirectory = [System.IO.Path]::GetDirectoryName($textFritzOut.Text)
    if ($saveDialog.ShowDialog() -eq "OK") {
        $textFritzOut.Text = $saveDialog.FileName
    }
})
$groupFritz.Controls.Add($btnBrowseFritz)

$checkEnableFritz = New-Object System.Windows.Forms.CheckBox
$checkEnableFritz.Location = New-Object System.Drawing.Point(10, 115)
$checkEnableFritz.Size = New-Object System.Drawing.Size(400, 20)
$checkEnableFritz.Text = "Enable FRITZ!Box logging (uncheck if you don't have a FRITZ!Box)"
$checkEnableFritz.Checked = $true
$groupFritz.Controls.Add($checkEnableFritz)

$tabConfig.Controls.Add($groupFritz)
$yPos += 160

# Analyzer Configuration Group
$groupAnalyze = New-Object System.Windows.Forms.GroupBox
$groupAnalyze.Location = New-Object System.Drawing.Point(10, $yPos)
$groupAnalyze.Size = New-Object System.Drawing.Size(630, 120)
$groupAnalyze.Text = "analyze_netlogs.py Settings"

$labelAnalyzeOut = New-Object System.Windows.Forms.Label
$labelAnalyzeOut.Location = New-Object System.Drawing.Point(10, 25)
$labelAnalyzeOut.Size = New-Object System.Drawing.Size(150, 20)
$labelAnalyzeOut.Text = "Incidents Output CSV:"
$groupAnalyze.Controls.Add($labelAnalyzeOut)

$textAnalyzeOut = New-Object System.Windows.Forms.TextBox
$textAnalyzeOut.Location = New-Object System.Drawing.Point(160, 22)
$textAnalyzeOut.Size = New-Object System.Drawing.Size(400, 20)
$defaultAnalyzePath = [System.IO.Path]::Combine([Environment]::GetFolderPath('MyDocuments'), 'Ping', 'Log', 'incidents.csv')
$textAnalyzeOut.Text = $defaultAnalyzePath
$groupAnalyze.Controls.Add($textAnalyzeOut)

$btnBrowseAnalyze = New-Object System.Windows.Forms.Button
$btnBrowseAnalyze.Location = New-Object System.Drawing.Point(570, 20)
$btnBrowseAnalyze.Size = New-Object System.Drawing.Size(50, 23)
$btnBrowseAnalyze.Text = "..."
$btnBrowseAnalyze.Add_Click({
    $saveDialog = New-Object System.Windows.Forms.SaveFileDialog
    $saveDialog.Filter = "CSV files (*.csv)|*.csv|All files (*.*)|*.*"
    $saveDialog.FileName = [System.IO.Path]::GetFileName($textAnalyzeOut.Text)
    $saveDialog.InitialDirectory = [System.IO.Path]::GetDirectoryName($textAnalyzeOut.Text)
    if ($saveDialog.ShowDialog() -eq "OK") {
        $textAnalyzeOut.Text = $saveDialog.FileName
    }
})
$groupAnalyze.Controls.Add($btnBrowseAnalyze)

$labelLatency = New-Object System.Windows.Forms.Label
$labelLatency.Location = New-Object System.Drawing.Point(10, 55)
$labelLatency.Size = New-Object System.Drawing.Size(150, 20)
$labelLatency.Text = "Latency Threshold (ms):"
$groupAnalyze.Controls.Add($labelLatency)

$textLatency = New-Object System.Windows.Forms.TextBox
$textLatency.Location = New-Object System.Drawing.Point(160, 52)
$textLatency.Size = New-Object System.Drawing.Size(100, 20)
$textLatency.Text = "20"
$groupAnalyze.Controls.Add($textLatency)

$labelLoss = New-Object System.Windows.Forms.Label
$labelLoss.Location = New-Object System.Drawing.Point(270, 55)
$labelLoss.Size = New-Object System.Drawing.Size(120, 20)
$labelLoss.Text = "Loss Threshold (%):"
$groupAnalyze.Controls.Add($labelLoss)

$textLoss = New-Object System.Windows.Forms.TextBox
$textLoss.Location = New-Object System.Drawing.Point(390, 52)
$textLoss.Size = New-Object System.Drawing.Size(100, 20)
$textLoss.Text = "1.0"
$groupAnalyze.Controls.Add($textLoss)

$checkPlots = New-Object System.Windows.Forms.CheckBox
$checkPlots.Location = New-Object System.Drawing.Point(10, 85)
$checkPlots.Size = New-Object System.Drawing.Size(400, 20)
$checkPlots.Text = "Generate plots (requires matplotlib and pandas)"
$checkPlots.Checked = $false
$groupAnalyze.Controls.Add($checkPlots)

$tabConfig.Controls.Add($groupAnalyze)

# ===== Control Tab =====
$tabControl2 = New-Object System.Windows.Forms.TabPage
$tabControl2.Text = "Control"
$tabControl2.UseVisualStyleBackColor = $true

$yPosControl = 20

# Status Group
$groupStatus = New-Object System.Windows.Forms.GroupBox
$groupStatus.Location = New-Object System.Drawing.Point(10, $yPosControl)
$groupStatus.Size = New-Object System.Drawing.Size(630, 80)
$groupStatus.Text = "Status"

$labelStatus = New-Object System.Windows.Forms.Label
$labelStatus.Location = New-Object System.Drawing.Point(10, 25)
$labelStatus.Size = New-Object System.Drawing.Size(600, 40)
$labelStatus.Text = "Ready to start tracking"
$labelStatus.Font = New-Object System.Drawing.Font("Microsoft Sans Serif", 10, [System.Drawing.FontStyle]::Bold)
$groupStatus.Controls.Add($labelStatus)

$tabControl2.Controls.Add($groupStatus)
$yPosControl += 90

# Tracking Control Group
$groupTracking = New-Object System.Windows.Forms.GroupBox
$groupTracking.Location = New-Object System.Drawing.Point(10, $yPosControl)
$groupTracking.Size = New-Object System.Drawing.Size(630, 80)
$groupTracking.Text = "Tracking Control"

$btnStartTracking = New-Object System.Windows.Forms.Button
$btnStartTracking.Location = New-Object System.Drawing.Point(20, 30)
$btnStartTracking.Size = New-Object System.Drawing.Size(280, 35)
$btnStartTracking.Text = "Start Tracking"
$btnStartTracking.Font = New-Object System.Drawing.Font("Microsoft Sans Serif", 10, [System.Drawing.FontStyle]::Bold)
$btnStartTracking.BackColor = [System.Drawing.Color]::LightGreen
$btnStartTracking.Add_Click({
    if ($script:IsTracking) {
        [System.Windows.Forms.MessageBox]::Show("Tracking is already running!", "Warning", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Warning)
        return
    }

    try {
        $scriptPath = $PSScriptRoot
        if ([string]::IsNullOrEmpty($scriptPath)) {
            $scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
        }

        # Start NetWatch.ps1
        $netwatchScript = Join-Path $scriptPath "NetWatch.ps1"
        $targets = $textPingTargets.Text -split ',' | ForEach-Object { $_.Trim() }

        $netwatchArgs = @(
            "-NoProfile",
            "-ExecutionPolicy", "Bypass",
            "-File", $netwatchScript,
            "-IntervalSeconds", $textInterval.Text,
            "-OutCsv", $textNetWatchOut.Text,
            "-PingTargets", ($targets -join ',')
        )

        $script:NetWatchProcess = Start-Process -FilePath "powershell.exe" -ArgumentList $netwatchArgs -PassThru -WindowStyle Minimized
        $logOutput.AppendText("[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Started NetWatch.ps1 (PID: $($script:NetWatchProcess.Id))`r`n")

        # Start fritzlog_pull.py if enabled
        if ($checkEnableFritz.Checked) {
            if ([string]::IsNullOrEmpty($textFritzPassword.Text)) {
                [System.Windows.Forms.MessageBox]::Show("FRITZ!Box password is required!", "Error", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
                $script:NetWatchProcess.Kill()
                $script:NetWatchProcess = $null
                return
            }

            $fritzScript = Join-Path $scriptPath "fritzlog_pull.py"
            $fritzArgs = @(
                $fritzScript,
                "--host", $textFritzHost.Text,
                "--password", $textFritzPassword.Text,
                "--interval", $textFritzInterval.Text,
                "--out", $textFritzOut.Text
            )

            if (-not [string]::IsNullOrEmpty($textFritzUser.Text)) {
                $fritzArgs += @("--user", $textFritzUser.Text)
            }

            $script:FritzLogProcess = Start-Process -FilePath $script:PythonCommand -ArgumentList $fritzArgs -PassThru -WindowStyle Minimized
            $logOutput.AppendText("[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Started fritzlog_pull.py (PID: $($script:FritzLogProcess.Id))`r`n")
        }

        $script:IsTracking = $true
        $labelStatus.Text = "Tracking in progress..."
        $labelStatus.ForeColor = [System.Drawing.Color]::Green
        $btnStartTracking.Enabled = $false
        $btnStopTracking.Enabled = $true
    } catch {
        [System.Windows.Forms.MessageBox]::Show("Failed to start tracking: $($_.Exception.Message)", "Error", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
        $logOutput.AppendText("[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] ERROR: $($_.Exception.Message)`r`n")
    }
})
$groupTracking.Controls.Add($btnStartTracking)

$btnStopTracking = New-Object System.Windows.Forms.Button
$btnStopTracking.Location = New-Object System.Drawing.Point(320, 30)
$btnStopTracking.Size = New-Object System.Drawing.Size(280, 35)
$btnStopTracking.Text = "Stop Tracking"
$btnStopTracking.Font = New-Object System.Drawing.Font("Microsoft Sans Serif", 10, [System.Drawing.FontStyle]::Bold)
$btnStopTracking.BackColor = [System.Drawing.Color]::LightCoral
$btnStopTracking.Enabled = $false
$btnStopTracking.Add_Click({
    if (-not $script:IsTracking) {
        [System.Windows.Forms.MessageBox]::Show("Tracking is not running!", "Warning", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Warning)
        return
    }

    try {
        if ($script:NetWatchProcess -and -not $script:NetWatchProcess.HasExited) {
            $script:NetWatchProcess.Kill()
            $logOutput.AppendText("[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Stopped NetWatch.ps1`r`n")
        }

        if ($script:FritzLogProcess -and -not $script:FritzLogProcess.HasExited) {
            $script:FritzLogProcess.Kill()
            $logOutput.AppendText("[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Stopped fritzlog_pull.py`r`n")
        }

        $script:NetWatchProcess = $null
        $script:FritzLogProcess = $null
        $script:IsTracking = $false
        $labelStatus.Text = "Tracking stopped"
        $labelStatus.ForeColor = [System.Drawing.Color]::Red
        $btnStartTracking.Enabled = $true
        $btnStopTracking.Enabled = $false
    } catch {
        [System.Windows.Forms.MessageBox]::Show("Failed to stop tracking: $($_.Exception.Message)", "Error", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
        $logOutput.AppendText("[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] ERROR: $($_.Exception.Message)`r`n")
    }
})
$groupTracking.Controls.Add($btnStopTracking)

$tabControl2.Controls.Add($groupTracking)
$yPosControl += 90

# Analysis Group
$groupAnalysis = New-Object System.Windows.Forms.GroupBox
$groupAnalysis.Location = New-Object System.Drawing.Point(10, $yPosControl)
$groupAnalysis.Size = New-Object System.Drawing.Size(630, 80)
$groupAnalysis.Text = "Analysis"

$btnAnalyze = New-Object System.Windows.Forms.Button
$btnAnalyze.Location = New-Object System.Drawing.Point(20, 30)
$btnAnalyze.Size = New-Object System.Drawing.Size(580, 35)
$btnAnalyze.Text = "Analyze Logs"
$btnAnalyze.Font = New-Object System.Drawing.Font("Microsoft Sans Serif", 10, [System.Drawing.FontStyle]::Bold)
$btnAnalyze.BackColor = [System.Drawing.Color]::LightBlue
$btnAnalyze.Add_Click({
    try {
        $scriptPath = $PSScriptRoot
        if ([string]::IsNullOrEmpty($scriptPath)) {
            $scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
        }

        # Check if log files exist
        if (-not (Test-Path $textNetWatchOut.Text)) {
            [System.Windows.Forms.MessageBox]::Show("NetWatch log file not found: $($textNetWatchOut.Text)`n`nPlease run tracking first to generate logs.", "Error", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
            return
        }

        $analyzeScript = Join-Path $scriptPath "analyze_netlogs.py"
        $analyzeArgs = @(
            $analyzeScript,
            "--netwatch", $textNetWatchOut.Text,
            "--out", $textAnalyzeOut.Text,
            "--latency", $textLatency.Text,
            "--loss", $textLoss.Text
        )

        if ($checkEnableFritz.Checked -and (Test-Path $textFritzOut.Text)) {
            $analyzeArgs += @("--fritz", $textFritzOut.Text)
        } else {
            # Use a dummy fritz file if not available
            $dummyFritz = [System.IO.Path]::GetTempFileName()
            "timestamp,wan_connection_status,wan_uptime_s,wan_external_ip,wan_last_error,common_bytes_sent,common_bytes_recv,dsl_link_status" | Set-Content $dummyFritz
            $analyzeArgs += @("--fritz", $dummyFritz)
        }

        if ($checkPlots.Checked) {
            $analyzeArgs += "--plots"
        }

        $logOutput.AppendText("[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Starting analysis...`r`n")

        # Run analysis and capture output
        $result = & $script:PythonCommand $analyzeArgs 2>&1 | Out-String
        $logOutput.AppendText($result)
        $logOutput.AppendText("[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Analysis complete. Results saved to: $($textAnalyzeOut.Text)`r`n")

        [System.Windows.Forms.MessageBox]::Show("Analysis complete!`n`nResults saved to:`n$($textAnalyzeOut.Text)", "Success", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)
    } catch {
        [System.Windows.Forms.MessageBox]::Show("Failed to analyze logs: $($_.Exception.Message)", "Error", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
        $logOutput.AppendText("[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] ERROR: $($_.Exception.Message)`r`n")
    }
})
$groupAnalysis.Controls.Add($btnAnalyze)

$tabControl2.Controls.Add($groupAnalysis)
$yPosControl += 90

# Log Output Group
$groupLog = New-Object System.Windows.Forms.GroupBox
$groupLog.Location = New-Object System.Drawing.Point(10, $yPosControl)
$groupLog.Size = New-Object System.Drawing.Size(630, 220)
$groupLog.Text = "Activity Log"

$logOutput = New-Object System.Windows.Forms.TextBox
$logOutput.Location = New-Object System.Drawing.Point(10, 20)
$logOutput.Size = New-Object System.Drawing.Size(610, 160)
$logOutput.Multiline = $true
$logOutput.ReadOnly = $true
$logOutput.ScrollBars = "Vertical"
$logOutput.Font = New-Object System.Drawing.Font("Consolas", 9)
$groupLog.Controls.Add($logOutput)

$btnClearLog = New-Object System.Windows.Forms.Button
$btnClearLog.Location = New-Object System.Drawing.Point(10, 185)
$btnClearLog.Size = New-Object System.Drawing.Size(150, 25)
$btnClearLog.Text = "Clear Log"
$btnClearLog.Add_Click({
    $logOutput.Clear()
})
$groupLog.Controls.Add($btnClearLog)

$btnOpenLogFolder = New-Object System.Windows.Forms.Button
$btnOpenLogFolder.Location = New-Object System.Drawing.Point(170, 185)
$btnOpenLogFolder.Size = New-Object System.Drawing.Size(150, 25)
$btnOpenLogFolder.Text = "Open Log Folder"
$btnOpenLogFolder.Add_Click({
    $logFolder = Split-Path $textNetWatchOut.Text
    if (Test-Path $logFolder) {
        Start-Process "explorer.exe" -ArgumentList $logFolder
    } else {
        [System.Windows.Forms.MessageBox]::Show("Log folder does not exist yet: $logFolder", "Info", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)
    }
})
$groupLog.Controls.Add($btnOpenLogFolder)

$tabControl2.Controls.Add($groupLog)

# Add tabs to TabControl
$tabControl.TabPages.Add($tabConfig)
$tabControl.TabPages.Add($tabControl2)

# Add TabControl to form
$form.Controls.Add($tabControl)

# Form closing event
$form.Add_FormClosing({
    if ($script:IsTracking) {
        $result = [System.Windows.Forms.MessageBox]::Show(
            "Tracking is still running. Do you want to stop it and exit?",
            "Confirm Exit",
            [System.Windows.Forms.MessageBoxButtons]::YesNo,
            [System.Windows.Forms.MessageBoxIcon]::Question
        )

        if ($result -eq [System.Windows.Forms.DialogResult]::Yes) {
            if ($script:NetWatchProcess -and -not $script:NetWatchProcess.HasExited) {
                $script:NetWatchProcess.Kill()
            }
            if ($script:FritzLogProcess -and -not $script:FritzLogProcess.HasExited) {
                $script:FritzLogProcess.Kill()
            }
        } else {
            $_.Cancel = $true
        }
    }
})

# Show the form
$form.Add_Shown({
    $form.Activate()
    # Check if Python is available
    if (-not (Get-Command $script:PythonCommand -ErrorAction SilentlyContinue)) {
        [System.Windows.Forms.MessageBox]::Show(
            "Python is not found in your PATH!`n`nPlease install Python and ensure it's accessible via 'python', 'python3', or 'py' command.`n`nFRITZ!Box logging and analysis features will not work without Python.",
            "Python Not Found",
            [System.Windows.Forms.MessageBoxButtons]::OK,
            [System.Windows.Forms.MessageBoxIcon]::Warning
        )
        $logOutput.AppendText("[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] WARNING: Python not found in PATH. Using default command: $($script:PythonCommand)`r`n")
    } else {
        $logOutput.AppendText("[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Python detected: $($script:PythonCommand)`r`n")
    }
})
[void]$form.ShowDialog()
