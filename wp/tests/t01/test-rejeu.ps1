# T-01 contract tests. No PHP is executed on Windows.
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object Text.UTF8Encoding($false)
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$scriptFile = Join-Path $root 'wp/tests/rejouer.ps1'
if (-not (Test-Path $scriptFile)) { throw 'RED: wp/tests/rejouer.ps1 is missing' }
$tokens = $null; $parseErrors = $null
foreach ($file in @($scriptFile, (Join-Path $root 'wp/tests/preparer-image.ps1'), (Join-Path $PSScriptRoot 'commun.ps1'))) {
    [void][Management.Automation.Language.Parser]::ParseFile($file, [ref]$tokens, [ref]$parseErrors)
    if ($parseErrors.Count) { throw ($parseErrors | Out-String) }
}
# The child process executes the real scripts, with only the external WSL boundary mocked.
$cases = @('missing-docker', 'missing-image', 'pass', 'fail', 'malformed', 'start-error', 'create-error', 'cleanup-error', 'unsafe-image', 'unsafe-mount', 'argument', 'unsafe-path', 'unsafe-ports', 'unsafe-label', 'skipped')
foreach ($case in $cases) {
    $env:T01_TEST_CASE = $case
    $env:T01_TEST_ROOT = $root
    $out = @(& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'mock-wsl.ps1') 2>&1)
    $rc = $LASTEXITCODE
    $last = [string]$out[-1]
    if ($case -eq 'pass') {
        if ($rc -ne 0 -or $last -ne 'REJEU : 7 tests, 19 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS') { throw "$case : rc=$rc $($out -join "`n")" }
    } else {
        if ($rc -ne 1 -or $last -notmatch '^REJEU : [0-9]+ tests, [0-9]+ assertions, [0-9]+ échecs, [1-9][0-9]* erreurs, [0-9]+ ignorés — FAIL$') { throw "$case : rc=$rc $($out -join "`n")" }
    }
    if ($case -in @('pass', 'fail', 'malformed', 'start-error', 'create-error', 'unsafe-mount') -and ($out -join "`n") -notmatch 'T01 CLEANUP : absence verifiee') { throw "$case : cleanup was not verified" }
    if ($case -eq 'missing-image' -and ($out -join "`n") -notmatch 'preparer-image.ps1') { throw 'Missing image remediation was not printed.' }
    Write-Output "PASS boundary/$case : exit=$rc ; $last"
}
Remove-Item Env:T01_TEST_CASE, Env:T01_TEST_ROOT
$preparationCases = @('prepare-pass', 'prepare-build-error', 'prepare-probe-error')
foreach ($case in $preparationCases) {
    $env:T01_TEST_CASE = $case; $env:T01_TEST_ROOT = $root
    $out = @(& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'mock-wsl.ps1') 2>&1)
    $rc = $LASTEXITCODE
    $expected = if ($case -eq 'prepare-pass') { 0 } else { 1 }
    if ($rc -ne $expected -or ($out -join "`n") -notmatch 'T01 PREP CONTEXT : removed') { throw "$case : rc=$rc $($out -join "`n")" }
    Write-Output "PASS boundary/$case : exit=$rc ; minimal manifest-only context removed"
}
Remove-Item Env:T01_TEST_CASE, Env:T01_TEST_ROOT
$count = $cases.Count + $preparationCases.Count
Write-Output ('T01 CONTRACT : {0}/{0} PASS (external Docker boundary mocked; not a PHP-suite receipt)' -f $count)
