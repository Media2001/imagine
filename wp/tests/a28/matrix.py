"""Serialize the complete A28 native bank under both real Windows encodings."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
sys.dont_write_bytecode = True
from gates import sources
ROOT = Path(__file__).resolve().parents[3]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    base = args.output.resolve()
    base.mkdir(parents=True, exist_ok=False)
    frozen = sources()
    (base / 'freeze.json').write_text(json.dumps(frozen, indent=2), encoding='utf-8')
    result = {'status': 'FAIL', 'commands': [], 'contexts': ['utf8', 'cp1252']}
    for context, encoding, utf8 in [('utf8', 'utf-8', '1'), ('cp1252', 'cp1252', '0')]:
        env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONIOENCODING': encoding, 'PYTHONUTF8': utf8}
        probe = 'import sys,os,json;print(json.dumps({"platform":sys.platform,"executable":sys.executable,"version":sys.version,"stdout":sys.stdout.encoding,"stderr":sys.stderr.encoding,"utf8":sys.flags.utf8_mode}))'
        measured = subprocess.run([sys.executable, '-B', '-c', probe], env=env, capture_output=True, timeout=30)
        assert measured.returncode == 0 and not measured.stderr
        argv = [sys.executable, '-B', str(Path(__file__).with_name('run.py')), '--output', str(base / context)]
        p = subprocess.run(argv, cwd=ROOT, env=env, capture_output=True, timeout=1800)
        (base / (context + '.stdout.log')).write_bytes(p.stdout)
        (base / (context + '.stderr.log')).write_bytes(p.stderr)
        folder = base / context
        if folder.exists():
            (folder / 'environment.json').write_bytes(measured.stdout)
        row = {'context': context, 'argv': argv, 'exit': p.returncode, 'sources_stable': sources() == frozen,
               'stdout_sha256': hashlib.sha256(p.stdout).hexdigest(), 'stderr_sha256': hashlib.sha256(p.stderr).hexdigest()}
        result['commands'].append(row)
        (base / 'matrix.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(context + ': exit ' + str(p.returncode), flush=True)
        if p.returncode or not row['sources_stable']:
            return 1
    result['status'] = 'PASS'
    (base / 'matrix.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
