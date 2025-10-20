BeforeAll {
  # Load the script content but prevent the while loop from executing
  $scriptContent = Get-Content $PSScriptRoot/NetWatch.ps1 -Raw
  # Split at the while loop and only execute the functions
  $functionsOnly = $scriptContent -split 'while \(\$true\)', 2 | Select-Object -First 1
  Invoke-Expression $functionsOnly
}

Describe "Default Parameters" {
  It "OutCsv default path uses UserProfile folder, not MyDocuments" {
    # Parse the script to extract the default OutCsv parameter value
    $scriptPath = "$PSScriptRoot/NetWatch.ps1"
    $ast = [System.Management.Automation.Language.Parser]::ParseFile($scriptPath, [ref]$null, [ref]$null)
    
    # Find the param block
    $paramBlock = $ast.FindAll({$args[0] -is [System.Management.Automation.Language.ParamBlockAst]}, $true) | Select-Object -First 1
    
    # Find the OutCsv parameter
    $outCsvParam = $paramBlock.Parameters | Where-Object { $_.Name.VariablePath.UserPath -eq 'OutCsv' }
    
    # Get the default value expression as a string
    $defaultValueText = $outCsvParam.DefaultValue.Extent.Text
    
    # Verify it uses UserProfile, not MyDocuments
    $defaultValueText | Should -Match "UserProfile"
    $defaultValueText | Should -Not -Match "MyDocuments"
    
    # Verify it uses 'Log' folder
    $defaultValueText | Should -Match "'Log'"
  }
}

Describe "ConvertTo-CsvValue" {
  It "Returns empty string for null value" {
    ConvertTo-CsvValue $null | Should -Be ''
  }

  It "Returns empty string for empty string" {
    ConvertTo-CsvValue '' | Should -Be ''
  }

  It "Returns simple value as-is" {
    ConvertTo-CsvValue "simple" | Should -Be "simple"
  }

  It "Wraps value with comma in quotes" {
    ConvertTo-CsvValue "value, with comma" | Should -Be '"value, with comma"'
  }

  It "Wraps value with quote and escapes quotes" {
    ConvertTo-CsvValue 'value with "quote"' | Should -Be '"value with ""quote"""'
  }

  It "Wraps value with newline in quotes" {
    ConvertTo-CsvValue "value`nwith newline" | Should -Be '"value
with newline"'
  }

  It "Wraps value with carriage return in quotes" {
    $result = ConvertTo-CsvValue "value`rwith cr"
    # The result should wrap the value with quotes because it contains \r
    $result | Should -Match '^\".+\"$'
  }

  It "Handles numeric values" {
    ConvertTo-CsvValue 123 | Should -Be "123"
  }

  It "Handles boolean values" {
    ConvertTo-CsvValue $true | Should -Be "True"
  }
}

Describe "New-CsvHeader" {
  It "Creates header with default ping targets" {
    $targets = @("8.8.8.8","1.1.1.1","192.168.178.1","www.riotgames.com")
    $header = New-CsvHeader $targets
    
    $expected = "timestamp,adapter,media_status,ipv4,ipv6_enabled,gateway,dns_ok,dns_ms," +
                "ping_8.8.8.8_avg_ms,ping_8.8.8.8_loss_pct,ping_1.1.1.1_avg_ms,ping_1.1.1.1_loss_pct," +
                "ping_192.168.178.1_avg_ms,ping_192.168.178.1_loss_pct,ping_www.riotgames.com_avg_ms,ping_www.riotgames.com_loss_pct"
    
    $header | Should -Be $expected
  }

  It "Creates header with single ping target" {
    $targets = @("8.8.8.8")
    $header = New-CsvHeader $targets
    
    $header | Should -Be "timestamp,adapter,media_status,ipv4,ipv6_enabled,gateway,dns_ok,dns_ms,ping_8.8.8.8_avg_ms,ping_8.8.8.8_loss_pct"
  }

  It "Creates header with correct column count" {
    $targets = @("8.8.8.8","1.1.1.1")
    $header = New-CsvHeader $targets
    $columns = $header.Split(',')
    
    $columns.Count | Should -Be (8 + ($targets.Count * 2))
  }
}

