<?php

declare(strict_types=1);

$checks = [];
$check = static function (string $name, bool $ok) use (&$checks): void {
    $checks[] = ['check' => $name, 'status' => $ok ? 'PASS' : 'FAIL'];
};
$check('mapping_implementation_present', is_file('/subject/a16/Mapping.php'));
if (is_file('/subject/a16/Mapping.php')) {
    require '/subject/a16/Mapping.php';
    $mapping = ['version' => 1, 'numero_type' => 'a16_numero', 'article_type' => 'a16_article',
        'liaison' => ['source' => 'postmeta', 'cle' => '_a16_numero_id'],
        'thematique' => 'a16_theme', 'pdf_cle' => '_a16_pdf_id', 'date_cle' => 'post_date_gmt'];
    $check('explicit_operator_mapping_accepted', \Imagine\IssueInventory\Mapping::validate($mapping) === $mapping);
    $reordered = $mapping;
    $reordered['liaison'] = ['cle' => '_a16_numero_id', 'source' => 'postmeta'];
    try {
        $accepted = \Imagine\IssueInventory\Mapping::validate($reordered) === $reordered;
    } catch (RuntimeException $error) {
        $accepted = false;
    }
    $check('liaison_keys_order_independent', $accepted);
    foreach (['missing', 'extra'] as $variant) {
        $bad = $mapping;
        if ($variant === 'missing') {
            unset($bad['liaison']['cle']);
        } else {
            $bad['liaison']['extra'] = 'forbidden';
        }
        try {
            \Imagine\IssueInventory\Mapping::validate($bad);
            $refused = false;
        } catch (RuntimeException $error) {
            $refused = $error->getMessage() === 'A16_MAPPING_INVALID';
        }
        $check('liaison_exact_keys:' . $variant, $refused);
    }
    foreach (['version', 'thematique', 'liaison'] as $key) {
        $bad = $mapping;
        unset($bad[$key]);
        try {
            \Imagine\IssueInventory\Mapping::validate($bad);
            $refused = false;
        } catch (RuntimeException $error) {
            $refused = $error->getMessage() === 'A16_MAPPING_INVALID';
        }
        $check('missing_mapping_field:' . $key, $refused);
    }
    $privateMapping = $mapping;
    $privateMapping['racine_privee'] = '/scratch/a16-private';
    $accepted = \Imagine\IssueInventory\Mapping::validate($privateMapping) === $privateMapping;
    $check('optional_private_root_accepted', $accepted);
    $invalidRoots = [null, '', '/', 'relative', 'https://example.org/private', '/scratch/../private',
        '/scratch/private/', '/scratch//private', '/scratch/private' . "\n", 12, []];
    foreach ($invalidRoots as $index => $root) {
        $bad = $mapping;
        $bad['racine_privee'] = $root;
        try {
            \Imagine\IssueInventory\Mapping::validate($bad);
            $refused = false;
        } catch (RuntimeException $error) {
            $refused = $error->getMessage() === 'A16_MAPPING_INVALID';
        }
        $check('private_root_strict_local_syntax:' . $index, $refused);
    }
    $taxonomyMapping = $mapping;
    $taxonomyMapping['numero_source'] = 'taxonomy';
    try {
        $accepted = \Imagine\IssueInventory\Mapping::validate($taxonomyMapping) === $taxonomyMapping;
    } catch (RuntimeException $error) {
        $accepted = false;
    }
    $check('explicit_taxonomy_issue_source', $accepted);
    $bad = $mapping;
    $bad['liaison']['source'] = 'guess';
    try {
        \Imagine\IssueInventory\Mapping::validate($bad);
        $refused = false;
    } catch (RuntimeException $error) {
        $refused = $error->getMessage() === 'A16_MAPPING_INVALID';
    }
    $check('never_guess_links', $refused);
}
$command = file_get_contents('/subject/a16/Command.php');
$check('report_encoded_once_after_both_hashes', substr_count($command, 'json_encode($report,') === 1
    && strpos($command, "'mapping_sha256'") < strpos($command, 'json_encode($report,'));
$exit = in_array('FAIL', array_column($checks, 'status'), true) ? 1 : 0;
file_put_contents('/report/unit.json', json_encode(['exit_code' => $exit, 'checks' => $checks], JSON_PRETTY_PRINT));
exit($exit);
