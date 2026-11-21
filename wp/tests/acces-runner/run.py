"""C-06 owned wrapper: PHP only inside a disposable WSL Docker runner."""
import hashlib
import importlib.util
import json
import pathlib
import os
import re
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('c03_acces_bench', ROOT / 'wp/tests/robots-runner/run.py')
c03 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c03)
bench = c03.bench
bench.OUT = ROOT / 'production/C-06/tests'
packet = os.environ.get('IMAGINE_C06_PACKET')
if packet is not None:
    assert re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', packet), 'Unsafe packet name'
    bench.OUT = ROOT / 'production/C-06/replays' / packet
bench.STATE = bench.OUT / 'runner-state.json'
bench.LABEL = 'org.imagine.c06-runner'
original_call = bench.call


def shared_inventory():
    files = list(bench.PLUGIN.rglob('*'))
    files += [ROOT / 'wp/tests/numeros-runner/run.py', ROOT / 'wp/tests/robots-runner/run.py']
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(files) if p.is_file() and 'vendor' not in p.parts
            and 'Acces' not in p.parts and 'Echeancier' not in p.parts}


def payload():
    import io
    import tarfile
    content = io.BytesIO()
    files = {}
    with tarfile.open(fileobj=content, mode='w') as archive:
        for path in sorted(bench.PLUGIN.rglob('*')):
            if not path.is_file() or 'vendor' in path.parts or 'Echeancier' in path.parts:
                continue
            relative = path.relative_to(bench.PLUGIN).as_posix()
            data = path.read_bytes()
            files[relative] = hashlib.sha256(data).hexdigest()
            entry = tarfile.TarInfo(relative)
            entry.size = len(data)
            entry.mode = 0o644
            archive.addfile(entry, io.BytesIO(data))
    return content.getvalue(), files


bench.payload = payload


def call(args, data=None, check=True):
    args = list(args)
    return original_call(args, data, check)


bench.call = call


def main():
    action = sys.argv[1] if len(sys.argv) > 1 else ''
    bench.OUT.mkdir(parents=True, exist_ok=True)
    baseline = bench.OUT / 'shared-before.json'
    if action == 'prepare':
        assert not baseline.exists(), 'Existing evidence: use the owned runner or preserve this packet first'
        baseline.write_text(json.dumps(shared_inventory(), indent=2), encoding='utf-8')
        c03.prepare()
        return
    assert json.loads(baseline.read_text(encoding='utf-8')) == shared_inventory(), 'Shared source drift'
    state = json.loads(bench.STATE.read_text(encoding='utf-8'))
    name = state['container']
    info = bench.info(name)
    assert not info['NetworkSettings']['Networks']
    if action == 'close':
        bench.call(['rm', '-f', name])
        missing = bench.call(['inspect', name], check=False)
        diagnostic = (missing.stdout + missing.stderr).decode(errors='replace').lower()
        assert missing.returncode != 0 and ('no such object' in diagnostic or 'no such container' in diagnostic)
        (bench.OUT / 'cleanup.json').write_text(json.dumps({
            'container': name, 'owned_runner_removed': True, 'absence_diagnostic': diagnostic,
            'shared_sources_unchanged': True, 'shared_source_count': len(shared_inventory())
        }, indent=2), encoding='utf-8')
        bench.STATE.unlink()
        print('CLOSED', name)
        return
    if '--filter' in sys.argv:
        import re
        assert re.fullmatch(r'[A-Za-z0-9_]+', sys.argv[sys.argv.index('--filter') + 1])
    stage = sys.argv[sys.argv.index('--name') + 1] if '--name' in sys.argv else 'green'
    assert not (bench.OUT / (stage + '.json')).exists(), 'Never overwrite a receipt'
    bench.call(['exec', name, 'rm', '-f', '/tmp/result.xml'])
    try:
        bench.main()
    finally:
        receipt_path = bench.OUT / (stage + '.json')
        if receipt_path.exists():
            receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
            receipt['command'] = 'composer test -- --log-junit /tmp/result.xml'
            if '--filter' in sys.argv:
                receipt['command'] += ' --filter ' + sys.argv[sys.argv.index('--filter') + 1]
            receipt['wrapper_sha256'] = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
            receipt['shared_sources_unchanged'] = shared_inventory() == json.loads(baseline.read_text(encoding='utf-8'))
            receipt_path.write_text(json.dumps(receipt, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
