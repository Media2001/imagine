"""Check the actual sibling C-02 loaded in the disposable C-04 container."""
import hashlib
import importlib.util
import json
import pathlib
import sys
sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = ROOT / 'production/C-04/tests-21nov'
spec = importlib.util.spec_from_file_location('bench', ROOT / 'wp/tests/numeros-runner/run.py')
bench = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bench)
bench.LABEL = 'org.imagine.correction-c-04'
name = json.loads((OUT / 'runner-state.json').read_text())['container']
info = bench.info(name)
assert not info['NetworkSettings']['Networks']
code = b'''<?php $out=[]; foreach(glob('/imagine-pilotage/src/Entreprise/*.php') as $p) { $out[basename($p)]=hash_file('sha256',$p); } echo json_encode($out);'''
copied = json.loads(bench.call(['exec', '-i', name, 'php'], code).stdout)
current = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
           for p in (ROOT / 'wp/plugins/imagine-pilotage/src/Entreprise').glob('*.php')}
assert copied == current == json.loads((OUT / 'dependency-source.json').read_text())
example = bench.call(['exec', '-w', '/work', name, 'php', 'examples/entreprise.php'])
assert json.loads(example.stdout) == {'violations': 0}
result = {'status': 'PASS', 'C02_container_sources_match_checkout': copied,
          'example_stdout': example.stdout.decode(), 'network_disconnected': True}
(OUT / 'composition.json').write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
