"""Optional PSR-12 checker using only the existing T01 dependency image."""
import argparse
import json
import pathlib
import re
import sys
import uuid
sys.dont_write_bytecode = True
import run


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', required=True, type=pathlib.Path)
    ap.add_argument('--fix', action='store_true')
    args = ap.parse_args()
    out = args.output.resolve()
    if out == run.REPO or run.REPO in out.parents:
        raise SystemExit('A12 style evidence must be outside repository')
    out.mkdir(parents=True, exist_ok=False)
    name = 'imagine-a12-style-'+uuid.uuid4().hex[:12]
    b = run.b
    created = False
    initial = run.manifest(['wp/tests/a12', 'wp/outils/bascule/a12'])
    protected = run.manifest(run.PROTECTED)
    receipt = {'container': name, 'checks': [], 'exit_code': 1, 'sources': initial}
    def record(key, ok, detail=None):
        receipt['checks'].append({'check': key, 'status': 'PASS' if ok else 'FAIL', 'detail': detail})
    try:
        image = json.loads(b.call(['image', 'inspect', 'imagine-tests-t01:1']).stdout)[0]
        assert image['Config']['Labels'].get('org.imagine.t01-image') == '1'
        assert not image['Config'].get('Volumes') and not image['Config'].get('ExposedPorts')
        b.call(['create', '--name', name, '--label', b.LABEL+'='+name, '--network', 'none', '--no-healthcheck', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--pull', 'never', '--entrypoint', 'sleep', image['Id'], 'infinity'])
        created = True
        record('isolation_before', True, b.validate(json.loads(b.call(['inspect', name]).stdout)[0], name))
        b.call(['start', name])
        b.call(['exec', '-u', '0', name, 'mkdir', '/subject'])
        tool = json.loads(b.call(['exec', name, 'php', '-r', "echo json_encode(glob('/opt/t01/*/vendor/bin/phpcs'));"]).stdout)[0]
        owned = sorted((run.REPO/'wp/outils/bascule/a12').glob('*.php')) + sorted(run.HERE.glob('*.php')) + [run.REPO/'wp/outils/bascule/a12/inventorier-contenus']
        mapping = {}
        for index, p in enumerate(owned):
            target = '/subject/'+str(index)+'-'+p.name+('' if p.suffix == '.php' else '.php')
            b.call(['cp', b.local(p), name+':'+target])
            mapping[target] = p
        if args.fix:
            fixed = b.call(['exec', '-u', '0', name, 'php', tool[:-5]+'phpcbf', '--standard=PSR12', *mapping], check=False)
            (out/'phpcbf.log').write_text(fixed.stdout+fixed.stderr, encoding='utf8')
            receipt['phpcbf_exit'] = fixed.returncode
            for target, p in mapping.items():
                b.call(['cp', name+':'+target, b.local(p)])
        result = b.call(['exec', name, 'php', tool, '--standard=PSR12', '--report=json', *mapping], check=False)
        (out/'phpcs.json').write_text(result.stdout, encoding='utf8')
        (out/'phpcs-stderr.log').write_text(result.stderr, encoding='utf8')
        receipt['phpcs_exit'] = result.returncode
        receipt['totals'] = json.loads(result.stdout)['totals']
        record('phpcs_strict_exit', result.returncode == 0, receipt['totals'])
        record('isolation_after', True, b.validate(json.loads(b.call(['inspect', name]).stdout)[0], name))
    except Exception as exc:
        record('exception', False, {'class': type(exc).__name__, 'code': str(exc)[:150]})
    finally:
        if created:
            info = json.loads(b.call(['inspect', name]).stdout)[0]
            assert info['Name'] == '/'+name and info['Config']['Labels'].get(b.LABEL) == name
            b.call(['rm', '-f', name])
            missing = b.call(['inspect', name], check=False)
            record('cleanup', missing.returncode != 0 and re.search(r'no such (object|container)', missing.stderr, re.I) is not None)
        if not args.fix:
            record('owned_sources_stable', initial == run.manifest(['wp/tests/a12', 'wp/outils/bascule/a12']))
        record('immutable_dependencies_stable', protected == run.manifest(run.PROTECTED))
        receipt['exit_code'] = int(any(x['status'] != 'PASS' for x in receipt['checks']))
        (out/'style.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf8')
        print(json.dumps(receipt, indent=2))
    return receipt['exit_code']

if __name__ == '__main__':
    sys.exit(main())
