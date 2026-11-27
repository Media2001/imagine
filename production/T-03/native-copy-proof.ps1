# PARENT ONLY: real Docker replay, after A28 and final declarations/wrappers.
# This script is NOT run by local contract tests and creates no synthetic receipts.
param([Parameter(Mandatory = $true)][string]$Output)
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object Text.UTF8Encoding($false)
$utf8 = New-Object Text.UTF8Encoding($false)
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$out = [IO.Path]::GetFullPath($Output)
if ($out.StartsWith($root + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase) -or $out -eq $root -or (Test-Path -LiteralPath $out)) { throw 'Output must be a new directory outside repository.' }
$scratch = Join-Path $env:LOCALAPPDATA 'hermes/cache/scratch'
if ($env:TMPDIR -and (Test-Path -LiteralPath $env:TMPDIR)) { $scratch = $env:TMPDIR }
$copy = Join-Path $scratch ('t03-native-copy-' + [Guid]::NewGuid().ToString('N'))
$receipt = 'production/A-28/preuves/final/before/native.json'
$proof = [ordered]@{ status = 'FAIL'; native_executed = $false; readiness_claimed = $false; receipt = $receipt; checks = @(); commands = @(); copy_absent = $false }
[void](New-Item -ItemType Directory -Path $out)
$originalHash = $null
function Invoke-CopyReplay {
    param([string]$Label)
    $text = @(& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $copy 'wp/tests/rejouer.ps1') 2>&1)
    $code = $LASTEXITCODE
    $lines = @($text | ForEach-Object { $_.ToString() } | Where-Object { $_.Trim() })
    [IO.File]::WriteAllText((Join-Path $out ($Label + '.log')), ($lines -join "`n") + "`n", $utf8)
    $proof.commands += @{ name = $Label; exit_code = $code; log = $Label + '.log' }
    if ($code -ne 0 -or $lines[-1] -notmatch '^REJEU : [1-9][0-9]* tests, [0-9]+ assertions, 0 .+checs, 0 erreurs, 0 ignor.+ .+ PASS$') { throw 'REPLAY_TESTS_NOT_GREEN' }
    if (@($lines | Where-Object { $_ -match '^T01 CLEANUP : absence verifiee de imagine-t01-[a-f0-9]{32}$' }).Count -ne 1 -or @($lines | Where-Object { $_ -match 'NETTOYAGE EN ECHEC' }).Count) { throw 'CONTAINER_ABSENCE_NOT_PROVED' }
    $markers = @($lines | Where-Object { $_ -match '^T01_RESULT ' })
    if ($markers.Count -ne 1) { throw 'PACKET_MARKER' }
    $packets = ($markers[0].Substring(11) | ConvertFrom-Json).packets
    $expectedLots = @('A-21', 'A-22', 'A-23', 'A-24', 'A-25', 'A-26', 'A-27', 'A-28', 'A-30', 'A-31')
    if (($packets.lots -join ',') -cne ($expectedLots -join ',') -or $packets.verified -ne $expectedLots.Count) { throw 'EXPECTED_CURRENT_PACKETS_NOT_REPLAYED' }
    $a20 = @($packets.excluded | Where-Object { $_.lot -eq 'A-20' -and $_.reason -eq 'declaration absente' })
    if ($a20.Count -ne 1 -or (Test-Path -LiteralPath (Join-Path $copy 'production/A-20/rejeu.json'))) { throw 'A20_MUST_REMAIN_OUTSIDE_REPLAY' }
    if (@($lines | Where-Object { $_ -match '^PAQUETS : ' }).Count -ne 1) { throw 'PACKET_LINE_COUNT' }
    return @{ last = $lines[-1]; packets = $packets; summary = @($lines | Where-Object { $_ -match '^PAQUETS : ' })[0] }
}
try {
    $original = Join-Path $root $receipt
    $originalHash = (Get-FileHash -LiteralPath $original -Algorithm SHA256).Hash
    [void](New-Item -ItemType Directory -Path $copy)
    # Complete source/evidence trees, no Git commands, no ignored-log substitution.
    foreach ($directory in @('wp', 'production', 'files')) {
        Copy-Item -LiteralPath (Join-Path $root $directory) -Destination (Join-Path $copy $directory) -Recurse -Force
    }
    $proof.native_executed = $true
    $green = Invoke-CopyReplay 'green'
    if (@($green.packets.failures).Count -ne 0 -or $green.summary -notmatch '^PAQUETS : [1-9][0-9]* .+, 0 .+checs ; hors rejeu : ') { throw 'BASELINE_PACKETS_NOT_GREEN' }
    $target = Join-Path $copy $receipt
    $before = [IO.File]::ReadAllBytes($target)
    if ($before.Length -eq 0) { throw 'EMPTY_RECEIPT' }
    $after = [byte[]]$before.Clone()
    $after[$after.Length - 1] = $after[$after.Length - 1] -bxor 1
    [IO.File]::WriteAllBytes($target, $after)
    $differences = 0
    for ($i = 0; $i -lt $before.Length; $i++) { if ($before[$i] -ne $after[$i]) { $differences++ } }
    if ($differences -ne 1 -or $before.Length -ne $after.Length) { throw 'NOT_EXACTLY_ONE_BYTE' }
    $red = Invoke-CopyReplay 'one-byte'
    if ($green.last -cne $red.last -or $green.packets.verified -ne $red.packets.verified -or (($green.packets.lots -join ',') -cne ($red.packets.lots -join ','))) { throw 'TEST_TOTALS_OR_PACKET_SELECTION_CHANGED' }
    if (@($red.packets.failures).Count -ne 1 -or $red.packets.failures[0].lot -ne 'A-28' -or $red.packets.failures[0].control -ne 'PACKAGE_DRIFT' -or $red.summary -notmatch '; A-28 PACKAGE_DRIFT$') { throw 'ONE_BYTE_RED_NOT_NAMED' }
    $proof.checks += @{ check = 'real_green_A21_to_A28_and_A30_A20_excluded'; status = 'PASS' }
    $proof.checks += @{ check = 'one_changed_byte_named_PACKAGE_DRIFT'; status = 'PASS' }
    $proof.checks += @{ check = 'identical_REJEU_PASS_and_test_counts'; status = 'PASS' }
    $proof.checks += @{ check = 'both_owned_containers_absence_read_back'; status = 'PASS' }
    $proof.green = $green
    $proof.mutant = $red
} catch {
    $proof.checks += @{ check = 'native_gate'; status = 'FAIL' }
    # Keep the real error in the private scratch evidence, not a made-up receipt.
    [IO.File]::WriteAllText((Join-Path $out 'error.txt'), $_.Exception.ToString(), $utf8)
} finally {
    if (Test-Path -LiteralPath $copy) { Remove-Item -LiteralPath $copy -Recurse -Force }
    $proof.copy_absent = -not (Test-Path -LiteralPath $copy)
    $proof.original_receipt_unchanged = $originalHash -and ((Get-FileHash -LiteralPath (Join-Path $root $receipt) -Algorithm SHA256).Hash -eq $originalHash)
}
if ($proof.copy_absent -and $proof.original_receipt_unchanged -and $proof.checks.Count -eq 4 -and @($proof.checks | Where-Object { $_.status -ne 'PASS' }).Count -eq 0) { $proof.status = 'PASS' }
[IO.File]::WriteAllText((Join-Path $out 'result.json'), ($proof | ConvertTo-Json -Depth 20) + "`n", $utf8)
Write-Output ('T03 NATIVE : ' + $proof.status + ' ; disposable copy absent=' + $proof.copy_absent)
if ($proof.status -ne 'PASS') { exit 1 }
exit 0
