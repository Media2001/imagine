# Mock only the external executable boundary, never PHPUnit evidence.
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = New-Object Text.UTF8Encoding($false)
$global:T01Mockcase = $env:T01_TEST_CASE
$global:T01Mockcreated = $false
$global:T01Mockremoved = $false
$global:T01Mockstarted = $false
$global:T01Mockowner = ''
$global:T01MockimageId = 'sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
function global:wsl.exe {
    $a = @($args)
    $global:LASTEXITCODE = 0
    # PowerShell consumes the -- separator when a function replaces an executable.
    if (($a[0..2] -join '|') -eq '-d|Ubuntu|wslpath') {
        if ($global:T01Mockcase -like 'prepare-*') { $global:T01Mockcontext = [string]$a[-1]; return '/fixture/build-context' }
        if ($global:T01Mockcase -eq 'unsafe-path') { return 'relative,path' }
        if (-not ([string]$a[-1]).EndsWith('/wp')) { throw 'Mount must expose wp only.' }
        return '/fixture/repository/wp'
    }
    if (($a[0..2] -join '|') -ne '-d|Ubuntu|docker') { throw ('Unexpected executable boundary: ' + ($a | ConvertTo-Json -Compress)) }
    $d = @($a[3..($a.Count - 1)])
    switch ($d[0]) {
        'ps' { return '' }
        'info' {
            if ($global:T01Mockcase -eq 'missing-docker') { $global:LASTEXITCODE = 1; return 'Docker daemon unavailable (test double)' }
            return '27.0.0-test-double'
        }
        'image' {
            if ($global:T01Mockcase -eq 'missing-image') { $global:LASTEXITCODE = 1; return 'No such image (test double)' }
            $config = @{ Labels = @{ 'org.imagine.t01-image' = '1' }; Volumes = $null; ExposedPorts = $null }
            if ($global:T01Mockcase -eq 'unsafe-image') { $config.Volumes = @{ '/data' = @{} } }
            if ($global:T01Mockcase -eq 'unsafe-ports') { $config.ExposedPorts = @{ '80/tcp' = @{} } }
            if ($global:T01Mockcase -eq 'unsafe-label') { $config.Labels.'org.imagine.t01-image' = 'wrong' }
            return (ConvertTo-Json -Depth 10 -Compress -InputObject @(@{ Id = $global:T01MockimageId; Config = $config }))
        }
        'create' {
            if ($global:T01Mockcase -in @('argument', 'unsafe-path', 'unsafe-ports', 'unsafe-label')) { throw 'Unexpected container creation for refused input.' }
            foreach ($required in @('--pull', 'never', '--network', 'none', '--read-only', '--mount', '--tmpfs', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--user', '65534:65534', '--entrypoint', 'timeout', '600', 'php', '/repo/wp/tests/t01/executer.php')) {
                if ($d -notcontains $required) { throw ('Missing isolation option: ' + $required) }
            }
            $binding = $d[[Array]::IndexOf($d, '--mount') + 1]
            if ($binding -ne 'type=bind,source=/fixture/repository/wp,target=/repo/wp,readonly') { throw 'Unsafe mount.' }
            $label = $d[[Array]::IndexOf($d, '--label') + 1]
            $global:T01Mockowner = $label.Substring('org.imagine.t01='.Length)
            $global:T01Mockcreated = $true
            if ($global:T01Mockcase -eq 'create-error') { $global:LASTEXITCODE = 1; return 'Create failed after object creation (test double)' }
            return 'fixture-container-id'
        }
        'inspect' {
            if ($global:T01Mockremoved) { $global:LASTEXITCODE = 1; return 'Error: no such object: fixture (test double)' }
            if (-not $global:T01Mockcreated) { throw 'Inspected before creation.' }
            $mount = @{ Type = 'bind'; Source = '/fixture/repository/wp'; Destination = '/repo/wp'; RW = ($global:T01Mockcase -eq 'unsafe-mount') }
            $info = @{ Image = $global:T01MockimageId; Config = @{ Labels = @{ 'org.imagine.t01' = $global:T01Mockowner }; ExposedPorts = $null }; HostConfig = @{ NetworkMode = 'none'; ReadonlyRootfs = $true; Privileged = $false; PortBindings = $null; CapDrop = @('ALL'); SecurityOpt = @('no-new-privileges') }; Mounts = @($mount); NetworkSettings = @{ Networks = @{ none = @{} } }; State = @{ Running = $false; ExitCode = $(if ($global:T01Mockcase -eq 'fail') { 1 } else { 0 }) } }
            return (ConvertTo-Json -Depth 15 -Compress -InputObject @($info))
        }
        'start' {
            $global:T01Mockstarted = $true
            if ($global:T01Mockcase -eq 'start-error') { $global:LASTEXITCODE = 1; return 'Start failed (test double)' }
            if ($global:T01Mockcase -eq 'malformed') { return 'T01_RESULT {"tests":"unknown"}' }
            if ($global:T01Mockcase -eq 'fail') { $global:LASTEXITCODE = 1; return 'T01_RESULT {"tests":7,"assertions":19,"failures":2,"errors":1,"skipped":0,"pass":false}' }
            if ($global:T01Mockcase -eq 'skipped') { return 'T01_RESULT {"tests":7,"assertions":19,"failures":0,"errors":0,"skipped":1,"pass":true}' }
            if ($global:T01Mockcase -eq 'tool-fail') { $global:LASTEXITCODE = 1; return 'T01_RESULT {"tests":7,"assertions":19,"failures":0,"errors":0,"skipped":0,"tools":{"tools":2,"checks":5,"failures":1,"excluded":[]},"pass":false}' }
            if ($global:T01Mockcase -eq 'tool-forged-pass') { return 'T01_RESULT {"tests":7,"assertions":19,"failures":0,"errors":0,"skipped":0,"tools":{"tools":2,"checks":5,"failures":1,"excluded":[]},"pass":true}' }
            if ($global:T01Mockcase -eq 'tool-missing') { return 'T01_RESULT {"tests":7,"assertions":19,"failures":0,"errors":0,"skipped":0,"pass":true}' }
            if ($global:T01Mockcase -eq 'tool-invalid') { return 'T01_RESULT {"tests":7,"assertions":19,"failures":0,"errors":0,"skipped":0,"tools":{"tools":2,"checks":"unknown","failures":0,"excluded":[]},"pass":true}' }
            if ($global:T01Mockcase -eq 'tool-excluded') { return 'T01_RESULT {"tests":7,"assertions":19,"failures":0,"errors":0,"skipped":0,"tools":{"tools":2,"checks":5,"failures":0,"excluded":[{"lot":"a90","reason":"WordPress et base requis"}]},"pass":true}' }
            return 'T01_RESULT {"tests":7,"assertions":19,"failures":0,"errors":0,"skipped":0,"tools":{"tools":2,"checks":5,"failures":0,"excluded":[]},"pass":true}'
        }
        'rm' {
            if (-not $global:T01Mockcreated) { throw 'Removal without ownership.' }
            if ($global:T01Mockcase -eq 'cleanup-error') { $global:LASTEXITCODE = 1; return 'Docker cleanup unavailable (test double)' }
            $global:T01Mockremoved = $true
            return 'fixture removed (test double)'
        }
        'build' {
            if ($global:T01Mockcase -notlike 'prepare-*') { throw 'Build forbidden in replay.' }
            $paths = @(Get-ChildItem $global:T01Mockcontext -File -Recurse | ForEach-Object { $_.FullName.Substring($global:T01Mockcontext.Length + 1).Replace('\', '/') } | Sort-Object)
            $expected = @('Dockerfile', 'verifier-image.php')
            foreach ($kind in @('plugins', 'mu-plugins', 'themes')) {
                $directory = Join-Path $env:T01_TEST_ROOT ('wp/' + $kind)
                if (-not (Test-Path $directory)) { continue }
                foreach ($package in @(Get-ChildItem $directory -Directory)) {
                    if (-not (Test-Path (Join-Path $package.FullName 'phpunit.xml')) -and -not (Test-Path (Join-Path $package.FullName 'phpunit.xml.dist'))) { continue }
                    $key = if ($kind -eq 'plugins') { $package.Name } else { $kind + '--' + $package.Name }
                    $expected += 'packages/' + $key + '/composer.json'
                    $expected += 'packages/' + $key + '/composer.lock'
                }
            }
            $expected = @($expected | Sort-Object)
            if (($paths -join '|') -ne ($expected -join '|')) { throw ('Unexpected build context: ' + ($paths -join '|')) }
            if ($global:T01Mockcase -eq 'prepare-build-error') { $global:LASTEXITCODE = 1; return 'Build failure (test double)' }
            return 'Build success (test double; no real image was built)'
        }
        'run' {
            if ($global:T01Mockcase -notlike 'prepare-*' -or $d -notcontains 'none' -or $d -notcontains '--rm' -or $d -notcontains '/opt/t01/verifier-image.php') { throw 'Unexpected preparation probe.' }
            if ($global:T01Mockcase -eq 'prepare-probe-error') { $global:LASTEXITCODE = 1; return 'Image probe failure (test double)' }
            return 'Image probe success (test double)'
        }
        default { throw ('Forbidden Docker operation in replay: ' + ($d -join ' ')) }
    }
}
if ($global:T01Mockcase -like 'prepare-*') {
    & (Join-Path $env:T01_TEST_ROOT 'wp/tests/preparer-image.ps1')
    $code = $LASTEXITCODE
    if ($global:T01Mockcontext -and (Test-Path $global:T01Mockcontext)) { throw 'Preparation context leaked.' }
    Write-Output 'T01 PREP CONTEXT : removed (external Docker boundary mocked)'
    exit $code
}
if ($global:T01Mockcase -eq 'argument') { & (Join-Path $env:T01_TEST_ROOT 'wp/tests/rejouer.ps1') 'forbidden'; exit $LASTEXITCODE }
& (Join-Path $env:T01_TEST_ROOT 'wp/tests/rejouer.ps1')
exit $LASTEXITCODE
