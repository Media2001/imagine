# Real T03 process regressions; no image preparation or production test switch.
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object Text.UTF8Encoding($false)
. (Join-Path $PSScriptRoot '../../wp/tests/t01/commun.ps1')
$name = 'imagine-t01-t03-streams-' + [Guid]::NewGuid().ToString('N')
$owner = [Guid]::NewGuid().ToString('N')
$created = $false
$failed = $false
try {
    $image = @((Assert-T01Success (Invoke-T01Docker @('image','inspect',$script:T01Image)) 'Prepared image required.') | ConvertFrom-Json)[0]
    $source = (@(& wsl.exe -d Ubuntu -- wslpath -a -u (Join-Path $script:T01Root 'wp').Replace('\','/')) -join "`n").Trim()
    if ($LASTEXITCODE -ne 0) { throw 'WSL path failed.' }
    $packetSource = $source.Substring(0, $source.Length - 3)
    $created = $true
    [void](Assert-T01Success (Invoke-T01Docker @('create','--name',$name,'--label',($script:T01Label + '=' + $owner),'--pull','never','--network','none','--read-only','--mount',('type=bind,source=' + $source + ',target=/repo/wp,readonly'),'--mount',('type=bind,source=' + $packetSource + ',target=/packet-repo,readonly'),'--tmpfs','/tmp:rw,nosuid,nodev,size=512m,mode=1777','--cap-drop','ALL','--security-opt','no-new-privileges','--user','65534:65534','--pids-limit','128','--memory','768m','--cpus','2','--no-healthcheck','--log-driver','none','--entrypoint','timeout',$image.Id,'600','/usr/bin/python3','-B','/repo/wp/tests/t01/test_t03_streams_native.py')) 'Create failed.')
    Assert-T01Isolation (Get-T01Inspect $name) $owner $image.Id $source $packetSource
    $run = Invoke-T01Docker @('start','-a',$name)
    Write-Output $run.Text
    [void](Assert-T01Success $run 'T03 real stream regressions failed.')
    $after = Get-T01Inspect $name
    Assert-T01Isolation $after $owner $image.Id $source $packetSource
    if ($after.State.Running -or $after.State.ExitCode -ne 0) { throw 'T03 native state invalid.' }
} catch { $failed = $true; Write-Output ('T03 STREAM ERROR : ' + $_.Exception.Message) }
finally { if ($created) { try { Remove-T01Container $name $owner } catch { $failed = $true; Write-Output $_ } } }
if ($failed) { exit 1 }; exit 0
