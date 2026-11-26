"""PARENT ONLY: PSR-12 of owned A29 PHP, offline disposable container."""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys
import uuid

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('a29_runner', HERE / 'run.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', required=True, type=Path)
    ap.add_argument('--fix', action='store_true')
    ap.add_argument('--parent-serialized', action='store_true', required=True)
    a = ap.parse_args()
    out = a.output.resolve()
    if out.is_relative_to(r.ROOT) or r.ROOT.is_relative_to(out):
        raise RuntimeError('A29_SCRATCH_REQUIRED')
    out.mkdir(parents=True, exist_ok=False)
    b = r.b
    name = 'imagine-a29-style-' + uuid.uuid4().hex[:10]
    created = False
    receipt = {'container': name, 'checks': [], 'exit_code': 1}
    before, deps = r.manifest(r.OWN), r.manifest(r.DEPS)

    def check(key, ok):
        receipt['checks'].append({'check': key, 'status': 'PASS' if ok else 'FAIL'})

    try:
        image = json.loads(b.call(['image', 'inspect', 'imagine-tests-t01:1']).stdout)[0]
        assert image['Config']['Labels'].get('org.imagine.t01-image') == '1'
        assert not image['Config'].get('Volumes') and not image['Config'].get('ExposedPorts')
        created = True  # Inspect ownership even if create reports an error.
        b.call(['create', '--name', name, '--label', b.LABEL + '=' + name, '--network', 'none',
                '--no-healthcheck', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges',
                '--pull', 'never', '--entrypoint', 'sleep', image['Id'], 'infinity'])
        b.validate(json.loads(b.call(['inspect', name]).stdout)[0], name)
        check('isolation_before', True)
        b.call(['start', name])
        b.call(['exec', '-u', '0', name, 'mkdir', '/subject'])
        tools = b.call(['exec', name, 'php', '-r', "echo json_encode(glob('/opt/t01/*/vendor/bin/phpcs'));"])
        tool = json.loads(tools.stdout)[0]
        files = sorted((r.ROOT / 'wp/outils/bascule/a29').glob('*.php')) + sorted(HERE.glob('*.php'))
        files.append(r.ROOT / 'wp/outils/bascule/a29/inventorier-taches')
        mapping = {}
        for i, p in enumerate(files):
            target = '/subject/' + str(i) + '-' + p.name + ('' if p.suffix == '.php' else '.php')
            b.call(['cp', b.local(p), name + ':' + target])
            mapping[target] = p
        if a.fix:
            fixed = b.call(['exec', '-u', '0', name, 'php', tool[:-5] + 'phpcbf', '--standard=PSR12', *mapping], check=False)
            (out / 'phpcbf.log').write_text(fixed.stdout + fixed.stderr, encoding='utf-8')
            for target, p in mapping.items():
                b.call(['cp', name + ':' + target, b.local(p)])
        result = b.call(['exec', name, 'php', tool, '--standard=PSR12', '--report=json', *mapping], check=False)
        (out / 'phpcs.json').write_text(result.stdout, encoding='utf-8')
        (out / 'stderr.log').write_text(result.stderr, encoding='utf-8')
        receipt['phpcs_exit'] = result.returncode
        receipt['totals'] = json.loads(result.stdout)['totals']
        check('strict_psr12', result.returncode == 0)
        b.validate(json.loads(b.call(['inspect', name]).stdout)[0], name)
        check('isolation_after', True)
    except Exception as error:
        check('exception_' + type(error).__name__, False)
    finally:
        if created:
            info = json.loads(b.call(['inspect', name]).stdout)[0]
            assert info['Name'] == '/' + name and info['Config']['Labels'].get(b.LABEL) == name
            b.call(['rm', '-f', name])
            p = b.call(['inspect', name], check=False)
            check('cleanup_exact_owned_container', p.returncode != 0 and re.search('no such (object|container)', p.stderr, re.I) is not None)
        if not a.fix:
            check('owned_sources_stable', before == r.manifest(r.OWN))
        check('dependencies_stable', deps == r.manifest(r.DEPS))
        receipt['sources'] = r.manifest(r.OWN)
        receipt['exit_code'] = int(any(c['status'] != 'PASS' for c in receipt['checks']))
        (out / 'style.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({k: v for k, v in receipt.items() if k != 'sources'}, indent=2))
    return receipt['exit_code']


if __name__ == '__main__':
    sys.exit(main())
