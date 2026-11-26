<?php

declare(strict_types=1);

// This process only runs in the disposable, disconnected PHP container.
$totals = ['tests' => 0, 'assertions' => 0, 'failures' => 0, 'errors' => 0, 'skipped' => 0];
$pass = true;

function copyTree(string $from, string $to): void
{
    if (is_link($from)) {
        throw new RuntimeException('Symbolic links are not allowed: ' . $from);
    }
    if (is_dir($from)) {
        if (!is_dir($to) && !mkdir($to, 0777, true)) {
            throw new RuntimeException('Cannot create disposable directory: ' . $to);
        }
        foreach (new DirectoryIterator($from) as $item) {
            if (!$item->isDot()) {
                copyTree($item->getPathname(), $to . '/' . $item->getFilename());
            }
        }
    } elseif (!copy($from, $to)) {
        throw new RuntimeException('Cannot copy fixture: ' . $from);
    }
}

function testFiles(string $path): array
{
    $files = [];
    foreach (new RecursiveIteratorIterator(new RecursiveDirectoryIterator($path, FilesystemIterator::SKIP_DOTS)) as $item) {
        if ($item->isFile() && str_ends_with($item->getFilename(), 'Test.php')) {
            $files[] = $item->getRealPath();
        }
    }
    sort($files);
    return $files;
}

require_once __DIR__ . '/discovery.php';

function verifyCoverage(string $package): void
{
    $package = realpath($package) ?: throw new RuntimeException('Missing library: ' . $package);
    $filename = phpunitConfiguration($package);
    $document = new DOMDocument();
    $previous = libxml_use_internal_errors(true);
    try {
        $valid = $filename !== null && $document->load($package . '/' . $filename, LIBXML_NONET);
    } finally {
        libxml_clear_errors();
        libxml_use_internal_errors($previous);
    }
    $root = $document->documentElement;
    if (!$valid || $document->doctype !== null || $root === null || $root->tagName !== 'phpunit'
        || $root->getAttribute('bootstrap') !== 'vendor/autoload.php') {
        throw new RuntimeException('Unsupported PHPUnit configuration: ' . $package);
    }
    // Fail closed: only this fully understood, unfiltered selection grammar is accepted.
    // An ignored unknown node/attribute can otherwise make PHPUnit run a partial suite.
    $children = ['phpunit' => ['testsuites'], 'testsuites' => ['testsuite'], 'testsuite' => ['directory', 'file'], 'directory' => [], 'file' => []];
    $attributes = ['phpunit' => ['bootstrap', 'colors', 'cacheDirectory'], 'testsuites' => [], 'testsuite' => ['name'], 'directory' => ['suffix'], 'file' => []];
    foreach ($document->getElementsByTagName('*') as $element) {
        $name = $element->tagName;
        if ($element->namespaceURI !== null || !isset($children[$name])) {
            throw new RuntimeException('Unsupported PHPUnit selection element: ' . $name);
        }
        foreach ($element->attributes as $attribute) {
            // PHPUnit's standard schema declaration does not change test selection.
            if ($element === $root && $attribute->namespaceURI === 'http://www.w3.org/2001/XMLSchema-instance'
                && $attribute->localName === 'noNamespaceSchemaLocation') {
                continue;
            }
            if (!in_array($attribute->name, $attributes[$name], true)
                || ($name === 'directory' && $attribute->value !== 'Test.php')) {
                throw new RuntimeException('Unsupported PHPUnit selection attribute: ' . $name . '/@' . $attribute->name);
            }
        }
        foreach ($element->childNodes as $child) {
            if ($child instanceof DOMElement && !in_array($child->tagName, $children[$name], true)) {
                throw new RuntimeException('Unsupported PHPUnit selection element: ' . $child->tagName);
            }
        }
    }
    $config = simplexml_import_dom($root);
    $testsRoot = realpath($package . '/tests');
    if ($testsRoot === false || !is_dir($testsRoot) || $testsRoot !== $package . '/tests') {
        throw new RuntimeException('Missing or symbolic tests root: ' . $package);
    }
    $selected = [];
    foreach ($config->xpath('/phpunit/testsuites/testsuite/directory') as $directory) {
        $path = realpath($package . '/' . trim((string) $directory));
        if ($path === false || !is_dir($path) || ($path !== $testsRoot && !str_starts_with($path, $testsRoot . '/'))) {
            throw new RuntimeException('Test directory outside library: ' . $directory);
        }
        $selected = array_merge($selected, testFiles($path));
    }
    foreach ($config->xpath('/phpunit/testsuites/testsuite/file') as $file) {
        $path = realpath($package . '/' . trim((string) $file));
        if ($path === false || !is_file($path) || !str_starts_with($path, $testsRoot . '/') || !str_ends_with($path, 'Test.php')) {
            throw new RuntimeException('Test file outside library: ' . $file);
        }
        $selected[] = $path;
    }
    sort($selected);
    if ($selected !== testFiles($testsRoot) || $selected === []) {
        throw new RuntimeException('PHPUnit configuration does not cover every *Test.php exactly once: ' . $package);
    }
    echo 'T01 COVERAGE : ' . basename($package) . ' ; ' . count($selected) . " test files; full root configuration\n";
}

