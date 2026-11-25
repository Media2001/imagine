"""C15 final receipts after writes; optional authorized T01 preparation, no theme deploy."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import subprocess
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'wp/outils/demo'))
import c15


def local_runner(name):
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), ROOT / 'wp/outils/demo' / (name + '.py'))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


def main():
    c15.profils.guard('imagine-test-demo')
    protected_code = r'''$out=[];foreach(['imagine-site','imagine-pilotage','imagine-connecteur'] as $dir){foreach(new RecursiveIteratorIterator(new RecursiveDirectoryIterator(WP_PLUGIN_DIR.'/'.$dir,FilesystemIterator::SKIP_DOTS)) as $file){$p=$file->getPathname();if($file->isFile()&&str_ends_with($p,'.php')&&!str_contains($p,'/vendor/')&&!str_contains($p,'/tests')&&!in_array($file->getFilename(),['EcheancesAdmin.php','EcheancesNatives.php','EcheancesRegles.php','imagine-site.php'],true)){$out[$p]=hash_file('sha256',$p);}}}ksort($out);echo wp_json_encode($out);'''
    protected_before = c15.wp(protected_code)
    result = {'scope': 'imagine-test-demo', 'at': datetime.now(timezone.utc).isoformat()}
    if '--prepare' in sys.argv:
        p = subprocess.run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(ROOT / 'wp/tests/preparer-image.ps1')], capture_output=True, text=True, encoding='utf-8', errors='replace')
        (c15.PROOF / 'preparation-image.log').write_text(p.stdout + p.stderr, encoding='utf-8')
        result['preparation_image_exit'] = p.returncode
        if p.returncode:
            raise RuntimeError('T01 preparation failed')
    result['pure'] = local_runner('c15-unit').run('pure-final')
    result['regression_C13_pure'] = local_runner('c13-unit').run()
    c15.deploy()
    result['runtime'] = c15.runtime('runtime-final')
    result['HTTP'] = c15.load_test('c15-http').verify()
    if '--action' in sys.argv:
        result['action_HTTP_et_reset'] = c15.load_test('c15-action').verify()
        # Re-read all five views after the reset, with freshly authenticated accounts.
        result['runtime_apres_reset'] = c15.runtime('runtime-apres-reset')
        result['HTTP_apres_reset'] = c15.load_test('c15-http').verify()
    raw = c15.profils.b00.wp('eval', 'require WP_CONTENT_DIR."/imagine-demo-build/c09-payments.php";', check=False)
    if raw['stderr']:
        raise RuntimeError('C09 readback warning')
    native = json.loads(raw['stdout'])
    if raw['code'] or native['failures']:
        raise RuntimeError('C09 native payments no longer valid')
    result['C09_paiements_natifs'] = {'total': native['total'], 'failures': native['failures'], 'exit': raw['code']}
    files = list((ROOT / 'wp/plugins/imagine-site').glob('Echeances*.php')) + [ROOT / 'wp/plugins/imagine-site/imagine-site.php']
    result['source_sha256'] = {str(p.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    result['tests_total_sans_doublonner_relectures'] = result['pure']['total'] + result['regression_C13_pure']['tests'] + len(result['runtime']) + len(result['HTTP']) + len(result.get('action_HTTP_et_reset', {})) + native['total']
    result['sources_B02_C13_et_bibliotheques_preservees'] = protected_before == c15.wp(protected_code)
    if not result['sources_B02_C13_et_bibliotheques_preservees']:
        raise RuntimeError('Protected plugin source changed')
    result['theme_televerse'] = False
    result['status'] = 'PRET_RELECTURE' if '--action' in sys.argv else 'TECHNIQUE_SANS_REJEU_ACTION'
    c15.save('verification', result)
    print(json.dumps({'status': result['status'], 'total': result['tests_total_sans_doublonner_relectures'], 'C09': native['total']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
