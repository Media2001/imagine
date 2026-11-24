"""PSR12 verification/formatting inside an exact-name owned offline runner."""
import argparse
import importlib.util
import json
import pathlib
import sys
import uuid

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('a03_run', ROOT / 'run.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
bench = runner.bench

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--fix', action='store_true')
    args = parser.parse_args()
    name = 'imagine-a03-style-' + uuid.uuid4().hex[:12]
    created = False
    result = {'exit_code': 1, 'cleanup': False}
    targets = [runner.REPO / 'wp/outils/bascule/non-regression', runner.REPO / 'wp/outils/bascule/comparer'] + list((runner.REPO / 'wp/outils/bascule/a03').glob('*.php')) + list((runner.REPO / 'wp/plugins/imagine-non-regression/src').glob('*.php'))
    tool = pathlib.Path('C:/Users/Ced/AppData/Local/hermes/cache/scratch/a02-phpcs.phar')
    # PHP_CodeSniffer 3.13.5, official release PHAR, exercised only in Docker.
    assert runner.hashlib.sha256(tool.read_bytes()).hexdigest() == '9ff3ddf1fcc6c9347a57bed63da10edfc6610e4339c6bee149e92537609c7939'
    output = pathlib.Path('C:/Users/Ced/AppData/Local/hermes/cache/scratch/imagine-a03-runs/style-final.json')
    try:
        bench.call(['create', '--name', name, '--label', runner.LABEL + '=' + name, '--network', 'none', '--no-healthcheck', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--pull', 'never', '--entrypoint', '/bin/sleep', bench.IMAGE, 'infinity'])
        created = True
        bench.validate(json.loads(bench.call(['inspect', name]).stdout)[0], name)
        bench.call(['start', name])
        bench.call(['exec', name, 'mkdir', '/subject'])
        bench.call(['cp', bench.local(tool), name + ':/phpcs.phar'])
        container_targets = []
        for path in targets:
            target = '/subject/' + str(path.relative_to(runner.REPO)).replace('\\', '--').replace('/', '--') + ('' if path.suffix == '.php' else '.php')
            container_targets.append(target)
            bench.call(['cp', bench.local(path), name + ':' + target])
        if args.fix:
            code = r"<?php require 'phar:///phpcs.phar/autoload.php'; $runner = new PHP_CodeSniffer\Runner(); exit($runner->runPHPCBF());"
            bench.call(['exec', '-i', name, 'tee', '/fix.php'], input_text=code)
            fixed = bench.call(['exec', name, 'php', '/fix.php', '--standard=PSR12'] + container_targets, check=False)
            print(fixed.stdout + fixed.stderr)
            for path, target in zip(targets, container_targets):
                bench.call(['cp', name + ':' + target, bench.local(path)])
        p = bench.call(['exec', name, 'php', '/phpcs.phar', '--standard=PSR12', '--report=json'] + container_targets, check=False)
        report = json.loads(p.stdout)
        result.update({'exit_code': p.returncode, 'totals': report['totals'], 'files': report['files']})
    finally:
        if created:
            info = json.loads(bench.call(['inspect', name]).stdout)[0]
            assert info['Name'] == '/' + name and info['Config']['Labels'].get(runner.LABEL) == name
            bench.call(['rm', '-f', name])
            missing = bench.call(['inspect', name], check=False)
            result['cleanup'] = missing.returncode != 0 and 'no such' in missing.stderr.lower()
        output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf8')
        print(json.dumps({'output': str(output), 'exit_code': result['exit_code'], 'totals': result.get('totals'), 'cleanup': result['cleanup']}))
    return result['exit_code']

if __name__ == '__main__':
    sys.exit(main())
