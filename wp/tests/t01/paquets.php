<?php

declare(strict_types=1);

// Same container as PHPUnit. The packet channel cannot change the test totals.
try {
    $process = proc_open(
        ['timeout', '150', '/usr/bin/python3', '-B', __DIR__ . '/paquets.py'],
        [0 => ['file', '/dev/null', 'r'], 1 => ['pipe', 'w'], 2 => ['pipe', 'w']],
        $pipes,
        '/tmp'
    );
    if (!is_resource($process)) {
        throw new RuntimeException('PACKET_RUNNER');
    }
    $packetOutput = stream_get_contents($pipes[1]);
    $packetError = stream_get_contents($pipes[2]);
    fclose($pipes[1]);
    fclose($pipes[2]);
    $packetCode = proc_close($process);
    if ($packetCode !== 0 || $packetError !== '' || !is_string($packetOutput)
        || strlen($packetOutput) > 1048576 || !preg_match('/\AT03_PACKETS [^\r\n]+\r?\n\z/D', $packetOutput)) {
        throw new RuntimeException('PACKET_RUNNER');
    }
    echo $packetOutput;
} catch (Throwable $packetFailure) {
    echo 'T03_PACKETS {"verified":0,"lots":[],"failures":[{"lot":"T-03","control":"RUNNER_OUTPUT"}],"excluded":[]}' . "\n";
}
