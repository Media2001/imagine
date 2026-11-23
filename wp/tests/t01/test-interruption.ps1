# Hard-kill a real parent; recovery is guaranteed at the next sweep, not immediately.
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object Text.UTF8Encoding($false)
. (Join-Path $PSScriptRoot 'commun.ps1')
$name = 'imagine-t01-interrupted-' + [Guid]::NewGuid().ToString('N')
$owner = [Guid]::NewGuid().ToString('N')
$control = 'imagine-t01-unrelated-' + [Guid]::NewGuid().ToString('N')
$child = $null
$failed = $false
try {
    $image = @((Assert-T01Success (Invoke-T01Docker @('image','inspect',$script:T01Image)) 'Prepared image required.') | ConvertFrom-Json)[0]
    # This unrelated canary has only a distinct label; sweep must not remove it.
    [void](Assert-T01Success (Invoke-T01Docker @('create','--name',$control,'--label',('org.imagine.t01-control=' + $owner),'--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user','65534:65534','--entrypoint','sleep',$image.Id,'120')) 'Control create failed.')
    $code = ". '" + (Join-Path $PSScriptRoot 'commun.ps1') + "'; [void](Assert-T01Success (Invoke-T01Docker @('create','--name','$name','--label','org.imagine.t01=$owner','--pull','never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--user','65534:65534','--pids-limit','32','--memory','64m','--entrypoint','sleep','" + $image.Id + "','120')) 'Create failed.'); [void](Assert-T01Success (Invoke-T01Docker @('start','$name')) 'Start failed.'); Start-Sleep -Seconds 120"
    $encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($code))
    $child = Start-Process powershell.exe -ArgumentList @('-NoProfile','-EncodedCommand',$encoded) -PassThru -WindowStyle Hidden
    $running = $false
    for ($i=0; $i -lt 30; $i++) {
        Start-Sleep -Milliseconds 500
        $probe = Invoke-T01Docker @('inspect',$name)
        if ($probe.Code -eq 0) { $info = @($probe.Text | ConvertFrom-Json)[0]; if ($info.State.Running) { $running = $true; break } }
        if ($child.HasExited) { throw 'Parent exited before kill.' }
    }
    if (-not $running) { throw 'Interrupted fixture did not start.' }
    Stop-Process -Id $child.Id -Force
    $child.WaitForExit()
    Assert-T01Ownership (Get-T01Inspect $name) $owner
    Write-Output 'T01 INTERRUPTION : parent force-killed; owned orphan exists (expected before next run).'
    Remove-T01Orphans
    $missing = Invoke-T01Docker @('inspect',$name)
    if ($missing.Code -eq 0 -or $missing.Text -notmatch '(?i)no such (object|container)') { throw 'Orphan survived recovery.' }
    $kept = Get-T01Inspect $control
    if ($kept.Config.Labels.'org.imagine.t01-control' -ne $owner) { throw 'Unrelated canary missing.' }
    Write-Output 'T01 INTERRUPTION : PASS; orphan absent after next-run sweep; unrelated container preserved.'
} catch { $failed = $true; Write-Output ('T01 INTERRUPTION ERROR : ' + $_.Exception.Message) }
finally {
    if ($child -and -not $child.HasExited) { Stop-Process -Id $child.Id -Force }
    try { Remove-T01Container $name $owner } catch { $failed = $true; Write-Output $_ }
    $probe = Invoke-T01Docker @('inspect',$control)
    if ($probe.Code -eq 0) {
        $info = @($probe.Text | ConvertFrom-Json)[0]
        if ($info.Config.Labels.'org.imagine.t01-control' -ne $owner) { throw 'Control ownership mismatch.' }
        [void](Assert-T01Success (Invoke-T01Docker @('rm','-f',$control)) 'Control cleanup failed.')
        $missing = Invoke-T01Docker @('inspect',$control)
        if ($missing.Code -eq 0 -or $missing.Text -notmatch '(?i)no such (object|container)') { throw 'Control absence not verified.' }
    }
}
if ($failed) { exit 1 }; exit 0
