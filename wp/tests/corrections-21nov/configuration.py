"""Lint the configuration included in the corrected C-03 receipt."""
import importlib.util
import json
import pathlib
import sys
sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = ROOT / 'production/C-03/tests-21nov'
spec = importlib.util.spec_from_file_location('bench', ROOT / 'wp/tests/numeros-runner/run.py')
bench = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bench)
bench.LABEL = 'org.imagine.correction-c-03'
name = json.loads((OUT / 'runner-state.json').read_text())['container']
assert not bench.info(name)['NetworkSettings']['Networks']
commands = [['php', '-l', 'config/robots.php'], ['php', 'vendor/bin/phpcs', '--standard=PSR12', 'config']]
results = []
for command in commands:
    p = bench.call(['exec', '-w', '/work', name] + command, check=False)
    results.append({'command': command, 'exit': p.returncode, 'stdout': p.stdout.decode(), 'stderr': p.stderr.decode()})
(OUT / 'configuration-arbitrages.json').write_text(json.dumps(results, indent=2))
print(json.dumps(results, indent=2))
assert all(r['exit'] == 0 for r in results)
