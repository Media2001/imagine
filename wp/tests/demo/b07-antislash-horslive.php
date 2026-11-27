<?php

declare(strict_types=1);

// Complément B07 seulement : copie jetable, dépôt et image en lecture seule.
define('T01_FUNCTIONS_ONLY', true);
require '/repo/wp/tests/t01/executer.php';
$dest = '/tmp/t01/plugins/imagine-site';
copyTree('/repo/wp/plugins/imagine-site', $dest);
copyTree('/opt/t01/imagine-site/vendor', $dest . '/vendor');
$mutation = $argv[1] ?? '';
if ($mutation !== '') {
    if ($mutation !== 'sans-echappement') {
        throw new RuntimeException('Mutation inconnue');
    }
    $path = $dest . '/Agenda.php';
    $source = file_get_contents($path);
    $old = "'imagine_agenda_nom' => wp_slash(\$nom)";
    if (substr_count($source, $old) !== 1) {
        throw new RuntimeException('Cible mutation absente ou ambiguë');
    }
    file_put_contents($path, str_replace($old, "'imagine_agenda_nom' => \$nom", $source));
    echo "B07 MUTATION SOURCE sans-echappement\n";
}
verifyCoverage($dest);
$cmd = ['php', 'vendor/bin/phpunit', '--configuration', 'phpunit.xml', '--filter', 'Agenda',
    '--do-not-cache-result', '--fail-on-warning', '--fail-on-risky', '--fail-on-deprecation',
    '--log-junit', '/tmp/b07-antislash-junit.xml'];
$process = proc_open($cmd, [0 => ['file', '/dev/null', 'r'], 1 => STDOUT, 2 => STDERR], $pipes, $dest);
$exit = proc_close($process);
echo "B07 JUNIT BEGIN\n", file_get_contents('/tmp/b07-antislash-junit.xml'), "B07 JUNIT END\n";
exit($exit);
