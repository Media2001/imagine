<?php

declare(strict_types=1);

namespace Imagine\StreamGuard;

/** Preserve the existing PHP command line; no site code runs in this process. */
function launch(string $tool, array $arguments): int
{
    $command = array_merge(['python3', __DIR__ . '/stream_guard.py', $tool], array_slice($arguments, 1));
    $process = proc_open($command, [0 => STDIN, 1 => STDOUT, 2 => STDERR], $pipes);
    if (!is_resource($process)) {
        fwrite(STDERR, $tool . "_EXECUTION_FAILED\n");
        return 1;
    }
    return proc_close($process) === 0 ? 0 : 1;
}
