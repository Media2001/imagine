<?php

declare(strict_types=1);

use Imagine\Pilotage\Robots\Configuration;
use Imagine\Pilotage\Robots\Methode;
use Imagine\Pilotage\Robots\Robot;

// C-03 / §4.4 : configuration proposée, sans chargement réseau ni activation WordPress.
// Domaines et méthodes Google :
// https://developers.google.com/crawling/docs/crawlers-fetchers/verify-google-requests
// https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers
// Source officielle des plages des robots communs (ne pas prendre toutes les IP Google) :
// https://developers.google.com/static/crawling/ipranges/common-crawlers.json
// Bing : domaine et lien vers ses plages, à rafraîchir quotidiennement selon l'exploitant :
// https://www.bing.com/webmasters/help/how-to-verify-bingbot-3905dc26
// https://www.bing.com/toolbox/bingbot.json
// La méthode Plages nécessite un instantané contrôlé et une expiration fournis par l'appelant.
// Aucun préfixe réel/fictif n'est ici activé ; pas de repli automatique d'une méthode à l'autre.
return new Configuration(
    robots: [
        new Robot('google', ['Googlebot'], Methode::Dns, ['googlebot.com']),
        new Robot('bing', ['bingbot'], Methode::Dns, ['search.msn.com']),
    ],
    delaiDnsMs: 200,
    ttlPositif: 3600,
    ttlNegatif: 60,
);
