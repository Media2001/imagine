"""C-07: reuse the disposable C-03 bench; no shared runner edits."""
import importlib.util
import io
import json
import pathlib
import os
import re
import sys
import tarfile

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('c07_c03', ROOT / 'wp/tests/robots-runner/run.py')
c03 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c03)
bench = c03.bench
bench.OUT = ROOT / 'production/C-07/tests'
packet = os.environ.get('IMAGINE_C07_PACKET')
if packet is not None:
    assert re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', packet), 'Unsafe packet name'
    bench.OUT = ROOT / 'production/C-07/replays' / packet
bench.STATE = bench.OUT / 'runner-state.json'
bench.LABEL = 'org.imagine.c07-runner'
original_payload = bench.payload


def payload():
    data, files = original_payload()
    source = ROOT / 'wp/plugins/imagine-connecteur'
    buffer = io.BytesIO(data)
    with tarfile.open(fileobj=buffer, mode='a') as archive:
        paths = list((source / 'src').glob('*.php')) + list((source / 'tests').glob('*.php'))
        for path in sorted(paths):
            content = path.read_bytes()
            name = ('connecteur/' if path.parent.name == 'src' else 'connecteur-tests/') + path.name
            item = tarfile.TarInfo(name)
            item.size = len(content)
            item.mode = 0o644
            archive.addfile(item, io.BytesIO(content))
            import hashlib
            files[name] = hashlib.sha256(content).hexdigest()
    return buffer.getvalue(), files


bench.payload = payload
if __name__ == '__main__':
    if sys.argv[1:] == ['prepare']:
        c03.prepare()
    else:
        if sys.argv[1:2] == ['run']:
            stage = sys.argv[sys.argv.index('--name') + 1] if '--name' in sys.argv else 'green'
            assert re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', stage), 'Unsafe receipt name'
            assert not (bench.OUT / (stage + '.json')).exists(), 'Never overwrite a receipt'
            state = json.loads(bench.STATE.read_text(encoding='utf-8'))
            bench.call(['exec', state['container'], 'rm', '-f', '/tmp/result.xml'])
        bench.main()
