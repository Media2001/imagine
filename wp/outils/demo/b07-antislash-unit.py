"""Complément B07 : PHPUnit réel isolé, reçus séparés de l'ancien paquet."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PROOF = ROOT / 'production/B-07'
SOURCES = ['wp/plugins/imagine-site/Agenda.php',
           'wp/plugins/imagine-site/tests/AgendaWPStubs.php',
           'wp/plugins/imagine-site/tests/AgendaAdapterTest.php',
           'wp/tests/demo/b07-antislash-horslive.php',
           'wp/outils/demo/b07-antislash-unit.py']


def hashes():
    return {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in SOURCES}


def run(label, mutation=''):
    assert label.replace('-', '').isalnum()
    log = PROOF / ('antislash-' + label + '.log')
    receipt = log.with_suffix('.json')
    assert not log.exists() and not receipt.exists()
    command = ['wsl.exe', '-d', 'Ubuntu', '--', 'docker', 'run', '--rm', '--pull', 'never',
               '--network', 'none', '--read-only', '--user', '65534:65534', '--cap-drop', 'ALL',
               '--security-opt', 'no-new-privileges', '--mount',
               'type=bind,source=/mnt/c/Users/Ced/imagine/wp,target=/repo/wp,readonly',
               '--tmpfs', '/tmp:rw,nosuid,nodev,size=512m,mode=1777', '--entrypoint', 'php',
               'imagine-tests-t01:1', '/repo/wp/tests/demo/b07-antislash-horslive.php']
    if mutation:
        command.append(mutation)
    before = hashes()
    result = subprocess.run(command, capture_output=True, encoding='utf-8', timeout=180)
    assert hashes() == before, 'Source modifiée pendant les tests'
    text = result.stdout + result.stderr
    log.write_text(text, encoding='utf-8')
    receipt.write_text(json.dumps({'scope': 'B07-complement-antislash', 'command': command,
                                  'exit': result.returncode, 'sources': before,
                                  'log': log.name, 'log_sha256': hashlib.sha256(log.read_bytes()).hexdigest()},
                                 ensure_ascii=False, indent=2), encoding='utf-8')
    print(text)
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(run(*sys.argv[1:]))
