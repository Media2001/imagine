<?php

declare(strict_types=1);

namespace Imagine\StreamGuard;

// Registered before any site extension: freeze the completed files before its
// shutdown callbacks run. The supervisor checks these hashes after both EOFs.
$output = null;
foreach (array_slice($argv, 1) as $argument) {
    if (str_starts_with($argument, '--output=')) {
        $output = substr($argument, 9);
    }
}
register_shutdown_function(static function () use ($output): void {
    if (!is_string($output) || !is_dir($output) || is_link($output)) {
        return;
    }
    $files = scandir($output);
    if ($files === false) {
        return;
    }
    $hashes = [];
    foreach ($files as $file) {
        if ($file === '.' || $file === '..') {
            continue;
        }
        if (
            !in_array($file, [
                'non-regression.json', 'adresses.csv', 'adresses.json', 'resume.md',
                'contenus.json', 'contenus.md', 'resume.json', 'rapproches.csv',
                'emails.json', 'emails.md', 'numeros.json', 'numeros.md',
                'securite.json', 'securite.md', 'conservation.json', 'conservation.md',
                'coherence.json', 'coherence.md',
            ], true) || is_link($output . '/' . $file) || !is_file($output . '/' . $file)
        ) {
            return;
        }
        $hashes[$file] = hash_file('sha256', $output . '/' . $file);
    }
    fwrite(STDOUT, 'A22_FINAL ' . json_encode($hashes, JSON_THROW_ON_ERROR) . "\n");
});
