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
    if (($a[0..2] -join '|') -eq '-d|Ubuntu|wslpath') { return '/fixture/repository' }
    if (($a[0..2] -join '|') -ne '-d|Ubuntu|docker') { throw ('Unexpected executable boundary: ' + ($a | ConvertTo-Json -Compress)) }
    $d = @($a[3..($a.Count - 1)])
    switch ($d[0]) {
        'info' {
            if ($global:T01Mockcase -eq 'missing-docker') { $global:LASTEXITCODE = 1; return 'Docker daemon unavailable (test double)' }
            return '27.0.0-test-double'
        }
        'image' {
            if ($global:T01Mockcase -eq 'missing-image') { $global:LASTEXITCODE = 1; return 'No such image (test double)' }
            $config = @{ Labels = @{ 'org.imagine.t01-image' = '1' }; Volumes = $null; ExposedPorts = $null }
            if ($global:T01Mockcase -eq 'unsafe-image') { $config.Volumes = @{ '/data' = @{} } }
            return (ConvertTo-Json -Depth 10 -Compress -InputObject @(@{ Id = $global:T01MockimageId; Config = $config }))
        }
        'create' {
            foreach ($required in @('--pull', 'never', '--network', 'none', '--read-only', '--mount', '--tmpfs', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--user', '65534:65534', '--entrypoint', 'timeout', '600', 'php', '/repo/wp/tests/t01/executer.php')) {
                if ($d -notcontains $required) { throw ('Missing isolation option: ' + $required) }
            }
            $binding = $d[[Array]::IndexOf($d, '--mount') + 1]
            if ($binding -ne 'type=bind,source=/fixture/repository,target=/repo,readonly') { throw 'Unsafe mount.' }
            $label = $d[[Array]::IndexOf($d, '--label') + 1]
            $global:T01Mockowner = $label.Substring('org.imagine.t01='.Length)
            $global:T01Mockcreated = $true
            return 'fixture-container-id'
        }
        'inspect' {
            if ($global:T01Mockremoved) { $global:LASTEXITCODE = 1; return 'Error: no such object: fixture (test double)' }
            if (-not $global:T01Mockcreated) { throw 'Inspected before creation.' }
            $mount = @{ Type = 'bind'; Source = '/fixture/repository'; Destination = '/repo'; RW = ($global:T01Mockcase -eq 'unsafe-mount') }
            $info = @{ Image = $global:T01MockimageId; Config = @{ Labels = @{ 'org.imagine.t01' = $global:T01Mockowner }; ExposedPorts = $null }; HostConfig = @{ NetworkMode = 'none'; ReadonlyRootfs = $true; Privileged = $false; PortBindings = $null; CapDrop = @('ALL'); SecurityOpt = @('no-new-privileges') }; Mounts = @($mount); NetworkSettings = @{ Networks = @{ none = @{} } }; State = @{ Running = $false; ExitCode = $(if ($global:T01Mockcase -eq 'fail') { 1 } else { 0 }) } }
            return (ConvertTo-Json -Depth 15 -Compress -InputObject @($info))
        }
        'start' {
            $global:T01Mockstarted = $true
            if ($global:T01Mockcase -eq 'start-error') { $global:LASTEXITCODE = 1; return 'Start failed (test double)' }
            if ($global:T01Mockcase -eq 'malformed') { return 'T01_RESULT {"tests":"unknown"}' }
            if ($global:T01Mockcase -eq 'fail') { $global:LASTEXITCODE = 1; return 'T01_RESULT {"tests":7,"assertions":19,"failures":2,"errors":1,"skipped":0,"pass":false}' }
            return 'T01_RESULT {"tests":7,"assertions":19,"failures":0,"errors":0,"skipped":0,"pass":true}'
        }
        'rm' {
            if (-not $global:T01Mockcreated) { throw 'Removal without ownership.' }
            if ($global:T01Mockcase -eq 'cleanup-error') { $global:LASTEXITCODE = 1; return 'Docker cleanup unavailable (test double)' }
            $global:T01Mockremoved = $true
            return 'fixture removed (test double)'
        }
        default { throw ('Forbidden Docker operation in replay: ' + ($d -join ' ')) }
    }
}
& (Join-Path $env:T01_TEST_ROOT 'wp/tests/rejouer.ps1')
exit $LASTEXITCODE
