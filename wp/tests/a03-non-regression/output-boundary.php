<?php

declare(strict_types=1);

namespace Imagine\NonRegression;

// Faults are confined to this separate test process, never loaded by the CLI.
function file_put_contents(string $path, string $data): int|false
{
    return match ($GLOBALS['a03_fault'] ?? '') {
        'write-failed' => false,
        'write-short' => strlen($data) - 1,
        default => \file_put_contents($path, $data),
    };
}

function chmod(string $path, int $mode): bool
{
    return ($GLOBALS['a03_fault'] ?? '') === 'chmod-failed' ? false : \chmod($path, $mode);
}

require '/subject/a03/Site.php';
$checks = [];
foreach (['write-failed', 'write-short', 'chmod-failed', 'success', 'mkdir-failed'] as $fault) {
    $GLOBALS['a03_fault'] = $fault;
    $target = '/report/output-' . $fault;
    try {
        if (!method_exists(Site::class, 'writeReport')) {
            throw new \LogicException('missing checked report writer');
        }
        if ($fault === 'mkdir-failed') {
            \mkdir($target);
        }
        Site::writeReport($target, ['fictitious' => true]);
        $checks[$fault] = $fault === 'success'
            && \file_get_contents($target . '/non-regression.json') === "{\n    \"fictitious\": true\n}\n"
            && (\fileperms($target . '/non-regression.json') & 0777) === 0600;
    } catch (\Throwable $error) {
        $checks[$fault] = $fault !== 'success' && $error->getMessage() === 'A03_OUTPUT_FAILED'
            && !is_file($target . '/non-regression.json');
    }
}
\file_put_contents('/report/output-boundary.json', json_encode($checks, JSON_PRETTY_PRINT) . "\n");
echo json_encode($checks) . "\n";
exit((int) in_array(false, $checks, true));
