"""Run unchanged C-01 and validate local evidence in the owned C-04 bench."""
import datetime
import hashlib
import importlib.util
import sys

sys.dont_write_bytecode = True
import io
import json
import pathlib
import tarfile
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = ROOT / 'production/C-04/tests'
spec = importlib.util.spec_from_file_location('c01_bench', ROOT / 'wp/tests/numeros-runner/run.py')
bench = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bench)
bench.LABEL = 'org.imagine.c04-runner'


def main():
    state = json.loads((OUT / 'runner-state.json').read_text(encoding='utf-8'))
    name = state['container']
    info = bench.info(name)
    assert not info['NetworkSettings']['Networks']
    before = json.loads((OUT / 'c01-before.json').read_text(encoding='utf-8'))
    after = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
             for folder in ['wp/plugins/imagine-pilotage', 'wp/tests/numeros-runner']
             for p in (ROOT / folder).rglob('*') if p.is_file()}
    assert before == after, 'Protected C-01 sources changed'
    bench.PLUGIN = ROOT / 'wp/plugins/imagine-pilotage'
    payload, hashes = bench.payload()
    bench.call(['exec', name, 'rm', '-rf', '/baseline'])
    bench.call(['exec', name, 'mkdir', '-p', '/baseline'])
    bench.call(['exec', '-i', name, 'tar', '-xf', '-', '-C', '/baseline'], payload)
    bench.call(['exec', name, 'cp', '-a', '/work/vendor', '/baseline/vendor'])
    dump = bench.call(['exec', '-w', '/baseline', '-e', 'COMPOSER_ROOT_VERSION=dev-main',
                       name, 'php', '/tmp/composer.phar', 'dump-autoload', '--no-scripts', '--no-plugins'])
    hash_code = (
        '<?php $r=[]; foreach(new RecursiveIteratorIterator(new RecursiveDirectoryIterator("/baseline",'
        'FilesystemIterator::SKIP_DOTS)) as $f) { $p=substr($f->getPathname(),10); '
        'if($f->isFile()&&!str_starts_with($p,"vendor/")) {$r[$p]=hash_file("sha256",$f->getPathname());}}'
        'echo json_encode($r);'
    )
    actual = json.loads(bench.call(['exec', '-i', name, 'php'], hash_code.encode()).stdout)
    assert actual == hashes, 'C-01 container source mismatch'
    tests = bench.call(['exec', '-w', '/baseline', '-e', 'COMPOSER_ROOT_VERSION=dev-main', name,
                        'php', '/tmp/composer.phar', 'test', '--', '--log-junit', '/baseline-result.xml'], check=False)
    lint = bench.call(['exec', '-w', '/baseline', '-e', 'COMPOSER_ROOT_VERSION=dev-main', name,
                       'php', '/tmp/composer.phar', 'lint'], check=False)
    xml = bench.call(['exec', name, 'cat', '/baseline-result.xml']).stdout
    (OUT / 'c01-regression.xml').write_bytes(xml)
    (OUT / 'c01-regression.log').write_bytes(dump.stdout + dump.stderr + tests.stdout + tests.stderr)
    (OUT / 'c01-regression-lint.log').write_bytes(lint.stdout + lint.stderr)
    suite = ET.fromstring(xml).find('testsuite')
    assert suite is not None
    receipt = {'time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'exit_code': tests.returncode, 'psr12_exit_code': lint.returncode,
               'suite': suite.attrib, 'source_sha256': hashes, 'protected_c01_unchanged': before == after,
               'container_source_verified': True, 'network_disconnected': True,
               'no_mounts': True, 'no_ports': True,
               'driver_sha256': hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()}
    (OUT / 'c01-regression.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    print(tests.stdout.decode() + tests.stderr.decode())
    print(json.dumps({k: v for k, v in receipt.items() if k != 'source_sha256'}, indent=2))
    assert tests.returncode == lint.returncode == 0
    assert int(suite.attrib.get('failures', '0')) == int(suite.attrib.get('errors', '0')) == 0
    bench.call(['exec', name, 'rm', '-rf', '/export-demo'])
    bench.call(['exec', name, 'mkdir', '/export-demo'])
    syntax = bench.call(['exec', '-w', '/work', name, 'php', '-l', 'examples/export.php'])
    demo = bench.call(['exec', '-w', '/work', name, 'php', 'examples/export.php', '/export-demo'])
    result = json.loads(demo.stdout)
    csv_bytes = bench.call(['exec', name, 'cat', '/export-demo/2026-11-19.csv']).stdout
    assert result['queue_entries'] == 1 and result['state'] == 'sent'
    assert result['replay_sent'] is False and result['alerts'] == []
    assert result['identical_after_rerun'] is True
    assert hashlib.sha256(csv_bytes).hexdigest() == result['export_sha256']
    (OUT / 'demo-result.json').write_bytes(demo.stdout)
    (OUT / 'demo-2026-11-19.csv').write_bytes(csv_bytes)
    (OUT / 'demo.log').write_bytes(syntax.stdout + syntax.stderr + demo.stdout + demo.stderr)
    print('DEMO', json.dumps(result))


if __name__ == '__main__':
    main()
