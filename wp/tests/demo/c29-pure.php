<?php

declare(strict_types=1);

$base = __DIR__ . '/../../plugins/imagine-site/';
if (is_file($base . 'ContactBrevoRegles.php')) {
    require_once $base . 'ContactBrevoRegles.php';
}
if (!class_exists(\Imagine\Site\ContactBrevoRegles::class)) {
    fwrite(STDERR, "C29 calcul pur absent\n"); exit(1);
}
$input = ['existe' => true, 'email_recevable' => true, 'email' => 'fictif@example.org',
    'catalogue' => ['principale'], 'preferences' => ['principale' => ['choix' => true, 'origine' => 'lecteur']],
    'abonnements' => [['etat' => 'active', 'tarifs' => ['normal-1']]], 'beneficiaire' => false,
    'cooperateur' => false, 'tarifs_autorises' => ['normal-1'], 'personnalisation' => ['fictif' => ['choix' => ['a']]]];
$expected = ['fiche' => ['email' => 'fictif@example.org', 'statut' => 'abonne', 'cooperateur' => 'non',
    'tarif' => 'normal-1', 'newsletters' => ['principale'], 'personnalisation' => $input['personnalisation']], 'raison' => 'eligible'];
if (\Imagine\Site\ContactBrevoRegles::fiche($input) !== $expected) {
    fwrite(STDERR, "C29 fiche active incorrecte\n"); exit(1);
}
$checks = ['fiche_active' => true];
foreach (require $base . 'tests/fixtures/c29-cases.php' as $name => [$source, $want]) {
    $copy = $source;
    $actual = \Imagine\Site\ContactBrevoRegles::fiche($source);
    $checks[$name] = $actual === $want && $source === $copy;
    if (!$checks[$name]) { fwrite(STDERR, 'C29 ' . $name . ' expected ' . json_encode($want) . ' actual ' . json_encode($actual) . "\n"); }
}
echo json_encode(['checks' => $checks]), "\n";
exit(in_array(false, $checks, true) ? 1 : 0);
