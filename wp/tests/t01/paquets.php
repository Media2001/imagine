<?php

declare(strict_types=1);

// Same container as PHPUnit. The packet channel cannot change the test totals.
$packetFailureControl = 'RUNNER_OUTPUT';
try {
    // Deadline established at PHP entry. Reserve publication plus TERM/KILL grace.
    $packetBudget = min(150.0, $t01Deadline - hrtime(true) / 1e9 - $t01PacketMargin - 1.0);
    if ($packetBudget <= 0.001) {
        $packetFailureControl = 'RUNNER_TIMEOUT';
        throw new RuntimeException('PACKET_DEADLINE');
    }
    $process = proc_open(
        ['timeout', '--kill-after=1s', sprintf('%.3fs', $packetBudget), '/usr/bin/python3', '-B', __DIR__ . '/paquets.py'],
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
    if (in_array($packetCode, [124, 137], true)) {
        $packetFailureControl = 'RUNNER_TIMEOUT';
    }
    if ($packetCode !== 0 || $packetError !== '' || !is_string($packetOutput)
        || strlen($packetOutput) > 1048576 || !preg_match('/\AT03_PACKETS [^\r\n]+\r?\n\z/D', $packetOutput)) {
        throw new RuntimeException('PACKET_RUNNER');
    }
    return json_decode(substr($packetOutput, 12), true, 512, JSON_THROW_ON_ERROR);
} catch (Throwable $packetFailure) {
    return ['verified' => 0, 'lots' => [], 'failures' => [['lot' => 'T-03', 'control' => $packetFailureControl]], 'excluded' => []];
}
