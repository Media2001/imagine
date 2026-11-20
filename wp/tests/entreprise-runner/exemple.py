"""Execute the final C-02 README PHP example inside the disconnected owned runner."""
import datetime
import hashlib
import importlib.util
import json
import pathlib
import re
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('c02_runner', pathlib.Path(__file__).with_name('run.py'))
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
bench = runner.bench
name = json.loads(bench.STATE.read_text(encoding='utf-8'))['container']
assert not bench.info(name)['NetworkSettings']['Networks']
readme = (bench.PLUGIN / 'README.md').read_bytes()
assert bench.call(['exec', name, 'cat', '/work/README.md']).stdout == readme
section = readme.decode('utf-8').split('## C-02 —', 1)[1]
example = re.search(r'```php\n(.*?)```', section, re.S).group(1)
code = "<?php require '/work/vendor/autoload.php';\n" + example + """
echo json_encode(['valide' => $numero->estValide(), 'normalise' => $numero->normalise,
'affichage' => $numero->affichage(), 'denomination' => $denomination->denomination,
'recherche_disponible' => $denomination->estDisponible(), 'message' => $denomination->message()]);
"""
p = bench.call(['exec', '-i', name, 'php'], code.encode('utf-8'), check=False)
(bench.OUT / 'exemple.log').write_bytes(p.stdout + p.stderr)
assert p.returncode == 0 and not p.stderr
result = json.loads(p.stdout)
expected = '01234567' + f'{97 - int("01234567") % 97:02d}'
assert result == {'valide': True, 'normalise': expected,
                  'affichage': expected[:4] + '.' + expected[4:7] + '.' + expected[7:],
                  'denomination': None, 'recherche_disponible': False,
                  'message': 'La recherche de dénomination n’est pas disponible.'}
receipt = {'time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'exit_code': p.returncode, 'result': result, 'readme_sha256': hashlib.sha256(readme).hexdigest(),
           'runner_sha256': hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
           'network_disconnected': True, 'no_mounts': True, 'no_ports': True}
(bench.OUT / 'exemple.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(receipt, ensure_ascii=False, indent=2))
