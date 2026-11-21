"""Final C-07 checks, C-04 regressions and synthetic CSV; PHP stays in Docker."""
import hashlib
import importlib.util
import json
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('c07_runner', pathlib.Path(__file__).with_name('run.py'))
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
b = runner.bench
stage = sys.argv[1] if len(sys.argv) > 1 else 'final'
assert re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', stage), 'Unsafe verification name'
record = b.OUT / (stage + '-verification.json')
assert not record.exists(), 'Never overwrite completed verification evidence'
state = json.loads(b.STATE.read_text(encoding='utf-8'))
name = state['container']
assert not b.info(name)['NetworkSettings']['Networks']
bootstrap = b'''<?php
require '/work/vendor/autoload.php';
spl_autoload_register(static function (string $class): void {
    $prefix = 'Imagine\\\\Connecteur\\\\';
    if (str_starts_with($class, $prefix)) {
        $file = '/work/connecteur/' . substr($class, strlen($prefix)) . '.php';
        if (is_file($file)) { require_once $file; }
    }
});
'''
b.call(['exec', '-i', name, 'sh', '-c', 'cat > /work/c07-bootstrap.php'], bootstrap)
commands = {
    'envoi': ['php', 'vendor/bin/phpunit', '--bootstrap', 'c07-bootstrap.php', '--fail-on-warning',
              '--fail-on-risky', '--fail-on-deprecation', '--log-junit', '/work/c07-envoi.xml', 'tests/Envoi'],
    'connecteur': ['php', 'vendor/bin/phpunit', '--no-configuration', '--bootstrap', 'c07-bootstrap.php',
                  '--fail-on-warning', '--fail-on-risky', '--fail-on-deprecation',
                  '--log-junit', '/work/c07-connecteur.xml', 'connecteur-tests'],
    'psr12-owned': ['php', 'vendor/bin/phpcs', '--standard=PSR12', 'src/Envoi', 'tests/Envoi',
                    'connecteur/CsvProtection.php', 'connecteur/DailyCsvDestination.php'],
}
receipts = {}
for key, command in commands.items():
    p = b.call(['exec', '-w', '/work', name] + command, check=False)
    (b.OUT / (key + '-final.log')).write_bytes(p.stdout + p.stderr)
    receipts[key] = {'command': command, 'exit_code': p.returncode}
    print(key, p.returncode, p.stdout.decode(errors='replace'), p.stderr.decode(errors='replace'))
    if key in ('envoi', 'connecteur'):
        data = b.call(['exec', name, 'cat', '/work/c07-' + key + '.xml']).stdout
        (b.OUT / (key + '-final.xml')).write_bytes(data)
        suite = ET.fromstring(data).find('testsuite')
        receipts[key]['junit'] = dict(suite.attrib)

# Produce actual file bytes from the public API, then compare a replay.
sample = b'''<?php
require '/work/c07-bootstrap.php';
use Imagine\\Pilotage\\Envoi\\{Abonnement, Destinataire, Situation, ListeEnvoi, ExportCsv};
use Imagine\\Pilotage\\Numeros\\{Numero, TypeNumero, Calendrier};
$z = new DateTimeZone('Europe/Brussels');
$d = static fn(string $s): DateTimeImmutable => new DateTimeImmutable($s, $z);
$n = new Numero('171', TypeNumero::Regulier, $d('2027-01-05'), $d('2026-12-20'));
$p = new Destinataire('fictive-1', 'Camille Fictive', '1 rue Imaginaire', 'Boite Fiction', '1000', 'Ville Fictive', 'BE');
$s = new Situation($d('2026-11-01'), $d('2026-11-01'), 'actif', true, ['171'], [$p]);
$a = new Abonnement('abo-fictif', 'offert', $d('2026-10-01'), [$s]);
$l = ListeEnvoi::etablir($n, new Calendrier([$n]), [$a], $n->cloture);
$bytes = ExportCsv::liste($l);
if ($bytes !== ExportCsv::liste(ListeEnvoi::etablir($n, new Calendrier([$n]), [$a], $n->cloture))) {
    throw new LogicException('Rejeu divergent');
}
file_put_contents('/work/c07-exemple.csv', $bytes);
echo json_encode(['replay_identical' => true, 'copies' => count($l->lignes), 'anomalies' => $l->anomalies]);
'''
p = b.call(['exec', '-i', '-w', '/work', name, 'php'], sample)
receipts['example'] = json.loads(p.stdout)
data = b.call(['exec', name, 'cat', '/work/c07-exemple.csv']).stdout
example = b.OUT.parent / 'exemples/liste-171.csv'
example.parent.mkdir(parents=True, exist_ok=True)
example.write_bytes(data)
receipts['example']['sha256'] = hashlib.sha256(data).hexdigest()
receipts['example']['path'] = example.relative_to(ROOT).as_posix()
receipts['network_disconnected'] = not b.info(name)['NetworkSettings']['Networks']
receipts['sources'] = runner.payload()[1]
receipts['wrapper_sha256'] = hashlib.sha256(pathlib.Path(__file__).with_name('run.py').read_bytes()).hexdigest()
receipts['verifier_sha256'] = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
(b.OUT / 'final-verification.json').write_text(json.dumps(receipts, indent=2), encoding='utf-8')
assert all(item['exit_code'] == 0 for key, item in receipts.items() if key in commands)
print('FINAL CHECKS OK')
