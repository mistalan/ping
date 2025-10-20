#requires -Version 5
param(
  [int]$IntervalSeconds = 30,
  [string]$OutCsv = [System.IO.Path]::Combine([Environment]::GetFolderPath('UserProfile'), 'Ping', 'Log', 'netwatch_log.csv'),
  [string[]]$PingTargets = @("8.8.8.8","1.1.1.1","192.168.178.1","www.riotgames.com")
)

$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path (Split-Path $OutCsv) | Out-Null

function ConvertTo-CsvValue($value) {
  # Properly escape CSV values according to RFC 4180
  if ($null -eq $value) {
    return ''
  }
  # Check if it's explicitly an empty string (numeric 0 and $false are converted to strings)
  if ($value -is [string] -and $value -eq '') {
    return ''
  }
  $stringValue = $value.ToString()
  # If value contains comma, quote, newline, or carriage return, wrap in quotes and escape quotes
  if ($stringValue -match '[,"\r\n]') {
    return '"' + $stringValue.Replace('"', '""') + '"'
  }
  return $stringValue
}

function New-CsvHeader($pingTargets) {
  $baseHeaders = @("timestamp", "adapter", "media_status", "ipv4", "ipv6_enabled", "gateway", "dns_ok", "dns_ms")
  $pingHeaders = $pingTargets | ForEach-Object { "ping_${_}_avg_ms"; "ping_${_}_loss_pct" }
  return ($baseHeaders + $pingHeaders) -join ","
}

function New-DataRow($timestamp, $adapter, $media, $ipv4, $ipv6Enabled, $gateway, $dnsOk, $dnsMs, $pingResults) {
  $values = @(
    (ConvertTo-CsvValue $timestamp),
    (ConvertTo-CsvValue $adapter),
    (ConvertTo-CsvValue $media),
    (ConvertTo-CsvValue $ipv4),
    (ConvertTo-CsvValue $ipv6Enabled),
    (ConvertTo-CsvValue $gateway),
    (ConvertTo-CsvValue $dnsOk),
    (ConvertTo-CsvValue $dnsMs)
  )
  foreach ($result in $pingResults) {
    $values += (ConvertTo-CsvValue $result)
  }
  return $values -join ","
}

function New-ErrorRow($timestamp, $errorMessage, $columnCount) {
  # Create an error row that matches the expected column count
  $values = @((ConvertTo-CsvValue $timestamp), "ERROR")
  # Add the error message in the third column
  $values += (ConvertTo-CsvValue $errorMessage)
  # Fill remaining columns with empty values to match header
  for ($i = 3; $i -lt $columnCount; $i++) {
    $values += ""
  }
  return $values -join ","
}

if (-not (Test-Path $OutCsv)) {
  New-CsvHeader $PingTargets | Set-Content -Encoding UTF8 $OutCsv
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
    $ipv4Addresses = Get-NetIPAddress -InterfaceIndex $adapter.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue
    $filteredIpv4 = $ipv4Addresses | Where-Object { $_.PrefixOrigin -ne "WellKnown" }
    $ipv4 = $filteredIpv4 | Select-Object -ExpandProperty IPAddress -First 1
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

    $line = New-DataRow $ts $adapter.Name $media $ipv4 ($ipv6Enabled -as [int]) $gw ($dnsOk -as [int]) $dnsMs $pingResults

    $line | Add-Content -Encoding UTF8 $OutCsv
  } catch {
    # Calculate expected column count from header
    $expectedColumnCount = 8 + ($PingTargets.Count * 2)
    $errorLine = New-ErrorRow (Get-Date).ToString("yyyy-MM-dd HH:mm:ss") $_.Exception.Message $expectedColumnCount
    $errorLine | Add-Content -Encoding UTF8 $OutCsv
  }

  Start-Sleep -Seconds $IntervalSeconds
}
