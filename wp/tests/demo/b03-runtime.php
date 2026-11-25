<?php

declare(strict_types=1);

namespace Imagine\Tests\B03;

$checks = [];
$function = 'Imagine\\Theme\\imagine_reading_minutes';
$checks['estimation_disponible'] = function_exists($function);
if ($checks['estimation_disponible']) {
    $checks['vide_minimum_une_minute'] = $function('') === 1;
    $checks['200_mots_une_minute'] = $function(str_repeat('lecture ', 200)) === 1;
    $checks['201_mots_deux_minutes'] = $function(str_repeat('lecture ', 201)) === 2;
    $checks['401_mots_trois_minutes'] = $function(str_repeat('lecture ', 401)) === 3;
    $checks['unicode_et_apostrophes'] = $function(str_repeat('l’été œuvre-à-lire ', 100)) === 1;
    $checks['entites_HTML_et_balises'] = $function(str_repeat('<p>&eacute;t&eacute;&nbsp;heureux</p> ', 100)) === 1;
    $checks['CTA_exclu_estimation'] = $function(str_repeat('lecture ', 200) . '<aside class="imagine-paywall-bloc" data-imagine-bloc="abonnement">' . str_repeat('abonnement ', 201) . '</aside>') === 1;
    $checks['scripts_non_comptes'] = $function('<script>' . str_repeat('secret ', 401) . '</script><p>Extrait</p>') === 1;
}
echo wp_json_encode(['total' => count($checks), 'failures' => array_keys(array_filter($checks, static fn($v) => !$v)), 'checks' => $checks]);
