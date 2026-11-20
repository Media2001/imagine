"""Run unmodified C-04 in a separate directory of the C-03 owned runner."""
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
bench.PLUGIN = ROOT / 'wp/plugins/imagine-connecteur'
tar, files = bench.payload()
bench.call(['exec', name, 'mkdir', '-p', '/regression-c04'])
bench.call(['exec', '-i', name, 'tar', '-xf', '-', '-C', '/regression-c04'], tar)
bench.call(['exec', name, 'cp', '-R', '/work/vendor', '/regression-c04/vendor'])
command = ['exec', '-w', '/regression-c04', '-e', 'COMPOSER_ROOT_VERSION=dev-main', name,
           'php', '/tmp/composer.phar']
dump = bench.call(command + ['dump-autoload', '--no-scripts', '--no-plugins'], check=False)
assert dump.returncode == 0, dump.stderr.decode(errors='replace')
probe = b'''<?php $files = []; foreach (new RecursiveIteratorIterator(new RecursiveDirectoryIterator('/regression-c04', FilesystemIterator::SKIP_DOTS)) as $f) { $rel = substr($f->getPathname(), strlen('/regression-c04/')); if ($f->isFile() && !str_starts_with($rel, 'vendor/')) { $files[$rel] = hash_file('sha256', $f->getPathname()); } } echo json_encode($files);'''
copied = json.loads(bench.call(['exec', '-i', name, 'php'], probe).stdout)
assert files == copied, 'C-04 source inventory/hash mismatch in isolated copy'
bench.call(['exec', name, 'rm', '-f', '/tmp/c03-c04.xml'])
p = bench.call(command + ['test', '--', '--log-junit', '/tmp/c03-c04.xml'], check=False)
lint = bench.call(command + ['lint'], check=False)
validate = bench.call(command + ['validate', '--strict', '--no-check-publish'], check=False)
syntax = bench.call(['exec', '-w', '/regression-c04', name, 'sh', '-c',
                     'find src tests examples -name "*.php" -print0 | xargs -0 -n 1 php -l'], check=False)
for suffix, result in [('.log', p), ('-lint.log', lint), ('-validate.log', validate), ('-syntax.log', syntax)]:
    (bench.OUT / ('c04-regression' + suffix)).write_bytes(result.stdout + result.stderr)
xml = bench.call(['exec', name, 'cat', '/tmp/c03-c04.xml'])
(bench.OUT / 'c04-regression.xml').write_bytes(xml.stdout)
receipt = {'time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'command': 'composer test', 'exit_code': p.returncode, 'psr12_exit_code': lint.returncode,
           'composer_validate_exit_code': validate.returncode, 'syntax_exit_code': syntax.returncode,
           'source_sha256': files, 'container_source_verified': True, 'network_disconnected': True,
           'no_mounts': True, 'no_ports': True,
           'runner_sha256': hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()}
(bench.OUT / 'c04-regression.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
print(p.stdout.decode(errors='replace') + p.stderr.decode(errors='replace'))
print(json.dumps({k: v for k, v in receipt.items() if k != 'source_sha256'}))
raise SystemExit(p.returncode or lint.returncode or validate.returncode or syntax.returncode)
