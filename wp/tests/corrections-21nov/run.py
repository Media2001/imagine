"""Disposable correction bench; historical receipts are never overwritten."""
import importlib.util
import pathlib
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('robots_bench', ROOT / 'wp/tests/robots-runner/run.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
lot, action, *extra = sys.argv[1:]
full = '--all' in extra
extra = [arg for arg in extra if arg != '--all']
assert lot in {'C-03', 'C-01', 'C-04', 'C-02', 'A-00'}
bench = module.bench
bench.OUT = ROOT / 'production' / lot / 'tests-21nov'
bench.STATE = bench.OUT / 'runner-state.json'
bench.LABEL = 'org.imagine.correction-' + lot.lower()
if lot == 'C-04':
    bench.PLUGIN = ROOT / 'wp/plugins/imagine-connecteur'
original_call = bench.call

def call(args, data=None, check=True):
    if lot == 'C-04' and action == 'prepare' and 'install' in args:
        import io
        import tarfile
        import hashlib
        import json
        name = json.loads(bench.STATE.read_text())['container']
        sources = ROOT / 'wp/plugins/imagine-pilotage/src/Entreprise'
        archive = io.BytesIO()
        manifest = {}
        with tarfile.open(fileobj=archive, mode='w') as tar:
            for path in sorted(sources.glob('*.php')):
                content = path.read_bytes()
                rel = path.name
                manifest[rel] = hashlib.sha256(content).hexdigest()
                info = tarfile.TarInfo(rel)
                info.size = len(content)
                tar.addfile(info, io.BytesIO(content))
        original_call(['exec', name, 'mkdir', '-p', '/imagine-pilotage/src/Entreprise'])
        original_call(['exec', '-i', name, 'tar', '-xf', '-', '-C', '/imagine-pilotage/src/Entreprise'], archive.getvalue())
        bench.OUT.joinpath('dependency-source.json').write_text(json.dumps(manifest, indent=2))
    if action == 'run' and lot == 'C-01' and not full and 'test' in args and '/tmp/composer.phar' in args:
        args += ['--testsuite', 'Numeros']
    return original_call(args, data, check)

bench.call = call
if action == 'prepare':
    module.prepare()
else:
    sys.argv = [sys.argv[0], action] + extra
    bench.main()
