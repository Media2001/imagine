"""C-07 correction evidence, reusing the lot-owned disposable PHP bench.

All PHP/Composer execution happens inside the owned, disconnected container.
Use IMAGINE_C07_PACKET to select a new immutable evidence packet.
"""
import datetime
import hashlib
import importlib.util
import io
import json
import pathlib
import sys
import tarfile
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('c07_correction_runner', HERE / 'run.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
b = runner.bench
ROOT = runner.ROOT
OUT = b.OUT


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(directory):
    return {p.relative_to(ROOT).as_posix(): digest(p)
            for p in sorted(directory.rglob('*')) if p.is_file() and 'vendor' not in p.parts}


def save(name, data):
    path = OUT / name
    assert not path.exists(), 'Never overwrite evidence: ' + str(path)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')


def owned():
    name = json.loads(b.STATE.read_text(encoding='utf-8'))['container']
    info = b.info(name)
    assert not info['NetworkSettings']['Networks'], 'Tests require disconnected networking'
    return name, info


def command(key, args, work='/work', junit=None):
    name, _ = owned()
    assert not (OUT / (key + '.json')).exists(), 'Immutable command receipt'
    if junit:
        b.call(['exec', name, 'rm', '-f', junit])
    result = b.call(['exec', '-w', work, '-e', 'COMPOSER_ROOT_VERSION=dev-main', name] + args, check=False)
    (OUT / (key + '.log')).write_bytes(result.stdout + result.stderr)
    receipt = {'time_utc': now(), 'command': args, 'workdir': work, 'exit_code': result.returncode}
    if junit:
        xml = b.call(['exec', name, 'cat', junit], check=False)
        if xml.returncode == 0:
            tree = ET.fromstring(xml.stdout)
            suite = tree.find('testsuite') if tree.tag == 'testsuites' else tree
            receipt['junit'] = dict(suite.attrib)
            (OUT / (key + '.xml')).write_bytes(xml.stdout)
    save(key + '.json', receipt)
    print(key, json.dumps(receipt, ensure_ascii=False))
    assert result.returncode == 0, result.stdout.decode(errors='replace') + result.stderr.decode(errors='replace')
    return result


def c05(stage):
    name, _ = owned()
    source = ROOT / 'wp/plugins/imagine-pilotage/tests/Echeancier/run.php'
    b.call(['exec', '-i', name, 'sh', '-c', 'cat > /work/tests/Echeancier/run.php'], source.read_bytes())
    result = command(stage, ['php', 'tests/Echeancier/run.php'])
    text = result.stdout.decode()
    report = json.loads(text.split('C05_JSON=', 1)[1])
    assert report['failed'] == 0
    save(stage + '-result.json', report)
    print('C05', report['tests'], report['assertions'], report['failed'])
    if stage == 'c05-after':
        before = json.loads((OUT / 'c05-before-result.json').read_text(encoding='utf-8'))
        assert before == report, 'Style correction changed C05 behavior'
        save('c05-style-equivalence.json', {'time_utc': now(), 'identical_complete_results': True,
                                           'tests': report['tests'], 'assertions': report['assertions']})


def strict():
    name, info = owned()
    # The standard bench run must copy the final source set before strict checks.
    full = json.loads((OUT / 'final.json').read_text(encoding='utf-8'))
    assert all(full[k] == 0 for k in ['exit_code', 'psr12_exit_code', 'syntax_exit_code', 'composer_validate_exit_code'])
    assert full['source_sha256'] == runner.payload()[1], 'Run final suite after all source edits'
    processes = b.call(['top', name, '-eo', 'pid,comm']).stdout.decode()
    assert [row.split()[-1] for row in processes.splitlines()[1:]] == ['sleep']
    save('container-inspection.json', {
        'time_utc': now(), 'container': name, 'image': info['Image'], 'label': b.LABEL,
        'labels': info['Config']['Labels'], 'mounts': info['Mounts'],
        'binds': info['HostConfig'].get('Binds'), 'ports': info['HostConfig'].get('PortBindings'),
        'exposed_ports': info['Config'].get('ExposedPorts'),
        'privileged': info['HostConfig']['Privileged'], 'cap_drop': info['HostConfig']['CapDrop'],
        'security_options': info['HostConfig']['SecurityOpt'],
        'networks': info['NetworkSettings']['Networks'], 'processes': processes,
    })
    command('envoi-strict', ['php', 'vendor/bin/phpunit', '--fail-on-warning', '--fail-on-risky',
                            '--fail-on-deprecation', '--testsuite', 'Envoi',
                            '--log-junit', '/tmp/c07-envoi-strict.xml'], junit='/tmp/c07-envoi-strict.xml')
    source = ROOT / 'wp/plugins/imagine-connecteur'
    before = json.loads((OUT / 'c04-before.json').read_text(encoding='utf-8'))
    current = inventory(source)
    assert before == current, 'C04 host inventory/hash drift'
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode='w') as archive:
        for rel in current:
            path = ROOT / rel
            data = path.read_bytes()
            item = tarfile.TarInfo(path.relative_to(source).as_posix())
            item.size = len(data)
            item.mode = 0o644
            archive.addfile(item, io.BytesIO(data))
    b.call(['exec', name, 'mkdir', '-p', '/c04'])
    b.call(['exec', '-i', name, 'tar', '-xf', '-', '-C', '/c04'], stream.getvalue())
    b.call(['exec', name, 'cp', '-a', '/work/vendor', '/c04/vendor'])
    command('c04-autoload', ['php', '/tmp/composer.phar', 'dump-autoload', '--no-scripts', '--no-plugins'], '/c04')
    code = b'''<?php
$files = [];
foreach (new RecursiveIteratorIterator(new RecursiveDirectoryIterator('/c04', FilesystemIterator::SKIP_DOTS)) as $file) {
    $relative = substr($file->getPathname(), 5);
    if ($file->isFile() && !str_starts_with($relative, 'vendor/')) {
        $files['wp/plugins/imagine-connecteur/' . $relative] = hash_file('sha256', $file->getPathname());
    }
}
echo json_encode($files);
'''
    copied = json.loads(b.call(['exec', '-i', name, 'php'], code).stdout)
    assert current == copied, 'C04 container complete inventory/hash drift'
    save('c04-integrity.json', {'time_utc': now(), 'host_unchanged': True, 'container_matches': True,
                               'file_count': len(current), 'before': before, 'after': current, 'container': copied})
    command('c04-strict', ['php', 'vendor/bin/phpunit', '--fail-on-warning', '--fail-on-risky',
                          '--fail-on-deprecation', '--log-junit', '/tmp/c04-strict.xml'],
            '/c04', '/tmp/c04-strict.xml')
    command('c04-lint', ['php', '/tmp/composer.phar', 'lint'], '/c04')
    command('psr12-owned', ['php', 'vendor/bin/phpcs', '--standard=PSR12', 'src/Envoi',
                           'tests/Envoi', 'tests/Echeancier/run.php'])
    sample = b'''<?php
require '/work/vendor/autoload.php';
spl_autoload_register(static function (string $class): void {
    $prefix = 'Imagine\\Connecteur\\';
    if (str_starts_with($class, $prefix)) {
        require_once '/work/connecteur/' . substr($class, strlen($prefix)) . '.php';
    }
});
use Imagine\Pilotage\Envoi\{Abonnement, Destinataire, Situation, ListeEnvoi, ExportCsv};
use Imagine\Pilotage\Numeros\{Numero, TypeNumero, Calendrier};
$zone = new DateTimeZone('Europe/Brussels');
$date = static fn (string $s): DateTimeImmutable => new DateTimeImmutable($s, $zone);
$numero = new Numero('171', TypeNumero::Regulier, $date('2027-01-05'), $date('2026-12-20'));
$personne = new Destinataire('horsligne-fictive', 'Camille Fictive', '1 rue Imaginaire', '', '00100', 'Ville Fictive', 'FR');
$situation = new Situation($date('2026-11-01'), $date('2026-11-01'), 'grace', false, ['171'], [$personne]);
$abo = new Abonnement('abo-fictif', 'offert', $date('2026-10-08'), [$situation]);
$liste = ListeEnvoi::etablir($numero, new Calendrier([$numero]), [$abo], $numero->cloture);
$bytes = ExportCsv::liste($liste);
if ($bytes !== ExportCsv::liste(ListeEnvoi::etablir($numero, new Calendrier([$numero]), [$abo], $numero->cloture))) {
    throw new LogicException('Rejeu divergent');
}
file_put_contents('/tmp/c07-sample.csv', $bytes);
echo json_encode(['copies' => count($liste->lignes), 'anomalies' => $liste->anomalies, 'replay_identical' => true]);
'''
    example = json.loads(b.call(['exec', '-i', name, 'php'], sample).stdout)
    data = b.call(['exec', name, 'cat', '/tmp/c07-sample.csv']).stdout
    assert example == {'copies': 1, 'anomalies': [], 'replay_identical': True}
    assert not (OUT / 'sample.csv').exists()
    (OUT / 'sample.csv').write_bytes(data)
    example['sha256'] = hashlib.sha256(data).hexdigest()
    save('sample.json', example)
    assert not b.info(name)['NetworkSettings']['Networks']


