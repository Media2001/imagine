# Shared T-01 Docker boundary. Windows PowerShell 5.1 compatible.
$script:T01Image = 'imagine-tests-t01:1'
$script:T01Root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$script:T01Label = 'org.imagine.t01'
function Invoke-T01Docker {
    param([string[]]$Arguments)
    $previous = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $text = @(& wsl.exe -d Ubuntu -- docker @Arguments 2>&1)
        $code = $LASTEXITCODE
        return [pscustomobject]@{ Code = $code; Text = (($text | ForEach-Object { $_.ToString() }) -join "`n") }
    } finally { $ErrorActionPreference = $previous }
}
function Assert-T01Success {
    param($Result, [string]$Message)
    if ($Result.Code -ne 0) { throw ($Message + "`n" + $Result.Text) }
    return $Result.Text
}
function Get-T01Inspect {
    param([string]$Name)
    $text = Assert-T01Success (Invoke-T01Docker @('inspect', $Name)) 'Inspection du conteneur impossible.'
    return @($text | ConvertFrom-Json)[0]
}
function Assert-T01Ownership {
    param($Info, [string]$Owner)
    if ($Info.Config.Labels.'org.imagine.t01' -ne $Owner) { throw 'Propriete du conteneur T01 non prouvee : refus de suppression.' }
}
function Remove-T01Container {
    param([string]$Name, [string]$Owner)
    $probe = Invoke-T01Docker @('inspect', $Name)
    if ($probe.Code -ne 0) {
        if ($probe.Text -match '(?i)no such (object|container)') { Write-Output ('T01 CLEANUP : absence verifiee de ' + $Name); return }
        throw ('Inspection avant nettoyage impossible : ' + $probe.Text)
    }
    $info = @($probe.Text | ConvertFrom-Json)[0]
    Assert-T01Ownership $info $Owner
    [void](Assert-T01Success (Invoke-T01Docker @('rm', '-f', $Name)) 'Suppression du conteneur impossible.')
    $missing = Invoke-T01Docker @('inspect', $Name)
    if ($missing.Code -eq 0 -or $missing.Text -notmatch '(?i)no such (object|container)') {
        throw ('Absence du conteneur non prouvee : ' + $missing.Text)
    }
    Write-Output ('T01 CLEANUP : absence verifiee de ' + $Name)
}
function Assert-T01Isolation {
    param($Info, [string]$Owner, [string]$ImageId, [string]$Source)
    Assert-T01Ownership $Info $Owner
    $h = $Info.HostConfig
    if ($Info.Image -ne $ImageId -or $h.NetworkMode -ne 'none' -or -not $h.ReadonlyRootfs -or $h.Privileged -or ($h.PortBindings -and @($h.PortBindings.PSObject.Properties).Count -gt 0) -or ($Info.Config.ExposedPorts -and @($Info.Config.ExposedPorts.PSObject.Properties).Count -gt 0) -or $h.CapDrop -notcontains 'ALL' -or $h.SecurityOpt -notcontains 'no-new-privileges') { throw ('Isolation du conteneur refusee : image=' + $Info.Image + '; expected=' + $ImageId + '; host=' + ($h | ConvertTo-Json -Compress -Depth 8)) }
    if (@($Info.Mounts).Count -ne 1) { throw 'Un seul montage du depot est permis.' }
    $m = @($Info.Mounts)[0]
    if ($m.Type -ne 'bind' -or $m.Destination -ne '/repo' -or $m.RW -or $m.Source -ne $Source) { throw 'Montage du depot non conforme (lecture seule obligatoire).' }
    if ($Info.NetworkSettings.Networks -and @($Info.NetworkSettings.Networks.PSObject.Properties.Name | Where-Object { $_ -ne 'none' }).Count) { throw 'Reseau externe detecte.' }
    Write-Output ('T01 ISOLATION : network=none ; rootfs=ro ; mount=' + $m.Source + ':/repo:ro ; ports=none ; cap-drop=ALL ; no-new-privileges')
}
