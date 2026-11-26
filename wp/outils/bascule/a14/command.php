<?php

declare(strict_types=1);

namespace Imagine\Contacts;

ini_set('display_errors', '0');
ini_set('log_errors', '0');
set_error_handler(static function (int $severity): bool {
    if (error_reporting() & $severity) {
        throw new \RuntimeException('A14_RUNTIME_WARNING');
    }
    return true;
});
$level = ob_get_level();
ob_start();
try {
    require dirname(__DIR__) . '/a12/AuditLibrary.php';
    \Imagine\ContentInventory\AuditLibrary::load();
    require dirname(__DIR__) . '/a11/Runtime.php';
    require dirname(__DIR__) . '/a12/Command.php';
    require __DIR__ . '/Matcher.php';
    require __DIR__ . '/Accounts.php';
    $o = [];
    foreach (array_slice($argv, 1) as $arg) {
        if (!preg_match('/\A--(wp-path|output|audit)=(.+)\z/D', $arg, $m) || isset($o[$m[1]])) {
            throw new \RuntimeException('A14_USAGE');
        }
        $o[$m[1]] = $m[2];
    }
    if (count($o) !== 3 || PHP_SAPI !== 'cli') {
        throw new \RuntimeException('A14_USAGE');
    }
    $site = realpath($o['wp-path']);
    $parent = realpath(dirname($o['output']));
    $repository = dirname(__DIR__, 4);
    if (!is_file($repository . '/wp/outils/bascule/audit')) {
        $repository = dirname(__DIR__);
    }
    if (
        !$site || !$parent || !is_dir($site) || !preg_match('/\A[A-Za-z0-9_-]+\z/D', basename($o['output']))
        || !\Imagine\ContentInventory\Command::disjointOutput($parent, $site, $repository)
    ) {
        throw new \RuntimeException('A14_OUTPUT_UNSAFE');
    }
    $out = $parent . '/' . basename($o['output']);
    if (file_exists($out) || is_link($out)) {
        throw new \RuntimeException('A14_OUTPUT_EXISTS');
    }
    $audit = realpath($o['audit']);
    if (!$audit || is_link($o['audit']) || filesize($audit) > 16777216 || dirname(dirname($audit)) !== $parent) {
        throw new \RuntimeException('A14_AUDIT_GUARD');
    }
    $photo = json_decode(file_get_contents($audit), true, 64, JSON_THROW_ON_ERROR);
    if (($photo['schema'] ?? null) !== 'imagine-a02-audit-v1' || ($photo['read_only'] ?? null) !== true) {
        throw new \RuntimeException('A14_AUDIT_GUARD');
    }
    if (getenv('A14_CONFINED') !== '1' || function_exists('mail') || function_exists('exec')) {
        throw new \RuntimeException('A14_CONFINEMENT_REQUIRED');
    }
    $input = stream_get_contents(STDIN, 16777217);
    if (strlen($input) > 16777216) {
        throw new \RuntimeException('A14_INPUT_LIMIT');
    }
    $contacts = json_decode($input, true, 64, JSON_THROW_ON_ERROR);
    $native = Accounts::collect($site);
    if ($native['storage'] !== ($photo['sections']['commerce']['order_storage'] ?? null)) {
        throw new \RuntimeException('A14_AUDIT_STORAGE_MISMATCH');
    }
    $result = Matcher::build($contacts, $native['accounts']);
    $matched = $result['matched'];
    unset($result['matched']);
    $result = [
        'schema' => 'imagine-a14-v1', 'read_only' => true, 'storage' => $native['storage'],
        'audit_sha256' => hash_file('sha256', $audit),
    ] + $result;
    $summary = __("# Rapprochement — lecture seule\n\nAucune réinscription ; coopérateur et tarif inconnus.\n", 'imagine');
    $summary .= __("Les contacts sont comptés par ligne source, pas par personne distincte. ", 'imagine')
        . __("Le compteur technique duplicate_contact_lines indique les lignes concernées par un doublon ; ", 'imagine')
        . __("il ne donne pas, à lui seul, le nombre de personnes distinctes.\n\n", 'imagine');
    $labels = [
        'contacts_total' => __('Total des contacts', 'imagine'),
        'contacts_with_account' => __('Contacts avec compte', 'imagine'),
        'contacts_without_account' => __('Contacts sans compte', 'imagine'),
        'ambiguous_contact_lines' => __('Lignes ambiguës', 'imagine'),
        'accounts_without_contact' => __('Comptes sans contact', 'imagine'),
        'accounts_unmatchable' => __('Comptes injoignables', 'imagine'),
        'invalid_contact_lines' => __('Lignes avec adresse invalide', 'imagine'),
        'duplicate_contact_lines' => __('Lignes concernées par un doublon', 'imagine'),
        'unsubscribed_contacts' => __('Contacts désinscrits', 'imagine'),
        'blocked_contacts' => __('Contacts bloqués', 'imagine'),
    ];
    foreach ($result['counts'] as $name => $count) {
        $summary .= $labels[$name] . ' : ' . $count . "\n";
    }
    $csv = "ligne;abonnement_actif;statut;cooperateur;tarif\n";
    foreach ($matched as $row) {
        $csv .= $row['line'] . ';' . ($row['active_subscription'] ? 'oui' : 'non') . ';' . $row['status'] . ";;\n";
    }
    if (!mkdir($out, 0700)) {
        throw new \RuntimeException('A14_OUTPUT_CREATE');
    }
    $outputs = [
        'resume.json' => json_encode($result, JSON_PRETTY_PRINT | JSON_THROW_ON_ERROR) . "\n",
        'resume.md' => $summary, 'rapproches.csv' => $csv,
    ];
    foreach ($outputs as $name => $text) {
        $f = fopen($out . '/' . $name, 'xb');
        if (!$f || !chmod($out . '/' . $name, 0600) || fwrite($f, $text) !== strlen($text)) {
            throw new \RuntimeException('A14_OUTPUT_WRITE');
        }
        fclose($f);
    }
    while (ob_get_level() > $level) {
        ob_end_clean();
    }
    fwrite(STDOUT, "A14_OK\n");
    exit(0);
} catch (\Throwable $error) {
    while (ob_get_level() > $level) {
        ob_end_clean();
    }
    $code = preg_match('/\AA(?:14|12|11|02)_[A-Z_]+\z/D', $error->getMessage()) ? $error->getMessage() : 'A14_FAILED';
    $message = class_exists(\Imagine\PublicAddresses\Runtime::class)
        ? \Imagine\PublicAddresses\Runtime::refusalMessage($error, $code) : $code;
    fwrite(STDERR, $message . "\n");
    exit(1);
}
