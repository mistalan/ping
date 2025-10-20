#requires -Version 5
param(
  [int]$IntervalSeconds = 30,
  [string]$OutCsv = "C:\Users\AlexB\Ping\Log\netwatch_log.csv",
  [string[]]$PingTargets = @("8.8.8.8","1.1.1.1","192.168.178.1","www.riotgames.com")
)

$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path (Split-Path $OutCsv) | Out-Null

if (-not (Test-Path $OutCsv)) {
  "timestamp,adapter,media_status,ipv4,ipv6_enabled,gateway, dns_ok, dns_ms, " + `
  ($PingTargets | ForEach-Object { "ping_${_}_avg_ms,ping_${_}_loss_pct" }) -join "," | `
  Set-Content -Encoding UTF8 $OutCsv
}

function Get-PingStats($target) {
  try {
    # 5 Pings für Mittelwert/Verlust
    $p = Test-Connection -TargetName $target -Count 5 -ErrorAction Stop
    $avg = [math]::Round(($p | Measure-Object -Property ResponseTime -Average).Average, 1)
    $loss = 0
  } catch {
    $avg = ''
    # Verlust = 100% wenn Test-Connection scheitert
    $loss = 100
  }
  return @{ Avg = $avg; Loss = $loss }
}

while ($true) {
  try {
    $ts = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    # aktiver Up-Adapter (kein vEthernet etc.)
    $adapter = Get-NetAdapter | Where-Object { $_.Status -eq 'Up' -and $_.HardwareInterface -eq $true } | Sort-Object -Property ifIndex | Select-Object -First 1
    $media = $adapter.MediaConnectionState
    $ipv4 = (Get-NetIPAddress -InterfaceIndex $adapter.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue | Where-Object {$_.PrefixOrigin -ne "WellKnown"} | Select-Object -ExpandProperty IPAddress -First 1)
    $ipv6Enabled = (Get-NetAdapterBinding -InterfaceDescription $adapter.InterfaceDescription -ComponentID ms_tcpip6).Enabled
    $gw = (Get-NetRoute -InterfaceIndex $adapter.ifIndex -DestinationPrefix "0.0.0.0/0" -ErrorAction SilentlyContinue | Sort-Object RouteMetric | Select-Object -ExpandProperty NextHop -First 1)

    # DNS Check
    $dnsMs = ''
    $dnsOk = $false
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    try {
      $r = Resolve-DnsName -Name "www.google.com" -Type A -ErrorAction Stop
      $sw.Stop()
      $dnsMs = [math]::Round($sw.Elapsed.TotalMilliseconds,0)
      $dnsOk = $true
    } catch {
      $sw.Stop()
      $dnsMs = ''
      $dnsOk = $false
    }

    $pingResults = @()
    foreach ($t in $PingTargets) {
      $stats = Get-PingStats $t
      $pingResults += @($stats.Avg, $stats.Loss)
    }

    $line = @(
      $ts,$adapter.Name,$media,$ipv4,($ipv6Enabled -as [int]),$gw,
      ($dnsOk -as [int]),$dnsMs
    ) + $pingResults

    ($line -join ",") | Add-Content -Encoding UTF8 $OutCsv
  } catch {
    # Fällt nie still – loggt eine Fehlerzeile
    ($("{0},ERROR,{1}" -f (Get-Date).ToString("yyyy-MM-dd HH:mm:ss"), $_.Exception.Message)) | Add-Content -Encoding UTF8 $OutCsv
  }

  Start-Sleep -Seconds $IntervalSeconds
}