Describe "New-DataRow" {
  It "Creates data row with all values" {
    $pingResults = @(10.5, 0, 20.3, 5, 5.2, 0, 15.8, 0)
    $row = New-DataRow "2025-01-01 12:00:00" "Ethernet" "Connected" "192.168.1.100" 1 "192.168.1.1" 1 15 $pingResults
    
    $row | Should -Be "2025-01-01 12:00:00,Ethernet,Connected,192.168.1.100,1,192.168.1.1,1,15,10.5,0,20.3,5,5.2,0,15.8,0"
  }

  It "Creates data row with empty values" {
    $pingResults = @('', 100, '', 100)
    $row = New-DataRow "2025-01-01 12:00:00" "Ethernet" "Connected" "" 0 "" 0 "" $pingResults
    
    $row | Should -Be "2025-01-01 12:00:00,Ethernet,Connected,,0,,0,,,100,,100"
  }

  It "Escapes commas in adapter name" {
    $pingResults = @(10.5, 0)
    $row = New-DataRow "2025-01-01 12:00:00" "Ethernet, Virtual" "Connected" "192.168.1.100" 1 "192.168.1.1" 1 15 $pingResults
    
    $row | Should -Be '2025-01-01 12:00:00,"Ethernet, Virtual",Connected,192.168.1.100,1,192.168.1.1,1,15,10.5,0'
  }

  It "Creates data row with correct column count" {
    $pingResults = @(10.5, 0, 20.3, 5)
    $row = New-DataRow "2025-01-01 12:00:00" "Ethernet" "Connected" "192.168.1.100" 1 "192.168.1.1" 1 15 $pingResults
    $columns = $row.Split(',')
    
    # Should be 8 base columns + 4 ping result columns = 12
    $columns.Count | Should -Be 12
  }

  It "Handles special characters in media status" {
    $pingResults = @(10.5, 0)
    $row = New-DataRow "2025-01-01 12:00:00" "Ethernet" "Status: ""Connected""" "192.168.1.100" 1 "192.168.1.1" 1 15 $pingResults
    
    $row | Should -Be '2025-01-01 12:00:00,Ethernet,"Status: ""Connected""",192.168.1.100,1,192.168.1.1,1,15,10.5,0'
  }
}

Describe "New-ErrorRow" {
  It "Creates error row with correct column count" {
    $errorRow = New-ErrorRow "2025-01-01 12:00:00" "Network adapter not found" 16
    $columns = $errorRow.Split(',')
    
    $columns.Count | Should -Be 16
  }

  It "Creates error row with ERROR marker" {
    $errorRow = New-ErrorRow "2025-01-01 12:00:00" "Some error" 10
    
    $errorRow | Should -Match "^2025-01-01 12:00:00,ERROR,"
  }

  It "Escapes commas in error message" {
    $errorRow = New-ErrorRow "2025-01-01 12:00:00" "Adapter not found, network disconnected" 10
    
    # Use proper CSV parsing instead of naive split
    $tempFile = [System.IO.Path]::GetTempFileName()
    "c1,c2,c3,c4,c5,c6,c7,c8,c9,c10" | Set-Content $tempFile
    $errorRow | Add-Content $tempFile
    $csv = Import-Csv $tempFile
    Remove-Item $tempFile
    
    # Should parse correctly with 10 columns
    $propertyCount = ($csv[0].PSObject.Properties | Measure-Object).Count
    $propertyCount | Should -Be 10
    $csv[0].c3 | Should -Be "Adapter not found, network disconnected"
  }

  It "Fills remaining columns with empty values" {
    $errorRow = New-ErrorRow "2025-01-01 12:00:00" "Error" 16
    
    # Parse the CSV to verify structure
    $tempFile = [System.IO.Path]::GetTempFileName()
    "c1,c2,c3,c4,c5,c6,c7,c8,c9,c10,c11,c12,c13,c14,c15,c16" | Set-Content $tempFile
    $errorRow | Add-Content $tempFile
    $csv = Import-Csv $tempFile
    Remove-Item $tempFile
    
    # Verify timestamp, ERROR marker, error message, and remaining empty columns
    $csv[0].c1 | Should -Be "2025-01-01 12:00:00"
    $csv[0].c2 | Should -Be "ERROR"
    $csv[0].c3 | Should -Be "Error"
    $csv[0].c4 | Should -Be ""
    $csv[0].c16 | Should -Be ""
  }

  It "Handles error messages with quotes" {
    $errorRow = New-ErrorRow "2025-01-01 12:00:00" 'Error "test" message' 10
    
    # Should properly escape quotes
    $errorRow | Should -Match '^2025-01-01 12:00:00,ERROR,"Error ""test"" message"'
  }
}

