<?php

declare(strict_types=1);

// B04 : aucune écriture de données, vrais adaptateurs déjà chargés.
$checks = [];
$status = 'Imagine\\Theme\\imagine_access_status';
$checks['fonction_statut_disponible'] = function_exists($status);
if (function_exists($status)) {
    foreach ([
        'libre' => [['complet' => true, 'motif' => 'contenu_ouvert'], 'libre'],
        'decouverte_duree' => [['complet' => true, 'motif' => 'decouverte_duree'], 'decouverte'],
        'decouverte_articles' => [['complet' => true, 'motif' => 'decouverte_articles'], 'decouverte'],
        'achat' => [['complet' => true, 'motif' => 'numero_achete'], 'ouvert'],
        'abonnement' => [['complet' => true, 'motif' => 'abonnement_actif'], 'ouvert'],
        'ferme' => [['complet' => false, 'motif' => 'sans_droit'], 'reserve'],
        'decouverte_epuisee' => [['complet' => false, 'motif' => 'decouverte_epuisee'], 'reserve'],
        'libre_mais_ferme' => [['complet' => false, 'motif' => 'contenu_ouvert'], 'reserve'],
        'invalide' => [[], 'reserve'],
        'vrai_strict' => [['complet' => 'yes', 'motif' => 'contenu_ouvert'], 'reserve'],
    ] as $name => [$decision, $expected]) {
        $actual = $status($decision);
        $checks['statut:' . $name] = $actual['code'] === $expected && is_string($actual['label']) && $actual['label'] !== '';
    }
}
echo wp_json_encode(['total' => count($checks), 'checks' => $checks,
    'failures' => array_keys(array_filter($checks, static fn ($value): bool => $value !== true))]);
