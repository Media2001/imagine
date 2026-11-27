"""Adversarial read-only verifier replay in an owned scratch mirror only."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
sys.dont_write_bytecode = True
from delivery import BASE, EXCLUDE, OWN, ROOT, digest, inventory, load, read


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', required=True, type=Path)
    a = ap.parse_args()
    out = a.output.resolve()
    if out.is_relative_to(ROOT) or ROOT.is_relative_to(out):
        raise ValueError('A33_SCRATCH_REQUIRED')
    out.mkdir(parents=True, exist_ok=False)
    mirror = out / 'mirror'
    runner = load('a33_probe_runner', Path(__file__).with_name('run.py'))
    names = inventory(OWN + runner.DEPS)
    names['wp/outils/bascule/README.md'] = digest(ROOT / 'wp/outils/bascule/README.md')
    for key in names:
        dest = mirror / key
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / key, dest)
    rows = []
    env = {**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONDONTWRITEBYTECODE': '1'}
    env.pop('TMPDIR', None)

    def execute(label, expected=None, args=()):
        p = subprocess.run([sys.executable, '-B', str(mirror / BASE / 'verify.py'), *args], cwd=mirror, capture_output=True, text=True, encoding='utf-8', errors='strict', env=env, timeout=90)
        d = json.loads(p.stdout)
        actual = d['checks'][0]['check']
        ok = p.stderr == '' and (p.returncode == 0 and actual == 'A33_PACKAGE_PASS' if expected is None else p.returncode == 1 and actual == expected)
        rows.append({'check': label, 'status': 'PASS' if ok else 'FAIL', 'exit_code': p.returncode, 'control': actual})
        return ok

    def reseal():
        (mirror / BASE / 'manifest.json').write_text(json.dumps({'lot': 'A-33', 'files': inventory(OWN, mirror, EXCLUDE)}, indent=2) + '\n', encoding='utf-8')

    def mutate(label, key, fn, expected):
        path = mirror / key
        before = path.read_bytes()
        manifest = (mirror / BASE / 'manifest.json').read_bytes()
        try:
            fn(path)
            reseal()
            execute(label, expected)
        finally:
            path.write_bytes(before)
            (mirror / BASE / 'manifest.json').write_bytes(manifest)

    def change_json(fn):
        def change(p):
            d = read(p)
            fn(d)
            p.write_text(json.dumps(d, indent=2) + '\n', encoding='utf-8')
        return change

    try:
        execute('authentic_packet')
        execute('unexpected_argument', 'A33_ARGUMENTS_REFUSED', ['--A33_ARG_CANARY=private'])
        folder = BASE + '/preuves/final/'
        mutate('resealed_missing_file_channel', folder + 'utf8/native/result.json', change_json(lambda d: d['checks'].__setitem__(slice(None), [r for r in d['checks'] if r['check'] != 'channel_file'])), 'A33_PARTIAL_EVIDENCE')
        mutate('resealed_native_hidden_red', folder + 'utf8/native/result.json', change_json(lambda d: d['checks'][0].update(status='FAIL')), 'A33_PARTIAL_EVIDENCE')
        mutate('resealed_database_mutation', folder + 'utf8/native/db-after.json', change_json(lambda d: d.update(logical_sha256='0' * 64)), 'A33_PARTIAL_EVIDENCE')
        mutate('resealed_dirty_windows', folder + 'cp1252/environment.json', change_json(lambda d: d.update(tmpdir='forbidden')), 'A33_PARTIAL_EVIDENCE')
        mutate('resealed_incomplete_missing_as_zero', folder + 'utf8/native/r1-nominal/archives.json', change_json(lambda d: d['outside_media_by_year'][0]['files'].update(total_bytes=0)), 'A33_PARTIAL_EVIDENCE')
        mutate('resealed_executed_source_changed', 'wp/outils/bascule/a33/Analysis.php', lambda p: p.write_bytes(p.read_bytes() + b'\n'), 'A33_PARTIAL_EVIDENCE')
        contract = (mirror / BASE / 'readme-ajout.txt').read_bytes().splitlines(keepends=True)
        mutate('readme_unrelated_append_allowed', 'wp/outils/bascule/README.md', lambda p: p.write_bytes(p.read_bytes() + b'Other owned lot appendix\n'), None)
        mutate('readme_owned_duplicate_refused', 'wp/outils/bascule/README.md', lambda p: p.write_bytes(p.read_bytes() + contract[-1]), 'A33_README_CONTRACT_DRIFT')
        # Forge an internally rehashed log, not merely a broken outer digest.
        command_path = mirror / folder / 'gates/commands.json'
        log_path = mirror / folder / 'gates/global-utf8.stdout.log'
        originals = [p.read_bytes() for p in (command_path, log_path, mirror / BASE / 'manifest.json')]
        try:
            text = log_path.read_text(encoding='utf-8')
            lines = text.splitlines()
            for i, line in enumerate(lines):
                if line.startswith('T01_RESULT '):
                    d = json.loads(line[len('T01_RESULT '):])
                    d['packets']['failures'] = [{'lot': 'A-33', 'control': 'A33_PACKET_INVALID'}]
                    lines[i] = 'T01_RESULT ' + json.dumps(d)
            log_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
            commands = read(command_path)
            next(r for r in commands if r['name'] == 'global-utf8')['stdout_sha256'] = digest(log_path)
            command_path.write_text(json.dumps(commands, indent=2) + '\n', encoding='utf-8')
            reseal()
            execute('resealed_rehashed_global_packet_red', 'A33_GATES_INVALID')
        finally:
            for p, data in zip((command_path, log_path, mirror / BASE / 'manifest.json'), originals):
                p.write_bytes(data)
        execute('restored_authentic_packet')
    finally:
        shutil.rmtree(mirror)
    result = {'exit_code': int(any(r['status'] != 'PASS' for r in rows)), 'checks': rows, 'mirror_removed': not mirror.exists()}
    (out / 'probes.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
    return result['exit_code']


if __name__ == '__main__':
    sys.exit(main())
