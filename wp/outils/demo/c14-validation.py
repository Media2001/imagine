"""Rejeu C14 complet et preuves actuelles, sans toucher PRET ni réinitialiser un profil."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import c14


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def run(prepare=False, deploy_code=False):
    c14.c10.guard()
    proof = c14.PROOF
    marker = proof / 'PRET'
    marker_before = hashlib.sha256(marker.read_bytes()).hexdigest() if marker.exists() else None
    shared = c14.preserve()
    result = {'at': datetime.now(timezone.utc).isoformat(), 'scope': 'imagine-test-demo',
              'status': 'EN_COURS', 'commands': [], 'PRET_before': marker_before, 'shared_before': digest(shared)}
    receipt = proof / 'validation-corrections.json'

    def save():
        receipt.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')

    def execute(name, command, timeout=600):
        p = subprocess.run(command, cwd=c14.ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=timeout)
        text = p.stdout + p.stderr
        (proof / ('validation-' + name + '.log')).write_text(text, encoding='utf-8')
        result['commands'].append({'name': name, 'argv': command, 'exit': p.returncode, 'log': 'validation-' + name + '.log'})
        save()
        print(name + ': exit ' + str(p.returncode), flush=True)
        if p.returncode:
            raise RuntimeError(name + ' en échec, voir le journal')
        return text

    try:
        if prepare:
            execute('image', ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(c14.ROOT / 'wp/tests/preparer-image.ps1')])
        text = execute('t01', ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(c14.ROOT / 'wp/tests/rejouer.ps1')])
        match = re.findall(r'^T01_RESULT (\{[^\n]+\})', text, re.M)
        if len(match) != 1:
            raise RuntimeError('Bilan T01 absent/ambigu')
        result['T01'] = json.loads(match[0])
        execute('c14', [sys.executable, str(c14.ROOT / 'wp/outils/demo/c14.py')] + (['--deploy-code'] if deploy_code else []))
        execute('regressions', [sys.executable, str(c14.ROOT / 'wp/outils/demo/c14-regressions.py')])
        execute('phpcs', ['wsl.exe', '-d', 'Ubuntu', '--', 'docker', 'run', '--rm', '--pull', 'never', '--network', 'none',
            '--read-only', '--tmpfs', '/tmp:rw,nosuid,nodev,size=16m,mode=1777', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges',
            '--user', '65534:65534', '--mount', 'type=bind,source=/mnt/c/Users/Ced/imagine/wp,target=/repo/wp,readonly',
            '--entrypoint', 'php', 'imagine-tests-t01:1', '/opt/t01/imagine-site/vendor/bin/phpcs', '--standard=PSR12',
            '/repo/wp/plugins/imagine-site/AchatNumero.php', '/repo/wp/plugins/imagine-site/AchatsNumeros.php',
            '/repo/wp/plugins/imagine-site/tests/AchatNumeroTest.php'])
        result['cleanup'] = c14.wp(r'''require_once WP_CONTENT_DIR . '/imagine-demo-build/c14-profil.php';
Imagine\Demo\C14\guard();global $wpdb;
echo wp_json_encode([
 'temporary_users'=>(int)$wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->usermeta} WHERE meta_key='_imagine_c14_fixture'"),
 'temporary_posts'=>(int)$wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->postmeta} WHERE meta_key='_imagine_c14_fixture' AND meta_value<>'profil'"),
 'refunds'=>count(wc_get_orders(['type'=>'shop_order_refund','limit'=>-1,'return'=>'ids'])),
 'policy'=>get_option(Imagine\Site\AchatsNumeros::REMBOURSEMENT,'commande')]);''')
        if any(result['cleanup'][k] != 0 for k in ['temporary_users', 'temporary_posts', 'refunds']):
            raise RuntimeError('Fixtures C14 résiduelles')
        result['shared_after'] = digest(c14.preserve())
        result['shared_preserved'] = result['shared_before'] == result['shared_after']
        result['PRET_after'] = hashlib.sha256(marker.read_bytes()).hexdigest() if marker.exists() else None
        result['PRET_unchanged'] = result['PRET_before'] == result['PRET_after']
        if not result['shared_preserved'] or not result['PRET_unchanged']:
            raise RuntimeError('État partagé ou PRET divergent')
        for filename in ['resultats.json', 'regressions.json']:
            data = json.loads((proof / filename).read_text(encoding='utf-8'))
            if data['status'] != 'VERT':
                raise RuntimeError('Reçu non vert : ' + filename)
            result[filename] = {'total': data['total'], 'sha256': hashlib.sha256((proof / filename).read_bytes()).hexdigest()}
        result['status'] = 'VERT'
        result['completed_at'] = datetime.now(timezone.utc).isoformat()
        print(json.dumps({k: result[k] for k in ['status', 'T01', 'cleanup', 'shared_preserved', 'PRET_unchanged']}, ensure_ascii=False), flush=True)
    except Exception as error:
        result['status'] = 'ECHEC'
        result['error'] = str(error)
        raise
    finally:
        save()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--deploy-code', action='store_true')
    args = parser.parse_args()
    run(args.prepare, args.deploy_code)
