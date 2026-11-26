# T02 executable contracts; same isolation as the T01 correction bench.
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object Text.UTF8Encoding($false)
. (Join-Path $PSScriptRoot 'commun.ps1')
$name = 'imagine-t01-tools-' + [Guid]::NewGuid().ToString('N')
$owner = [Guid]::NewGuid().ToString('N')
$created = $false
$failed = $false
try {
    $image = @((Assert-T01Success (Invoke-T01Docker @('image','inspect',$script:T01Image)) 'Prepared image required.') | ConvertFrom-Json)[0]
    $source = (@(& wsl.exe -d Ubuntu -- wslpath -a -u (Join-Path $script:T01Root 'wp').Replace('\','/')) -join "`n").Trim()
    if ($LASTEXITCODE -ne 0) { throw 'WSL path failed.' }
    $created = $true
    [void](Assert-T01Success (Invoke-T01Docker @('create','--name',$name,'--label',($script:T01Label + '=' + $owner),'--pull','never','--network','none','--read-only','--mount',('type=bind,source=' + $source + ',target=/repo/wp,readonly'),'--tmpfs','/tmp:rw,nosuid,nodev,size=512m,mode=1777','--cap-drop','ALL','--security-opt','no-new-privileges','--user','65534:65534','--pids-limit','128','--memory','768m','--cpus','2','--no-healthcheck','--log-driver','none','--entrypoint','timeout',$image.Id,'600','php','/repo/wp/tests/t01/tools-contract.php')) 'Create failed.')
    Assert-T01Isolation (Get-T01Inspect $name) $owner $image.Id $source
    $run = Invoke-T01Docker @('start','-a',$name)
    Write-Output $run.Text
    [void](Assert-T01Success $run 'T02 contracts failed.')
    $after = Get-T01Inspect $name
    Assert-T01Isolation $after $owner $image.Id $source
    if ($after.State.Running -or $after.State.ExitCode -ne 0) { throw 'T02 contract state invalid.' }
} catch { $failed = $true; Write-Output ('T02 CONTRACT ERROR : ' + $_.Exception.Message) }
finally { if ($created) { try { Remove-T01Container $name $owner } catch { $failed = $true; Write-Output $_ } } }
if ($failed) { exit 1 }; exit 0
