"""A28 Windows gate receipts: explicit child encodings, real exit statuses."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]


def sources():
    files = []
    for folder in ('wp/outils/staging', 'wp/outils/staging-court', 'wp/tests/a28'):
        files += [p for p in (ROOT / folder).rglob('*') if p.is_file() and p.suffix in ('.py', '.php', '.json')
                  and '__pycache__' not in p.parts]
    files += list((ROOT / 'production/A-28').glob('*.py'))
    files += list((ROOT / 'production/A-28/reference').glob('*.php'))
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(files))}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--python-only', action='store_true')
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    frozen = sources()
    (out / 'freeze.json').write_text(json.dumps({'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                              'sources': frozen}, indent=2), encoding='utf-8')
    rows = []

    def run(name, argv, encoding='utf-8', utf8='1'):
        env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONIOENCODING': encoding, 'PYTHONUTF8': utf8}
        p = subprocess.run(argv, cwd=ROOT, env=env, capture_output=True, timeout=1800)
        (out / (name + '.stdout.log')).write_bytes(p.stdout)
        (out / (name + '.stderr.log')).write_bytes(p.stderr)
        row = {'name': name, 'argv': argv, 'exit': p.returncode, 'encoding': encoding, 'utf8': utf8,
               'sources_stable': sources() == frozen, 'stdout_sha256': hashlib.sha256(p.stdout).hexdigest(),
               'stderr_sha256': hashlib.sha256(p.stderr).hexdigest()}
        if name.startswith('python-') or name.startswith('a01-windows-'):
            text = p.stderr.decode(encoding, errors='strict')
            counts = re.findall(r'^Ran (\d+) tests? in ', text, re.M)
            row['tests'] = int(counts[0]) if len(counts) == 1 else 0
        rows.append(row)
        (out / 'commands.json').write_text(json.dumps(rows, indent=2), encoding='utf-8')
        print(name + ': ' + str(p.returncode), flush=True)
        return row['exit'] == 0 and row['sources_stable']

    ok = True
    for suffix, encoding, mode in [('utf8', 'utf-8', '1'), ('cp1252', 'cp1252', '0')]:
        probe = 'import sys,locale,json;print(json.dumps({"executable":sys.executable,"version":sys.version,"stdout":sys.stdout.encoding,"stderr":sys.stderr.encoding,"utf8":sys.flags.utf8_mode,"locale":locale.getencoding(),"preferred":locale.getpreferredencoding(False)}))'
        ok = run('environment-' + suffix, [sys.executable, '-c', probe], encoding, mode) and ok
        ok = run('python-' + suffix, [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'wp/tests/a28', '-p', 'test_*.py', '-v'], encoding, mode) and ok
        ok = run('a01-windows-' + suffix, [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'wp/tests/a01-court', '-p', 'test_*.py', '-v'], encoding, mode) and ok
    if not args.python_only:
        ok = run('prepare-image', ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', 'wp/tests/preparer-image.ps1']) and ok
        for suffix, encoding, mode in [('utf8', 'utf-8', '1'), ('cp1252', 'cp1252', '0')]:
            ok = run('global-' + suffix, ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', 'wp/tests/rejouer.ps1'], encoding, mode) and ok
    result = {'status': 'PASS' if ok else 'FAIL', 'exit': 0 if ok else 1, 'sources_stable': sources() == frozen,
              'commands': len(rows), 'python_executable': sys.executable}
    (out / 'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    return result['exit']


if __name__ == '__main__':
    raise SystemExit(main())
