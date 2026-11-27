# Shared T-01 Docker boundary. Windows PowerShell 5.1 compatible.
$script:T01Image = 'imagine-tests-t01:1'
$script:T01Root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$script:T01Label = 'org.imagine.t01'
function Get-T01Packages {
    param([string]$WpRoot)
    $keys = @{}
    foreach ($kind in @('plugins', 'mu-plugins', 'themes')) {
        $directory = Join-Path $WpRoot $kind
        if (-not (Test-Path -LiteralPath $directory)) { continue }
        foreach ($package in @(Get-ChildItem -LiteralPath $directory -Directory | Sort-Object Name)) {
            if ($package.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Symbolic package path refused.' }
            $config = 'phpunit.xml'
            if (-not (Test-Path (Join-Path $package.FullName $config))) { $config = 'phpunit.xml.dist' }
            if (-not (Test-Path (Join-Path $package.FullName $config))) { Write-Warning ('T01 sans tests : ' + $kind + '/' + $package.Name); continue }
            foreach ($file in @('composer.json','composer.lock')) {
                if (-not (Test-Path (Join-Path $package.FullName $file) -PathType Leaf)) { throw ('Configured library missing ' + $file + ': ' + $kind + '/' + $package.Name) }
            }
            $key = if ($kind -eq 'plugins') { $package.Name } else { $kind + '--' + $package.Name }
            if ($keys.ContainsKey($key)) { throw ('Duplicate cache key: ' + $key) }
            $keys[$key] = $true
            [pscustomobject]@{ FullName = $package.FullName; CacheKey = $key; Relative = $kind + '/' + $package.Name; Config = $config }
        }
        if ($kind -eq 'mu-plugins') { Get-ChildItem -LiteralPath $directory -File -Filter '*.php' | ForEach-Object { Write-Warning ('T01 standalone MU sans configuration : ' + $_.Name) } }
    }
}
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
function Remove-T01Orphans {
    # The per-lane host lock excludes a concurrent replay. Never touch other labels.
    $listed = Assert-T01Success (Invoke-T01Docker @('ps', '-aq', '--filter', ('label=' + $script:T01Label))) 'Inventaire des orphelins T01 impossible.'
    foreach ($id in @($listed -split "`n" | Where-Object { $_.Trim() })) {
        $id = $id.Trim()
        if ($id -notmatch '^[a-f0-9]{12,64}$') { throw 'Identifiant Docker orphelin invalide.' }
        $info = Get-T01Inspect $id
        $owner = [string]$info.Config.Labels.'org.imagine.t01'
        if ([string]::IsNullOrWhiteSpace($owner)) { throw 'Etiquette T01 absente : refus du balayage.' }
        Remove-T01Container $id $owner
    }
    Write-Output 'T01 ORPHANS : sweep complete (label org.imagine.t01 only).'
}
function Assert-T01Isolation {
    param($Info, [string]$Owner, [string]$ImageId, [string]$Source, [string]$PacketSource = '')
    Assert-T01Ownership $Info $Owner
    $h = $Info.HostConfig
    if ($Info.Image -ne $ImageId -or $h.NetworkMode -ne 'none' -or -not $h.ReadonlyRootfs -or $h.Privileged -or ($h.PortBindings -and @($h.PortBindings.PSObject.Properties).Count -gt 0) -or ($Info.Config.ExposedPorts -and @($Info.Config.ExposedPorts.PSObject.Properties).Count -gt 0) -or $h.CapDrop -notcontains 'ALL' -or $h.SecurityOpt -notcontains 'no-new-privileges') { throw ('Isolation du conteneur refusee : image=' + $Info.Image + '; expected=' + $ImageId + '; host=' + ($h | ConvertTo-Json -Compress -Depth 8)) }
    $expectedMounts = if ($PacketSource) { 2 } else { 1 }
    if (@($Info.Mounts).Count -ne $expectedMounts) { throw 'Nombre exact de montages en lecture seule requis.' }
    $wpMounts = @($Info.Mounts | Where-Object { $_.Destination -eq '/repo/wp' })
    if ($wpMounts.Count -ne 1) { throw 'Montage wp absent ou ambigu.' }
    $m = $wpMounts[0]
    if ($m.Type -ne 'bind' -or $m.Destination -ne '/repo/wp' -or $m.RW -or $m.Source -ne $Source) { throw 'Montage de wp non conforme (lecture seule obligatoire).' }
    if ($PacketSource) {
        $packetMounts = @($Info.Mounts | Where-Object { $_.Destination -eq '/packet-repo' })
        if ($packetMounts.Count -ne 1 -or ($PacketSource + '/wp') -cne $Source) { throw 'Montage paquet absent ou racine incoherente.' }
        $p = $packetMounts[0]
        if ($p.Type -ne 'bind' -or $p.RW -or $p.Source -cne $PacketSource) { throw 'Montage paquet non conforme (lecture seule obligatoire).' }
    }
    if ($Info.NetworkSettings.Networks -and @($Info.NetworkSettings.Networks.PSObject.Properties.Name | Where-Object { $_ -ne 'none' }).Count) { throw 'Reseau externe detecte.' }
    Write-Output ('T01 ISOLATION : network=none ; rootfs=ro ; mount=' + $m.Source + ':/repo/wp:ro ; ports=none ; cap-drop=ALL ; no-new-privileges')
}
