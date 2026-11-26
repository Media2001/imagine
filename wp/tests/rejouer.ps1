# Run from the repository root: .\wp\tests\rejouer.ps1
# No installation, pull, network, commercial bench or staging operation.
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object Text.UTF8Encoding($false)
. (Join-Path $PSScriptRoot 't01/commun.ps1')
$exitCode = 1
$created = $false
$name = 'imagine-t01-' + [Guid]::NewGuid().ToString('N')
$owner = [Guid]::NewGuid().ToString('N')
$result = @{ tests = 0; assertions = 0; failures = 0; errors = 0; skipped = 0 }
$toolResult = @{ tools = 0; checks = 0; failures = 0 }
$toolOutside = 'non evalue'
try {
    if ($args.Count) { throw 'Cette commande ne prend aucun argument.' }
    [void](Assert-T01Success (Invoke-T01Docker @('info', '--format', '{{.ServerVersion}}')) 'Docker indisponible : demarrer Docker dans WSL Ubuntu ; aucune installation automatique.')
    Remove-T01Orphans
    $imageProbe = Invoke-T01Docker @('image', 'inspect', $script:T01Image)
    if ($imageProbe.Code -ne 0) { throw ('Image T01 absente. Ced doit lancer .\wp\tests\preparer-image.ps1 une fois (reseau autorise uniquement pendant cette preparation), puis rejouer. Aucun telechargement effectue.' + "`n" + $imageProbe.Text) }
    $image = @($imageProbe.Text | ConvertFrom-Json)[0]
    if ($image.Config.Labels.'org.imagine.t01-image' -ne '1' -or $image.Config.Volumes -or $image.Config.ExposedPorts) { throw 'Image T01 non conforme : relancer preparer-image.ps1.' }
    # WSL path conversion is read-only and does not inspect any site.
    $wpRoot = (Join-Path $script:T01Root 'wp').Replace('\', '/')
    $sourceLines = @(& wsl.exe -d Ubuntu -- wslpath -a -u $wpRoot 2>&1)
    if ($LASTEXITCODE -ne 0) { throw ('Conversion du chemin WSL impossible : ' + ($sourceLines -join "`n")) }
    $source = ($sourceLines -join "`n").Trim()
    if (-not $source.StartsWith('/') -or $source.Contains(',') -or $source.Contains("`n")) { throw 'Chemin de montage WSL refuse.' }
    # Also check ownership/absence if Docker created the object but returned an error.
    $created = $true
    $create = Invoke-T01Docker @('create', '--name', $name, '--label', ($script:T01Label + '=' + $owner), '--pull', 'never', '--network', 'none', '--read-only', '--mount', ('type=bind,source=' + $source + ',target=/repo/wp,readonly'), '--tmpfs', '/tmp:rw,nosuid,nodev,size=512m,mode=1777', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--user', '65534:65534', '--pids-limit', '128', '--memory', '768m', '--cpus', '2', '--no-healthcheck', '--log-driver', 'none', '--entrypoint', 'timeout', $image.Id, '600', 'php', '/repo/wp/tests/t01/executer.php')
    [void](Assert-T01Success $create 'Creation du conteneur jetable impossible.')
    Assert-T01Isolation (Get-T01Inspect $name) $owner $image.Id $source
    Write-Output ('T01 IMAGE : ' + $image.Id)
    $run = Invoke-T01Docker @('start', '-a', $name)
    Write-Output $run.Text
    $after = Get-T01Inspect $name
    Assert-T01Isolation $after $owner $image.Id $source
    if ($after.State.Running) { throw 'Le conteneur ne s est pas arrete.' }
    $markers = @($run.Text -split "`n" | Where-Object { $_ -match '^T01_RESULT ' })
    if ($markers.Count -ne 1) { throw 'Bilan PHPUnit absent ou ambigu.' }
    $data = $markers[0].Substring(11) | ConvertFrom-Json
    foreach ($key in @('tests', 'assertions', 'failures', 'errors', 'skipped')) {
        $value = $data.$key
        if ($null -eq $value -or $value -notmatch '^\d+$' -or [long]$value -gt [int]::MaxValue) { throw 'Bilan PHPUnit invalide.' }
        $result[$key] = [int]$value
    }
    foreach ($key in @('tools', 'checks', 'failures')) {
        $value = $data.tools.$key
        if ($null -eq $value -or $value -notmatch '^\d+$' -or [long]$value -gt [int]::MaxValue) { throw 'Bilan des outils absent ou invalide.' }
        $toolResult[$key] = [int]$value
    }
    if ($null -eq $data.tools.excluded) { throw 'Liste des outils hors rejeu absente.' }
    $outside = @($data.tools.excluded | ForEach-Object {
        if ($_.lot -notmatch '^[a-z0-9][a-z0-9-]*$' -or [string]::IsNullOrWhiteSpace($_.reason) -or $_.reason.Length -gt 120 -or $_.reason -match '[\r\n]') { throw 'Liste des outils hors rejeu invalide.' }
        $_.lot + ' (' + $_.reason + ')'
    })
    $toolOutside = if ($outside.Count) { $outside -join ', ' } else { 'aucun' }
    if ($toolResult.failures -gt 0) { throw 'Tests purs des outils en echec : consulter la sortie complete ci-dessus.' }
    if ($run.Code -ne 0 -or $after.State.ExitCode -ne 0 -or $data.pass -ne $true -or $result.tests -eq 0 -or $result.failures -gt 0 -or $result.errors -gt 0 -or $result.skipped -gt 0) { throw 'Suite PHP en echec : consulter la sortie complete ci-dessus.' }
    $exitCode = 0
} catch {
    Write-Output ('T01 ERREUR : ' + $_.Exception.Message)
    if ($result.errors -eq 0 -and $result.failures -eq 0) { $result.errors = 1 }
} finally {
    if ($created) {
        try { Remove-T01Container $name $owner } catch { Write-Output ('T01 NETTOYAGE EN ECHEC : ' + $_.Exception.Message); $exitCode = 1; $result.errors = [Math]::Max(1, $result.errors) }
    }
}
$status = if ($exitCode -eq 0) { 'PASS' } else { 'FAIL' }
# Accents use codepoints to keep this entry point parseable under Windows PowerShell 5.1.
$e = [char]0x00e9; $dash = [char]0x2014
Write-Output ('OUTILS : {0} outils, {1} contr{4}les, {2} {5}checs ; hors rejeu : {3}' -f $toolResult.tools, $toolResult.checks, $toolResult.failures, $toolOutside, [char]0x00f4, $e)
Write-Output ('REJEU : {0} tests, {1} assertions, {2} {5}checs, {3} erreurs, {4} ignor{5}s {6} {7}' -f $result.tests, $result.assertions, $result.failures, $result.errors, $result.skipped, $e, $dash, $status)
exit $exitCode
