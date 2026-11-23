$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object Text.UTF8Encoding($false)
. (Join-Path $PSScriptRoot 'commun.ps1')
$name = 'imagine-t01-php-contract-' + [Guid]::NewGuid().ToString('N')
$owner = [Guid]::NewGuid().ToString('N')
$created = $false
$failed = $false
try {
    $image = @((Assert-T01Success (Invoke-T01Docker @('image','inspect',$script:T01Image)) 'Prepared image required.') | ConvertFrom-Json)[0]
    $source = (@(& wsl.exe -d Ubuntu -- wslpath -a -u (Join-Path $script:T01Root 'wp').Replace('\','/')) -join "`n").Trim()
    if ($LASTEXITCODE -ne 0) { throw 'WSL path failed.' }
    $created = $true
    [void](Assert-T01Success (Invoke-T01Docker @('create','--name',$name,'--label',($script:T01Label + '=' + $owner),'--pull','never','--network','none','--read-only','--mount',('type=bind,source=' + $source + ',target=/repo/wp,readonly'),'--tmpfs','/tmp:rw,nosuid,nodev,size=512m,mode=1777','--cap-drop','ALL','--security-opt','no-new-privileges','--user','65534:65534','--pids-limit','64','--memory','768m','--cpus','1','--no-healthcheck','--log-driver','none','--entrypoint','php',$image.Id,'/repo/wp/tests/t01/corrections-php.php')) 'Create failed.')
    Assert-T01Isolation (Get-T01Inspect $name) $owner $image.Id $source
    $run = Invoke-T01Docker @('start','-a',$name)
    Write-Output $run.Text
    [void](Assert-T01Success $run 'PHP correction regressions failed.')
    $after = Get-T01Inspect $name
    Assert-T01Isolation $after $owner $image.Id $source
    if ($after.State.Running -or $after.State.ExitCode -ne 0) { throw 'PHP regression state invalid.' }
} catch { $failed = $true; Write-Output ('T01 PHP CONTRACT ERROR : ' + $_.Exception.Message) }
finally { if ($created) { try { Remove-T01Container $name $owner } catch { $failed = $true; Write-Output $_ } } }
if ($failed) { exit 1 }; exit 0
