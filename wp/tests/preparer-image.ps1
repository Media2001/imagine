# Ced-only, explicit online preparation. Replay never invokes this file.
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object Text.UTF8Encoding($false)
. (Join-Path $PSScriptRoot 't01/commun.ps1')
$context = $null
try {
    if ($args.Count) { throw 'Cette commande ne prend aucun argument.' }
    [void](Assert-T01Success (Invoke-T01Docker @('info', '--format', '{{.ServerVersion}}')) 'Docker indisponible : demarrer Docker dans WSL Ubuntu. Rien ne sera installe sur Windows.')
    $scratch = Join-Path $env:LOCALAPPDATA 'hermes/cache/scratch'
    if ($env:TMPDIR -and (Test-Path $env:TMPDIR)) { $scratch = $env:TMPDIR }
    $context = Join-Path $scratch ('t01-prepare-' + [Guid]::NewGuid().ToString('N'))
    [void](New-Item -ItemType Directory -Path $context -Force)
    Copy-Item (Join-Path $PSScriptRoot 't01/Dockerfile') (Join-Path $context 'Dockerfile')
    Copy-Item (Join-Path $PSScriptRoot 't01/verifier-image.php') (Join-Path $context 'verifier-image.php')
    $manifests = @(Get-ChildItem (Join-Path $script:T01Root 'wp/plugins') -Directory | Where-Object { Test-Path (Join-Path $_.FullName 'composer.json') })
    if ($manifests.Count -eq 0) { throw 'Aucune bibliotheque PHP trouvee.' }
    foreach ($package in $manifests) {
        $destination = Join-Path $context ('packages/' + $package.Name)
        [void](New-Item -ItemType Directory -Path $destination -Force)
        foreach ($file in @('composer.json', 'composer.lock')) {
            Copy-Item (Join-Path $package.FullName $file) (Join-Path $destination $file)
        }
    }
    # Only public dependency manifests enter the build context; no repository, site, config or credentials.
    $converted = @(& wsl.exe -d Ubuntu -- wslpath -a -u $context.Replace('\', '/') 2>&1)
    if ($LASTEXITCODE -ne 0) { throw 'Conversion du dossier temporaire impossible.' }
    $linux = ($converted -join "`n").Trim()
    Write-Output 'PREPARATION T01 : reseau utilise uniquement dans Docker pour les dependances publiques verrouillees ; aucun PHP ni paquet installe sur Windows.'
    $build = Invoke-T01Docker @('build', '--tag', $script:T01Image, '--file', ($linux + '/Dockerfile'), $linux)
    Write-Output $build.Text
    [void](Assert-T01Success $build 'Construction de l image T01 echouee.')
    $image = @((Assert-T01Success (Invoke-T01Docker @('image', 'inspect', $script:T01Image)) 'Image construite introuvable.') | ConvertFrom-Json)[0]
    if ($image.Config.Labels.'org.imagine.t01-image' -ne '1' -or $image.Config.Volumes -or $image.Config.ExposedPorts) { throw 'Image construite non conforme.' }
    $probe = Invoke-T01Docker @('run', '--rm', '--pull', 'never', '--network', 'none', '--read-only', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--user', '65534:65534', '--entrypoint', 'php', $image.Id, '/opt/t01/verifier-image.php')
    Write-Output (Assert-T01Success $probe 'Verification hors ligne de l image echouee.')
    Write-Output ('PREPARATION T01 : image verifiee ' + $image.Id + ' ; lancer .\wp\tests\rejouer.ps1')
} catch {
    Write-Output ('PREPARATION T01 EN ECHEC : ' + $_.Exception.Message)
    exit 1
} finally {
    if ($context -and (Test-Path $context)) { Remove-Item -LiteralPath $context -Recurse -Force }
}
exit 0
