# Real offline Docker checks using a pre-existing PUBLIC synthetic PHP image.
# This is NOT the library suite and cannot produce PRET.
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object Text.UTF8Encoding($false)
. (Join-Path $PSScriptRoot 'commun.ps1')
$imageId = 'sha256:b2ffa6ad01ffacc6d31b176232c8d0779c0320daba381e05cbbd80f56d5327a0'
$name = 'imagine-t01-proof-' + [Guid]::NewGuid().ToString('N')
$owner = [Guid]::NewGuid().ToString('N')
$attempted = $false
$failed = $false
function Get-LibrarySnapshot {
    $rows = @(Get-ChildItem (Join-Path $script:T01Root 'wp/plugins') -File -Recurse | Sort-Object FullName | ForEach-Object { $_.FullName + '=' + (Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash })
    return ($rows -join "`n")
}
$before = Get-LibrarySnapshot
try {
    [void](Assert-T01Success (Invoke-T01Docker @('image', 'inspect', $imageId)) 'Public synthetic PHP image absent; no pull allowed.')
    $source = (@(& wsl.exe -d Ubuntu -- wslpath -a -u $script:T01Root.Replace('\', '/')) -join "`n").Trim()
    if ($LASTEXITCODE -ne 0) { throw 'WSL path conversion failed.' }
    $attempted = $true
    [void](Assert-T01Success (Invoke-T01Docker @('create', '--name', $name, '--label', ($script:T01Label + '=' + $owner), '--pull', 'never', '--network', 'none', '--read-only', '--mount', ('type=bind,source=' + $source + ',target=/repo,readonly'), '--tmpfs', '/tmp:rw,nosuid,nodev,size=512m,mode=1777', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--user', '65534:65534', '--pids-limit', '128', '--memory', '768m', '--cpus', '2', '--no-healthcheck', '--log-driver', 'none', '--entrypoint', 'sleep', $imageId, 'infinity')) 'Create failed.')
    [void](Assert-T01Success (Invoke-T01Docker @('start', $name)) 'Start failed.')
    $info = Get-T01Inspect $name
    Assert-T01Isolation $info $owner $imageId $source
    Write-Output ($info | ConvertTo-Json -Depth 12)
    foreach ($file in @('executer.php', 'verifier-image.php', 'probe-isolation.php')) {
        Write-Output (Assert-T01Success (Invoke-T01Docker @('exec', $name, 'php', '-l', ('/repo/wp/tests/t01/' + $file))) 'PHP syntax failed.')
    }
    Write-Output (Assert-T01Success (Invoke-T01Docker @('exec', $name, 'php', '/repo/wp/tests/t01/probe-isolation.php')) 'Real read-only/network test failed.')
    $worker = Invoke-T01Docker @('exec', $name, 'php', '/repo/wp/tests/t01/executer.php')
    Write-Output $worker.Text
    if ($worker.Code -ne 1 -or $worker.Text -notmatch 'Image dependencies stale or absent' -or $worker.Text -notmatch '"tests":0' -or $worker.Text -notmatch '"errors":1') { throw 'Real PHP worker did not refuse missing prepared dependencies.' }
    Assert-T01Isolation (Get-T01Inspect $name) $owner $imageId $source
    if ((Get-LibrarySnapshot) -ne $before) { throw 'Immutable custom libraries changed.' }
    Write-Output 'T01 LIBRARIES : complete file inventory and SHA256 unchanged'
    if (Test-Path (Join-Path $script:T01Root 'wp/tests/t01/.forbidden-write')) { throw 'Read-only canary left in repository.' }
} catch {
    $failed = $true
    Write-Output ('T01 REAL CHECK ERROR : ' + $_.Exception.Message)
} finally {
    if ($attempted) {
        try { Remove-T01Container $name $owner } catch { $failed = $true; Write-Output ('T01 CLEANUP ERROR : ' + $_.Exception.Message) }
    }
}
if ($failed) { Write-Output 'T01 REAL ISOLATION : FAIL'; exit 1 }
Write-Output 'T01 REAL ISOLATION : PASS (PHP library suite NOT executed; prepared image absent)'
exit 0