def close():
    name, _ = owned()
    b.call(['rm', '-f', name])
    result = b.call(['inspect', name], check=False)
    diagnostic = (result.stdout + result.stderr).decode(errors='replace')
    assert result.returncode != 0 and ('no such object' in diagnostic.lower() or 'no such container' in diagnostic.lower())
    save('cleanup.json', {'time_utc': now(), 'container': name, 'owned_runner_removed': True,
                          'inspect_exit_code': result.returncode, 'inspect_diagnostic': diagnostic})
    b.STATE.unlink()
    print('OWNED RUNNER REMOVED', name, diagnostic)


def seal():
    assert not b.STATE.exists(), 'Close owned runner before seal'
    full = json.loads((OUT / 'final.json').read_text(encoding='utf-8'))
    assert full['source_sha256'] == runner.payload()[1]
    protected = json.loads((OUT / 'protected-before.json').read_text(encoding='utf-8'))
    # Parent owns the lock lifecycle; it is checked here only while still delegated.
    assert all(digest(ROOT / p) == value for p, value in protected.items())
    c04 = json.loads((OUT / 'c04-before.json').read_text(encoding='utf-8'))
    assert c04 == inventory(ROOT / 'wp/plugins/imagine-connecteur')
    paths = list((ROOT / 'wp/tests/envoi-runner').glob('*.py'))
    paths += [ROOT / p for p in ['wp/tests/robots-runner/run.py', 'wp/tests/numeros-runner/run.py']]
    source = inventory(ROOT / 'wp/plugins/imagine-pilotage')
    source.update(c04)
    source.update({p.relative_to(ROOT).as_posix(): digest(p) for p in paths})
    save('source-seal.json', {'time_utc': now(), 'source_sha256': source,
                             'protected_unchanged': True, 'c04_complete_inventory_unchanged': True})
    evidence = {p.name: digest(p) for p in sorted(OUT.iterdir()) if p.is_file()
                and p.name not in ['handoff-verification.json']}
    save('evidence-seal.json', {'time_utc': now(), 'sha256': evidence})
    check()


