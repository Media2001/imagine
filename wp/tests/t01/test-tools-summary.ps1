# T02 output contracts use explicit Docker boundary doubles, never suite receipts.
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object Text.UTF8Encoding($false)
$env:T01_TEST_ROOT = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$cases = @('pass', 'tool-fail', 'tool-forged-pass', 'tool-missing', 'tool-invalid', 'tool-excluded', 'missing-image')
foreach ($case in $cases) {
    $env:T01_TEST_CASE = $case
    $output = @(& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'mock-wsl.ps1') 2>&1)
    $code = $LASTEXITCODE
    $lines = @($output | ForEach-Object { $_.ToString() } | Where-Object { $_.Trim() })
    $pass = $case -in @('pass', 'tool-excluded')
    $status = if ($pass) { 'PASS' } else { 'FAIL' }
    if ($code -ne $(if ($pass) { 0 } else { 1 }) -or $lines[-1] -notmatch ('^REJEU : \d+ tests, \d+ assertions, \d+ .+ ' + $status + '$')) { throw ($case + ' : ' + ($lines -join "`n")) }
    if ($lines[-2] -notmatch '^OUTILS : \d+ outils, \d+ contr.+les, \d+ .+checs ; hors rejeu : .+$') { throw ($case + ' : missing penultimate tool summary : ' + ($lines -join "`n")) }
    if ($case -eq 'pass' -and $lines[-2] -notmatch '^OUTILS : 2 outils, 5 contr.+les, 0 .+checs ; hors rejeu : aucun$') { throw ('Tool counts changed : ' + $lines[-2]) }
    if ($case -eq 'tool-excluded' -and $lines[-2] -notmatch 'a90 \(WordPress et base requis\)$') { throw ('Exclusion reason absent : ' + $lines[-2]) }
    Write-Output ('PASS T02 boundary/' + $case + ' : ' + $lines[-2] + ' ; ' + $lines[-1])
}
Remove-Item Env:T01_TEST_CASE, Env:T01_TEST_ROOT
Write-Output ('T02 OUTPUT CONTRACT : ' + $cases.Count + '/' + $cases.Count + ' PASS (boundary doubles only)')
