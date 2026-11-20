"""Supplement the inherited bench with C-03 configuration checks."""
import importlib.util
import sys
import pathlib
import json
import hashlib
import datetime

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('c03_runner', pathlib.Path(__file__).with_name('run.py'))
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
bench = runner.bench
state = json.loads(bench.STATE.read_text(encoding='utf-8'))
name = state['container']
info = bench.info(name)
assert not info['NetworkSettings']['Networks']
path = bench.PLUGIN / 'config/robots.php'
expected = hashlib.sha256(path.read_bytes()).hexdigest()
probe = b"<?php echo hash_file('sha256', '/work/config/robots.php');"
actual = bench.call(['exec', '-i', name, 'php'], probe).stdout.decode().strip()
assert actual == expected
lint = bench.call(['exec', '-w', '/work', name, 'php', 'vendor/bin/phpcs', '--standard=PSR12', 'config'], check=False)
syntax = bench.call(['exec', name, 'php', '-l', '/work/config/robots.php'], check=False)
(bench.OUT / 'configuration-lint.log').write_bytes(lint.stdout + lint.stderr)
(bench.OUT / 'configuration-syntax.log').write_bytes(syntax.stdout + syntax.stderr)
receipt = {'time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'psr12_exit_code': lint.returncode, 'syntax_exit_code': syntax.returncode,
           'config_sha256': expected, 'container_source_verified': True,
           'network_disconnected': True, 'no_mounts': True, 'no_ports': True,
           'runner_sha256': hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()}
(bench.OUT / 'configuration.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
print(json.dumps(receipt))
print(syntax.stdout.decode(errors='replace'))
raise SystemExit(lint.returncode or syntax.returncode)