def check():
    seal_data = json.loads((OUT / 'source-seal.json').read_text(encoding='utf-8'))
    assert all(digest(ROOT / p) == value for p, value in seal_data['source_sha256'].items()), 'Source drift'
    evidence = json.loads((OUT / 'evidence-seal.json').read_text(encoding='utf-8'))
    assert all(digest(OUT / p) == value for p, value in evidence['sha256'].items()), 'Evidence drift'
    cleanup = json.loads((OUT / 'cleanup.json').read_text(encoding='utf-8'))
    result = b.call(['inspect', cleanup['container']], check=False)
    diagnostic = (result.stdout + result.stderr).decode(errors='replace')
    assert result.returncode != 0 and ('no such object' in diagnostic.lower() or 'no such container' in diagnostic.lower())
    assert not b.STATE.exists()
    counts = {}
    for key in ['final', 'envoi-strict', 'c04-strict']:
        tree = ET.parse(OUT / (key + '.xml')).getroot()
        suite = tree.find('testsuite') if tree.tag == 'testsuites' else tree
        counts[key] = {k: int(suite.attrib[k]) for k in ['tests', 'assertions', 'failures', 'errors', 'skipped']}
        assert counts[key]['failures'] == counts[key]['errors'] == counts[key]['skipped'] == 0
        receipt = json.loads((OUT / (key + '.json')).read_text(encoding='utf-8'))
        assert receipt['exit_code'] == 0
    assert counts['envoi-strict']['tests'] > 36 and counts['c04-strict'] == {
        'tests': 37, 'assertions': 224, 'failures': 0, 'errors': 0, 'skipped': 0}
    result = {'time_utc': now(), 'source_hashes_verified': len(seal_data['source_sha256']),
              'evidence_hashes_verified': len(evidence['sha256']), 'counts': counts,
              'container_absent': cleanup['container'], 'runner_state_absent': True}
    if not (OUT / 'handoff-verification.json').exists():
        save('handoff-verification.json', result)
    print('VERIFIED', json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    action = sys.argv[1] if len(sys.argv) > 1 else 'check'
    if action in ['c05-before', 'c05-after']:
        c05(action)
    elif action == 'strict':
        strict()
    elif action == 'close':
        close()
    elif action == 'seal':
        seal()
    elif action == 'check':
        check()
    else:
        raise SystemExit('Expected c05-before, c05-after, strict, close, seal or check')
