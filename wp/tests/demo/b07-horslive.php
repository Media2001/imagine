<?php

declare(strict_types=1);

// Rejeu ciblé dans la même image, sans réseau, sans WordPress ni site.
define('T01_FUNCTIONS_ONLY', true);
require '/repo/wp/tests/t01/executer.php';
$discovery = discoverT01Packages('/repo/wp');
foreach ($discovery['packages'] as $package) {
    if ($package['relative'] !== 'plugins/imagine-site') { continue; }
    $source = '/repo/wp/' . $package['relative'];
    $dest = '/tmp/t01/' . $package['relative'];
    copyTree($source, $dest);
    copyTree('/opt/t01/' . $package['cacheKey'] . '/vendor', $dest . '/vendor');
    // Les gabarits et le filtre sont les vrais fichiers du thème.
    copyTree('/repo/wp/themes/imagine', '/tmp/t01/themes/imagine');
    // Mutations des SOURCES jetables, jamais des réponses en mémoire ni du site.
    $mutation = $argv[1] ?? '';
    $mutants = [
        'r1' => ['/tmp/t01/themes/imagine/functions.php', "get_post_meta(get_the_ID(), 'imagine_type', true) === 'partenaire'", 'false'],
        'r2' => [$dest . '/Agenda.php', "'description' => \$projection['description']", "'description' => \$e['description']"],
        'double-contenu' => ['/tmp/t01/themes/imagine/single-imagine_evenement.php', 'Agenda::schema($id, $projection)', 'Agenda::schema($id)'],
        'r4' => [$dest . '/AgendaConfidentialite.php', "return new \\WP_Error('imagine_agenda_export_lecture', __('Lecture des inscriptions impossible : réessayez cette page.', 'imagine-site'));", "return ['data' => [], 'done' => false];"],
        'formulaire' => ['/tmp/t01/themes/imagine/single-imagine_evenement.php', "echo \$projection['html'];", "echo \$projection['html'] . '<form id=\"imagine-agenda-inscription\"></form>';"],
        'alerte' => [$dest . '/Agenda.php', 'if (!self::dateSaisie((int)$post->ID)) {', 'if (false) {'],
    ];
    if ($mutation !== '') {
        if (!isset($mutants[$mutation])) { throw new RuntimeException('Mutation inconnue'); }
        [$path, $old, $new] = $mutants[$mutation];
        $raw = file_get_contents($path);
        if (substr_count($raw, $old) !== 1) { throw new RuntimeException('Cible mutation ambiguë'); }
        file_put_contents($path, str_replace($old, $new, $raw));
        echo 'B07 SOURCE MUTANT ' . $mutation . "\n";
    }
    verifyCoverage($dest);
    $cmd = ['php', 'vendor/bin/phpunit', '--configuration', 'phpunit.xml', '--filter', 'Agenda', '--do-not-cache-result', '--fail-on-warning', '--fail-on-risky', '--fail-on-deprecation', '--log-junit', '/tmp/agenda-junit.xml'];
    $proc = proc_open($cmd, [0 => ['file', '/dev/null', 'r'], 1 => STDOUT, 2 => STDERR], $pipes, $dest);
    $code = proc_close($proc);
    echo "B07 JUNIT BEGIN\n", file_get_contents('/tmp/agenda-junit.xml'), "B07 JUNIT END\n";
    exit($code);
}
throw new RuntimeException('Paquet imagine-site non découvert');
