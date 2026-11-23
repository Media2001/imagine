"""C10 : déploiement ciblé des adaptateurs, jamais de reconstruction B00."""
from pathlib import Path
import argparse
import hashlib
import json
from datetime import datetime, timezone
import c08
import construire as b00

ROOT = b00.ROOT
PROOF = ROOT / 'production/C-10'
FILES = [
    'plugins/imagine-site/Paywall.php',
    'plugins/imagine-pilotage/imagine-reglages.php',
    'plugins/imagine-pilotage/src/Administration/Reglages.php',
    'plugins/imagine-pilotage/src/Acces/AdministrationReglages.php',
    'plugins/imagine-pilotage/src/Echeancier/ReglagesAdministration.php',
    'plugins/imagine-pilotage/src/Envoi/AdministrationFormatExport.php',
]


def snapshot():
    code = '''$out=[];foreach(['imagine_c08_fixture','imagine_c09_fixture','imagine_demo_manifest','imagine_acces_plans'] as $k){$out[$k]=get_option($k);}global $wpdb;$out['users']=$wpdb->get_results("SELECT ID,user_login,user_pass FROM {$wpdb->users} ORDER BY ID",ARRAY_A);$out['postmeta']=$wpdb->get_results("SELECT * FROM {$wpdb->postmeta} WHERE post_id NOT IN (SELECT post_id FROM {$wpdb->postmeta} WHERE meta_key='_imagine_c10_fixture') ORDER BY meta_id",ARRAY_A);$out['rights_meta']=$wpdb->get_results("SELECT * FROM {$wpdb->usermeta} WHERE meta_key LIKE '%capabilities' OR meta_key LIKE '_imagine_%' ORDER BY umeta_id",ARRAY_A);foreach(['wc_orders','wc_order_addresses','wc_order_operational_data','wc_orders_meta','woocommerce_order_items','woocommerce_order_itemmeta'] as $suffix){$table=$wpdb->prefix.$suffix;if($wpdb->get_var($wpdb->prepare('SHOW TABLES LIKE %s',$wpdb->esc_like($table)))===$table){$rows=$wpdb->get_results("SELECT * FROM `{$table}`",ARRAY_A);usort($rows,static fn($a,$b)=>strcmp(wp_json_encode($a),wp_json_encode($b)));$out[$suffix]=$rows;}}$out['posts']=$wpdb->get_results("SELECT ID,post_type,post_status,post_content,post_password FROM {$wpdb->posts} WHERE ID NOT IN (SELECT post_id FROM {$wpdb->postmeta} WHERE meta_key='_imagine_c10_fixture') ORDER BY ID",ARRAY_A);$out['safety']=hash_file('sha256',WPMU_PLUGIN_DIR . '/imagine-demo-offline.php');$out['site']=hash_file('sha256',WP_PLUGIN_DIR . '/imagine-site/imagine-site.php');$closed=[];foreach(['imagine-pilotage','imagine-connecteur'] as $dir){foreach(new RecursiveIteratorIterator(new RecursiveDirectoryIterator(WP_PLUGIN_DIR . '/' . $dir . '/src',FilesystemIterator::SKIP_DOTS)) as $f){$p=$f->getPathname();if(str_contains($p,'/Administration/')||in_array($f->getFilename(),['AdministrationReglages.php','ReglagesAdministration.php','AdministrationFormatExport.php'],true)){continue;}$closed[$p]=hash_file('sha256',$p);}}ksort($closed);$out['closed']=$closed;echo hash('sha256',wp_json_encode($out));'''
    return b00.wp('eval', code)['stdout'].strip()


def guard():
    site, state = c08.guard()
    if site['url'].rstrip('/') != 'http://192.168.129.32:8085':
        raise RuntimeError('C10 refuse une URL différente de la démonstration autorisée.')
    return site, state


def run(tests_only=False):
    site, before = guard()
    PROOF.mkdir(parents=True, exist_ok=True)
    protected = snapshot()
    files = {} if tests_only else {rel: ROOT / 'wp' / rel for rel in FILES}
    if not tests_only:
        files['imagine-demo-build/c10-fixture.php'] = ROOT / 'wp/tests/demo/c10-fixture.php'
    files['imagine-demo-build/c10-runtime.php'] = ROOT / 'wp/tests/demo/c10-runtime.php'
    hashes = {}
    for rel, source in files.items():
        data = source.read_bytes()
        hashes[rel] = hashlib.sha256(data).hexdigest()
        b00.upload(rel, data)
    code = '$files=json_decode(' + json.dumps(json.dumps(list(files))) + ',true);$out=[];foreach($files as $f){$p=WP_CONTENT_DIR . "/" . $f;token_get_all(file_get_contents($p),TOKEN_PARSE);$out[$f]=hash_file("sha256",$p);}echo wp_json_encode($out);'
    actual = json.loads(b00.wp('eval', code)['stdout'])
    if hashes != actual:
        raise RuntimeError('Readback divergent.')
    if not tests_only:
        b00.wp('plugin', 'activate', 'imagine-pilotage/imagine-reglages.php')
        active = json.loads(b00.wp('eval', 'echo wp_json_encode(is_plugin_active("imagine-pilotage/imagine-reglages.php"));')['stdout'])
        if not active:
            raise RuntimeError('Activation non relue.')
    fixture = None if tests_only else b00.wp('eval', 'require WP_CONTENT_DIR . "/imagine-demo-build/c10-fixture.php";')
    runtime = b00.wp('eval', 'require WP_CONTENT_DIR . "/imagine-demo-build/c10-runtime.php";', check=False)
    record = {'scope': site['slug'], 'at': datetime.now(timezone.utc).isoformat(), 'url': site['url'],
              'files_sha256': actual, 'file_count': len(actual), 'runtime': runtime, 'fixture': fixture,
              'protected_before': protected, 'protected_after': snapshot(),
              'manifest_unchanged': before == c08.guard()[1]}
    record['status'] = 'VERIFIED' if runtime['code'] == 0 and record['protected_before'] == record['protected_after'] and record['manifest_unchanged'] else 'RED' if tests_only else 'FAILED'
    (PROOF / ('red-runtime.json' if tests_only else 'installation.json')).write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(record, ensure_ascii=False, indent=2))
    if record['status'] != 'VERIFIED':
        raise SystemExit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tests-only', action='store_true')
    run(parser.parse_args().tests_only)
