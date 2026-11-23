<?php

declare(strict_types=1);

/** Select the same root configuration that PHPUnit would select. */
function phpunitConfiguration(string $package): ?string
{
    foreach (['phpunit.xml', 'phpunit.xml.dist'] as $name) {
        if (is_link($package . '/' . $name)) {
            throw new RuntimeException('Symbolic PHPUnit configuration refused: ' . $package);
        }
        if (is_file($package . '/' . $name)) {
            return $name;
        }
    }
    return null;
}

/**
 * Repository-owned package boundaries are immediate directories in these three
 * code roots, not arbitrary PHPUnit fixtures elsewhere under wp/.
 *
 * packages: [{relative, kind, name, config, cacheKey}], warnings: [{relative, reason}]
 * plugins retain /opt/t01/{name}; other roots use /opt/t01/{kind}--{name}.
 * Disposable source layout remains /tmp/t01/{relative}, preserving siblings.
 * A config without Composer manifests is discovered, then refused by replay /
 * preparation rather than silently omitted. No manifests are executed here.
 */
function discoverT01Packages(string $wpRoot): array
{
    $wpRoot = rtrim($wpRoot, '/');
    if (!is_dir($wpRoot)) {
        throw new RuntimeException('Missing wp package root: ' . $wpRoot);
    }
    $packages = [];
    $warnings = [];
    $cacheKeys = [];
    foreach (['plugins', 'mu-plugins', 'themes'] as $kind) {
        $root = $wpRoot . '/' . $kind;
        if (is_link($root)) {
            throw new RuntimeException('Symbolic package root refused: ' . $kind);
        }
        if (!is_dir($root)) {
            continue;
        }
        foreach (new DirectoryIterator($root) as $item) {
            if ($item->isDot()) {
                continue;
            }
            $name = $item->getFilename();
            $relative = $kind . '/' . $name;
            if ($item->isLink()) {
                throw new RuntimeException('Symbolic custom package refused: ' . $relative);
            }
            if (!$item->isDir()) {
                if ($kind === 'mu-plugins' && str_ends_with($name, '.php')) {
                    $warnings[] = ['relative' => $relative, 'reason' => 'standalone custom extension without package PHPUnit configuration'];
                }
                continue;
            }
            if (!preg_match('/^[a-zA-Z0-9][a-zA-Z0-9._-]*$/D', $name)) {
                throw new RuntimeException('Unsupported custom package name: ' . $relative);
            }
            $config = phpunitConfiguration($item->getPathname());
            if ($config === null) {
                $warnings[] = ['relative' => $relative, 'reason' => 'custom package without PHPUnit tests (phpunit.xml or phpunit.xml.dist)'];
                continue;
            }
            $cacheKey = $kind === 'plugins' ? $name : $kind . '--' . $name;
            if (isset($cacheKeys[$cacheKey])) {
                throw new RuntimeException('Conflicting prepared cache key: ' . $cacheKey);
            }
            $cacheKeys[$cacheKey] = true;
            $packages[] = compact('relative', 'kind', 'name', 'config', 'cacheKey');
        }
    }
    usort($packages, static fn (array $a, array $b): int => strcmp($a['relative'], $b['relative']));
    usort($warnings, static fn (array $a, array $b): int => strcmp($a['relative'], $b['relative']));
    return compact('packages', 'warnings');
}

// Optional machine-readable discovery for preparer-image.ps1, offline in Docker.
if (realpath($_SERVER['SCRIPT_FILENAME'] ?? '') === __FILE__) {
    try {
        echo json_encode(discoverT01Packages($argv[1] ?? '/repo/wp'), JSON_THROW_ON_ERROR | JSON_UNESCAPED_SLASHES) . "\n";
    } catch (Throwable $error) {
        fwrite(STDERR, 'T01 DISCOVERY ERROR : ' . $error->getMessage() . "\n");
        exit(1);
    }
}
