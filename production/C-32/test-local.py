"""C32 seulement : tests purs locaux, conteneur jetable sans réseau ni site.
Usage : python -B production/C-32/test-local.py LABEL
Aucune préparation d'image, aucun rejeu global, aucune commande Git.
"""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent


def main(label):
    if not label or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in label):
        raise ValueError('Étiquette locale invalide')
    target = OUT/(label+'.json')
    if target.exists():
        raise FileExistsError(target)
    image = 'imagine-tests-t01:1'
    docker = ['wsl.exe', '-d', 'Ubuntu', '--', 'docker']
    runs = []
    def run(name, command):
        r = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace', env={**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONDONTWRITEBYTECODE': '1'}, timeout=180)
        log = label+'-'+name+'.log'
        with (OUT/log).open('x', encoding='utf-8') as f:
            f.write(r.stdout+r.stderr)
        record = {'name': name, 'command': command, 'exit': r.returncode, 'log': log, 'log_sha256': hashlib.sha256((OUT/log).read_bytes()).hexdigest()}
        runs.append(record)
        print(name, 'exit='+str(r.returncode))
        return r
    inspected = run('image-inspect', docker+['image', 'inspect', image, '--format', '{{.Id}}'])
    if inspected.returncode:
        raise RuntimeError('Image locale préexistante requise ; aucune préparation automatique')
    image_id = inspected.stdout.strip()
    base = docker+['run', '--rm', '--pull', 'never', '--network', 'none', '--read-only', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--user', '65534:65534', '--pids-limit', '64', '--memory', '256m', '--cpus', '1', '--tmpfs', '/tmp:rw,nosuid,nodev,size=64m', '--mount', 'type=bind,source=/mnt/c/Users/Ced/imagine/wp,target=/repo/wp,readonly', '--entrypoint', 'php', image_id]
    run('python', [sys.executable, '-B', str(ROOT/'wp/tests/demo/c32-browser-test.py')])
    run('php-lint', base+['-l', '/repo/wp/plugins/imagine-site/Cookies.php'])
    run('phpunit', base+['/opt/t01/imagine-site/vendor/phpunit/phpunit/phpunit', '--no-configuration', '--bootstrap', '/repo/wp/tests/demo/c32-phpunit-bootstrap.php', '--do-not-cache-result', '--fail-on-warning', '--fail-on-risky', '--fail-on-deprecation', '/repo/wp/plugins/imagine-site/tests/CookiesC32Test.php'])
    selected = [ROOT/'wp/plugins/imagine-site/Cookies.php', ROOT/'wp/plugins/imagine-site/AutresPages.php']
    selected += [p for p in (ROOT/'wp/plugins/imagine-site/tests').glob('*C32*') if p.is_file()]
    selected += [p for folder in ['wp/outils/demo', 'wp/tests/demo'] for p in (ROOT/folder).glob('c32*') if p.is_file()]
    selected += [p for p in OUT.glob('*.py') if p.is_file()]
    selected += [OUT/'A-VOIR.md', OUT/'official-corrections-V2.json', ROOT/'production/C-26/mutations-livraison-extension.json']
    syntax = 'import ast; from pathlib import Path; paths='+repr([str(p) for p in selected if p.suffix=='.py'])+'; [ast.parse(Path(p).read_text(encoding="utf-8"),filename=p) for p in paths]; print("C32 Python syntax PASS:",len(paths),"files")'
    run('python-syntax', [sys.executable, '-B', '-c', syntax])
    sys.path.insert(0, str(OUT))
    import reception_c32 as reader
    with reader.c.bound(reader.owner):
        section = reader.c.core.section('C32')
    result = {'readme_section': hashlib.sha256(section.encode()).hexdigest(), 'scope': 'C32_LOCAL_OFFLINE_ONLY', 'live_validated': False, 'global_replay': False, 'image_prepared': False, 'image_id': image_id, 'runs': runs, 'pass': all(r['exit']==0 for r in runs), 'sources': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(selected))}}
    with target.open('x', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    return 0 if result['pass'] else 1


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage : python -B production/C-32/test-local.py LABEL')
    raise SystemExit(main(sys.argv[1]))
