"""A03 pure PHPUnit replay, offline, without changing the shared T01 bench."""
import argparse
import importlib.util
import hashlib
import json
import pathlib
import re
import sys
import uuid
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('a03_run', ROOT / 'run.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
bench = runner.bench


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--name', required=True)
    args = parser.parse_args()
    assert re.fullmatch('[A-Za-z0-9-]+', args.name)
    out = pathlib.Path(__import__('os').environ['LOCALAPPDATA']) / 'hermes/cache/scratch/imagine-a03-runs' / args.name
    out.mkdir(parents=True, exist_ok=False)
    package = runner.REPO / 'wp/plugins/imagine-non-regression'
    roots = [package, ROOT, runner.REPO / 'wp/outils/bascule/a03', ROOT.parent / 't01']
    def inventory():
        return {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for root in roots
                for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    before = inventory()
    name = 'imagine-a03-phpunit-' + uuid.uuid4().hex[:12]
    result = {'container': name, 'commands': {}, 'exit_code': 1, 'cleanup': False}
    created = False
    try:
        image = json.loads(bench.call(['image', 'inspect', 'imagine-tests-t01:1']).stdout)[0]
        assert image['Config']['Labels'].get('org.imagine.t01-image') == '1'
        assert not image['Config'].get('Volumes') and not image['Config'].get('ExposedPorts')
        bench.call(['create', '--name', name, '--label', runner.LABEL + '=' + name,
                    '--network', 'none', '--no-healthcheck', '--cap-drop', 'ALL',
                    '--security-opt', 'no-new-privileges', '--pids-limit', '128',
                    '--memory', '768m', '--cpus', '2', '--log-driver', 'none',
                    '--pull', 'never', '--user', '0:0', '--entrypoint', 'sleep', image['Id'], 'infinity'])
        created = True
        result['isolation'] = bench.validate(json.loads(bench.call(['inspect', name]).stdout)[0], name)
        bench.call(['start', name])
        bench.call(['exec', name, 'mkdir', '-p', '/fixture/wp/plugins', '/t01', '/report'])
        bench.call(['cp', bench.local(package), name + ':/fixture/wp/plugins/imagine-non-regression'])
        for file in ['discovery.php', 'executer.php']:
            bench.call(['cp', bench.local(ROOT.parent / 't01' / file), name + ':/t01/' + file])
        base = '/fixture/wp/plugins/imagine-non-regression'
        # Reuse only prepared dependency bytes, never another lot's sources/manifests.
        bench.call(['exec', name, 'cp', '-a', '/opt/t01/imagine-pilotage/vendor', base + '/vendor'])
        commands = {
            'discovery': ['php', '/t01/discovery.php', '/fixture/wp'],
            'validate': ['composer', 'validate', '--strict', '--no-check-publish'],
            'install': ['composer', 'install', '--no-scripts', '--no-plugins', '--no-interaction'],
            'coverage': ['php'],
            'phpunit': ['composer', 'test', '--', '--fail-on-skipped', '--fail-on-incomplete',
                        '--do-not-cache-result', '--log-junit', '/report/phpunit.xml'],
            'lint': ['composer', 'lint'],
        }
        coverage = "<?php define('T01_FUNCTIONS_ONLY', true); require '/t01/executer.php'; verifyCoverage('" + base + "');"
        for key, command in commands.items():
            p = bench.call(['exec', '-e', 'COMPOSER_DISABLE_NETWORK=1', '-e', 'COMPOSER_ROOT_VERSION=1.0.0']
                           + (['-i'] if key == 'coverage' else []) + ['-w', base, name] + command,
                           check=False, input_text=coverage if key == 'coverage' else None)
            result['commands'][key] = {'returncode': p.returncode, 'output': p.stdout + p.stderr}
            (out / (key + '.log')).write_text(p.stdout + p.stderr, encoding='utf8')
            print(key, p.returncode, p.stdout + p.stderr, flush=True)
            if key == 'discovery':
                packages = json.loads(p.stdout)['packages']
                assert len(packages) == 1 and packages[0]['relative'] == 'plugins/imagine-non-regression'
                result['discovered'] = packages[0]
            if key not in ('phpunit', 'lint') and p.returncode:
                raise RuntimeError('A03_PHPUNIT_' + key.upper())
        bench.call(['cp', name + ':/report/phpunit.xml', bench.local(out / 'phpunit.xml')])
        junit = ET.parse(out / 'phpunit.xml').getroot().find('testsuite')
        assert junit is not None and int(junit.attrib['tests']) > 0
        result['junit'] = {k: int(junit.attrib[k]) for k in ['tests', 'assertions', 'failures', 'errors', 'skipped']}
        cases = {case.attrib['name'] for case in junit.iter('testcase')}
        assert {'testMinimalReportsAreRefused', 'testDisappearingPageIsAnomalous',
                'testIncompleteBaselineIsRefusedEvenIfPageAppearsAfterwards',
                'testOnlyObservedAdminHookAndItsCounterAreExpectedAfterWooUpdate',
                'testSilentPhpDiagnosticIsAnomalousEvenWithHealthyHttpAndUnchangedCount',
                'testMissingLogIsNotAnEmptyLog', 'testRotationDuringProbeIsBlocking',
                'testPureClassesBelongToTheDiscoverablePackage'} <= cases
        result['isolation_after'] = bench.validate(json.loads(bench.call(['inspect', name]).stdout)[0], name)
        result['exit_code'] = int(any(item['returncode'] for item in result['commands'].values())
                                  or any(result['junit'][k] for k in ['failures', 'errors', 'skipped']))
    except Exception as error:
        result['error'] = {'class': type(error).__name__, 'code': str(error)[:200]}
    finally:
        if created:
            info = json.loads(bench.call(['inspect', name]).stdout)[0]
            assert info['Name'] == '/' + name and info['Config']['Labels'].get(runner.LABEL) == name
            bench.call(['rm', '-f', name])
            missing = bench.call(['inspect', name], check=False)
            result['cleanup'] = missing.returncode != 0 and re.search('no such (object|container)', missing.stderr, re.I) is not None
        result['sources_unchanged'] = before == inventory()
        if not result['cleanup'] or not result['sources_unchanged']:
            result['exit_code'] = 1
        (out / 'checks.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf8')
        print(json.dumps({'output': str(out), **result}, indent=2))
    return result['exit_code']


if __name__ == '__main__':
    sys.exit(main())