if (defined('T01_FUNCTIONS_ONLY') && T01_FUNCTIONS_ONLY === true) {
    return;
}

try {
    if (!extension_loaded('dom') || !extension_loaded('SimpleXML') || !extension_loaded('mbstring')) {
        throw new RuntimeException('Image T01 incomplete: DOM, SimpleXML and mbstring required; run preparer-image.ps1.');
    }
    $discovery = discoverT01Packages('/repo/wp');
    foreach ($discovery['warnings'] as $warning) {
        echo 'T01 WARNING : ' . $warning['relative'] . ' ; ' . $warning['reason'] . "\n";
    }
    if ($discovery['packages'] === []) {
        throw new RuntimeException('No custom library was discovered.');
    }
    $packages = [];
    foreach ($discovery['packages'] as $discovered) {
        $source = '/repo/wp/' . $discovered['relative'];
        $name = $discovered['relative'];
        $cache = '/opt/t01/' . $discovered['cacheKey'];
        $destination = '/tmp/t01/' . $discovered['relative'];
        foreach (['composer.json', 'composer.lock'] as $file) {
            if (!is_file($source . '/' . $file) || is_link($source . '/' . $file)) {
                throw new RuntimeException('Custom PHPUnit package requires ' . $name . '/' . $file . '; run preparer-image.ps1 after preparing its manifests.');
            }
            if (!is_file($cache . '/' . $file) || hash_file('sha256', $source . '/' . $file) !== hash_file('sha256', $cache . '/' . $file)) {
                throw new RuntimeException('Image dependencies stale or absent for ' . $name . '/' . $file . '; Ced must run preparer-image.ps1.');
            }
        }
        if (!is_file($cache . '/vendor/bin/phpunit')) {
            throw new RuntimeException('Prepared PHPUnit missing for ' . $name . '; run preparer-image.ps1.');
        }
        // Sibling-relative Composer mappings remain valid in this disposable topology.
        copyTree($source, $destination);
        if (is_dir($destination . '/vendor')) {
            throw new RuntimeException('Host vendor tree refused; dependencies must come from the prepared image.');
        }
        copyTree($cache . '/vendor', $destination . '/vendor');
        verifyCoverage($destination);
        $packages[] = $destination;
    }
    foreach ($packages as $index => $package) {
        echo "\nT01 LIBRARY : " . basename($package) . "\n";
        $junit = '/tmp/t01/junit-' . $index . '.xml';
        // Every run starts in a fresh container, so stale XML cannot be recycled.
        $command = ['php', 'vendor/bin/phpunit', '--configuration', phpunitConfiguration($package), '--fail-on-warning', '--fail-on-risky', '--fail-on-deprecation', '--fail-on-skipped', '--fail-on-incomplete', '--do-not-cache-result', '--colors=never', '--log-junit', $junit];
        echo 'T01 COMMAND : ' . implode(' ', $command) . "\n";
        $process = proc_open($command, [0 => ['file', '/dev/null', 'r'], 1 => STDOUT, 2 => STDERR], $pipes, $package);
        if (!is_resource($process)) {
            throw new RuntimeException('Could not launch PHPUnit.');
        }
        $code = proc_close($process);
        if (!is_file($junit)) {
            throw new RuntimeException('Fresh JUnit missing for ' . basename($package));
        }
        $document = simplexml_load_file($junit);
        $suite = $document->testsuite[0] ?? null;
        if ($suite === null) {
            throw new RuntimeException('Invalid JUnit for ' . basename($package));
        }
        foreach (array_keys($totals) as $key) {
            $value = (string) $suite[$key];
            if (!ctype_digit($value)) {
                throw new RuntimeException('Missing JUnit counter: ' . $key);
            }
            $totals[$key] += (int) $value;
        }
        // The complete XML is part of stdout, not an artifact written to the host.
        echo "T01 JUNIT BEGIN " . basename($package) . "\n";
        echo file_get_contents($junit);
        echo "T01 JUNIT END " . basename($package) . "\n";
        if ($code !== 0 || (int) $suite['tests'] === 0) {
            $pass = false;
        }
    }
} catch (Throwable $error) {
    echo 'T01 PHP ERROR : ' . $error->getMessage() . "\n";
    $totals['errors']++;
    $pass = false;
}
$toolTotals = ['tools' => 0, 'checks' => 0, 'failures' => 0, 'excluded' => []];
try {
    require_once __DIR__ . '/tools.php';
    $toolTotals = runT01Tools('/repo/wp', '/tmp/t01-tools');
} catch (Throwable $error) {
    echo 'T01 TOOL ERROR : ' . $error->getMessage() . "\n";
    $toolTotals['failures']++;
}
$pass = $pass && $totals['tests'] > 0 && $totals['failures'] === 0 && $totals['errors'] === 0 && $totals['skipped'] === 0 && $toolTotals['failures'] === 0;
echo 'T01_RESULT ' . json_encode($totals + ['tools' => $toolTotals, 'pass' => $pass], JSON_THROW_ON_ERROR) . "\n";
exit($pass ? 0 : 1);
