$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'commun.ps1')
$scratch = Join-Path $env:LOCALAPPDATA ('hermes/cache/scratch/t01-discovery-' + [Guid]::NewGuid().ToString('N'))
try {
    foreach ($relative in @('plugins/a','mu-plugins/b','themes/c','themes/untested','tests/ignored')) {
        $dir = Join-Path $scratch $relative
        [void](New-Item -ItemType Directory $dir -Force)
        if ($relative -ne 'themes/untested') {
            $config = if ($relative -eq 'themes/c') { 'phpunit.xml.dist' } else { 'phpunit.xml' }
            [IO.File]::WriteAllText((Join-Path $dir $config), '<phpunit/>')
            foreach ($file in @('composer.json','composer.lock')) { [IO.File]::WriteAllText((Join-Path $dir $file), '{}') }
        }
    }
    $packages = @(Get-T01Packages $scratch)
    if (($packages.CacheKey -join '|') -ne 'a|mu-plugins--b|themes--c') { throw 'Discovery did not cover exactly plugins, MU and themes.' }
    Remove-Item (Join-Path $scratch 'themes/c/composer.lock')
    $refused = $false
    try { Get-T01Packages $scratch | Out-Null } catch { $refused = $true }
    if (-not $refused) { throw 'Configured package without lock was silently omitted.' }
    Write-Output 'T01 PREPARATION DISCOVERY : 2/2 PASS; three roots, dist fallback, fixtures excluded, missing lock refused.'
} finally { if (Test-Path $scratch) { Remove-Item -LiteralPath $scratch -Recurse -Force } }
