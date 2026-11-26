<?php

declare(strict_types=1);

/** Immediate unit.php banks only; no native runner is executed by discovery. */
function discoverT01Tools(string $wpRoot): array
{
    $directory = rtrim($wpRoot, '/') . '/tests';
    if (is_link($directory)) {
        throw new RuntimeException('T02_TEST_ROOT_INVALID');
    }
    if (!is_dir($directory)) {
        return ['tools' => [], 'excluded' => []];
    }
    $tools = [];
    $excluded = [];
    foreach (new DirectoryIterator($directory) as $item) {
        if ($item->isDot()) {
            continue;
        }
        $path = $item->getPathname();
        if (is_link($path . '/unit.php')) {
            throw new RuntimeException('T02_UNIT_SYMLINK');
        }
        if (!is_file($path . '/unit.php')) {
            continue;
        }
        if ($item->isLink()) {
            throw new RuntimeException('T02_UNIT_SYMLINK');
        }
        $lot = $item->getFilename();
        if (!preg_match('/^[a-z0-9][a-z0-9-]*$/D', $lot)) {
            throw new RuntimeException('T02_UNIT_NAME_INVALID');
        }
        $exclusion = $path . '/unit.hors-rejeu';
        if (is_link($exclusion)) {
            throw new RuntimeException('T02_EXCLUSION_SYMLINK');
        }
        if (is_file($exclusion)) {
            $reason = trim(file_get_contents($exclusion));
            if ($reason === '' || strlen($reason) > 120 || preg_match('/[\r\n]/', $reason)) {
                throw new RuntimeException('T02_EXCLUSION_REASON_INVALID');
            }
            $excluded[] = compact('lot', 'reason');
            continue;
        }
        $tools[] = ['lot' => $lot, 'path' => $path . '/unit.php'];
    }
    usort($tools, static fn (array $a, array $b): int => strcmp($a['lot'], $b['lot']));
    usort($excluded, static fn (array $a, array $b): int => strcmp($a['lot'], $b['lot']));
    return compact('tools', 'excluded');
}

/** Relocate only literal legacy fixture roots, never assertions or source libraries. */
function relocateT01Unit(string $source, array $roots): string
{
    $code = '';
    foreach (token_get_all($source) as $token) {
        if (!is_array($token)) {
            $code .= $token;
            continue;
        }
        $text = $token[1];
        if ($token[0] === T_CONSTANT_ENCAPSED_STRING) {
            foreach ($roots as $from => $to) {
                $prefix = substr($text, 1, strlen($from));
                $next = $text[1 + strlen($from)] ?? '';
                if ($prefix === $from && ($next === '/' || $next === $text[0])) {
                    $text = $text[0] . $to . substr($text, 1 + strlen($from));
                    break;
                }
            }
        }
        $code .= $text;
    }
    return $code;
}

/** Fresh PHP subprocess and receipt for each unit; all writes stay under /tmp. */
function runT01Tools(string $wpRoot, string $workspace = '/tmp/t01-tools'): array
{
    $discovery = discoverT01Tools($wpRoot);
    $result = ['tools' => 0, 'checks' => 0, 'failures' => 0, 'excluded' => $discovery['excluded']];
    if (file_exists($workspace) || is_link($workspace) || !str_starts_with($workspace, '/tmp/')) {
        throw new RuntimeException('T02_WORKSPACE_NOT_FRESH');
    }
    mkdir($workspace . '/wp/tests', 0777, true);
    if ($discovery['tools'] !== []) {
        copyTree($wpRoot . '/outils/bascule', $workspace . '/wp/outils/bascule');
        // Legacy tools may require a pure library by its canonical sibling path.
        // These aliases only point at the already read-only repository mount.
        foreach (['plugins', 'mu-plugins', 'themes'] as $kind) {
            if (is_dir($wpRoot . '/' . $kind)) {
                symlink($wpRoot . '/' . $kind, $workspace . '/wp/' . $kind);
            }
        }
    }
    foreach ($discovery['tools'] as $tool) {
        $lot = $tool['lot'];
        $result['tools']++;
        $directory = $workspace . '/wp/tests/' . $lot;
        copyTree(dirname($tool['path']), $directory);
        $report = $workspace . '/reports/' . $lot;
        mkdir($report, 0777, true);
        file_put_contents($directory . '/unit.php', relocateT01Unit(file_get_contents($tool['path']), [
            '/subject' => $workspace . '/wp/outils/bascule',
            '/checkout' => $workspace,
            '/report' => $report,
            '/unit-origin-fixture' => $report . '/origin',
        ]));
        $stdout = $report . '/stdout.log';
        $stderr = $report . '/stderr.log';
        $process = proc_open(['timeout', '30', 'php', $directory . '/unit.php'], [
            0 => ['file', '/dev/null', 'r'], 1 => ['file', $stdout, 'w'], 2 => ['file', $stderr, 'w'],
        ], $pipes, $directory);
        $code = is_resource($process) ? proc_close($process) : -1;
        $failures = 0;
        $checks = 0;
        try {
            if (!is_file($report . '/unit.json')) {
                throw new RuntimeException('T02_UNIT_RECEIPT_MISSING');
            }
            $receipt = json_decode(file_get_contents($report . '/unit.json'), true, 512, JSON_THROW_ON_ERROR);
            if (isset($receipt['tests']) && is_array($receipt['tests'])) {
                foreach ($receipt['tests'] as $name => $ok) {
                    if (!is_string($name) || !is_bool($ok)) {
                        throw new RuntimeException('T02_UNIT_RECEIPT_INVALID');
                    }
                    $checks++;
                    $failures += (int) !$ok;
                }
            } elseif (isset($receipt['checks']) && is_array($receipt['checks'])) {
                foreach ($receipt['checks'] as $check) {
                    if (!is_array($check) || !is_string($check['check'] ?? null)
                        || !in_array($check['status'] ?? null, ['PASS', 'FAIL'], true)) {
                        throw new RuntimeException('T02_UNIT_RECEIPT_INVALID');
                    }
                    $checks++;
                    $failures += (int) ($check['status'] === 'FAIL');
                }
            } else {
                throw new RuntimeException('T02_UNIT_RECEIPT_INVALID');
            }
            if (array_key_exists('exit_code', $receipt) && $receipt['exit_code'] !== 0) {
                $failures = max(1, $failures);
            }
            if ($checks === 0) {
                throw new RuntimeException('T02_UNIT_RECEIPT_EMPTY');
            }
        } catch (Throwable) {
            $failures = max(1, $failures);
        }
        if ($code !== 0 || filesize($stderr) > 0) {
            $failures = max(1, $failures);
        }
        $result['checks'] += $checks;
        $result['failures'] += $failures;
        echo 'T01 TOOL : ' . $lot . ' ; ' . $checks . ' controls ; ' . $failures . ' failures ; exit=' . $code . "\n";
        if ($failures > 0) {
            echo file_get_contents($stdout), file_get_contents($stderr);
        }
    }
    return $result;
}