Describe "CSV Output Integration" {
  It "Header and data row have matching column counts" {
    $targets = @("8.8.8.8","1.1.1.1","192.168.178.1","www.riotgames.com")
    $header = New-CsvHeader $targets
    $headerColumns = $header.Split(',').Count
    
    $pingResults = @(10.5, 0, 20.3, 5, 5.2, 0, 15.8, 0)
    $row = New-DataRow "2025-01-01 12:00:00" "Ethernet" "Connected" "192.168.1.100" 1 "192.168.1.1" 1 15 $pingResults
    $rowColumns = $row.Split(',').Count
    
    $rowColumns | Should -Be $headerColumns
  }

  It "Header and error row have matching column counts" {
    $targets = @("8.8.8.8","1.1.1.1","192.168.178.1","www.riotgames.com")
    $header = New-CsvHeader $targets
    $headerColumns = $header.Split(',').Count
    
    $errorRow = New-ErrorRow "2025-01-01 12:00:00" "Some error" $headerColumns
    $errorColumns = $errorRow.Split(',').Count
    
    $errorColumns | Should -Be $headerColumns
  }

  It "Can parse CSV output correctly" {
    $targets = @("8.8.8.8")
    $header = New-CsvHeader $targets
    
    $pingResults = @(10.5, 0)
    $row = New-DataRow "2025-01-01 12:00:00" "Ethernet, Virtual" "Connected" "192.168.1.100" 1 "192.168.1.1" 1 15 $pingResults
    
    # Write to temp file and parse
    $tempFile = [System.IO.Path]::GetTempFileName()
    $header | Set-Content $tempFile
    $row | Add-Content $tempFile
    
    $csv = Import-Csv $tempFile
    $csv.Count | Should -Be 1
    $csv[0].timestamp | Should -Be "2025-01-01 12:00:00"
    $csv[0].adapter | Should -Be "Ethernet, Virtual"
    $csv[0].ipv4 | Should -Be "192.168.1.100"
    
    Remove-Item $tempFile
  }

  It "Can parse CSV with error row correctly" {
    $targets = @("8.8.8.8")
    $header = New-CsvHeader $targets
    $headerColumns = $header.Split(',').Count
    
    $errorRow = New-ErrorRow "2025-01-01 12:00:00" "Network adapter not found, connection lost" $headerColumns
    
    # Write to temp file and parse
    $tempFile = [System.IO.Path]::GetTempFileName()
    $header | Set-Content $tempFile
    $errorRow | Add-Content $tempFile
    
    $csv = Import-Csv $tempFile
    $csv.Count | Should -Be 1
    $csv[0].timestamp | Should -Be "2025-01-01 12:00:00"
    $csv[0].adapter | Should -Be "ERROR"
    $csv[0].media_status | Should -Be "Network adapter not found, connection lost"
    
    Remove-Item $tempFile
  }
}
