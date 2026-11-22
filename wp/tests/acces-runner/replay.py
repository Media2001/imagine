"""Bounded C-06 replay: disposable PHP only, fresh receipts, owned cleanup."""
import argparse
import json
import os
import pathlib
import re
import subprocess
import sys
import uuid

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[3]
RUNNER = ROOT / 'wp/tests/acces-runner'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--packet', default='parent-' + uuid.uuid4().hex[:12])
    args = parser.parse_args()
    assert re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', args.packet), 'Unsafe packet name'
    output = ROOT / 'production/C-06/replays' / args.packet
    assert not output.exists(), 'Existing packet: use another name, never overwrite evidence'
    env = dict(os.environ, IMAGINE_C06_PACKET=args.packet, PYTHONDONTWRITEBYTECODE='1')

    def invoke(script, arguments, timeout):
        result = subprocess.run([sys.executable, '-B', str(RUNNER / script)] + arguments,
                                cwd=ROOT, env=env, timeout=timeout)
        if result.returncode:
            raise RuntimeError(f'{script} {arguments}: exit {result.returncode}; see {output}')

    try:
        invoke('run.py', ['prepare'], 420)
        invoke('run.py', ['run', '--name', 'final'], 180)
        invoke('check-standard-suite.py', [str(output / 'final.xml')], 30)
    finally:
        if (output / 'runner-state.json').exists():
            invoke('run.py', ['close'], 60)
    invoke('verify.py', ['seal'], 60)
    invoke('verify.py', ['check'], 60)
    seal = json.loads((output / 'artifact-verification.json').read_text(encoding='utf-8'))
    print(json.dumps({'status': seal['status'], 'packet': args.packet,
                      'suites': seal['suites'], 'container_absent': True}, indent=2))


if __name__ == '__main__':
    main()
