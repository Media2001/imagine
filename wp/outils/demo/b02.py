"""B02 : installation ciblée, lecture native et HTTP sur la seule démo existante."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import base64
import hashlib
import importlib.util
import json
import sys
import c14

ROOT = c14.ROOT
PROOF = ROOT / 'production/B-02'
FILES = ['plugins/imagine-site/MonCompte.php', 'themes/imagine/parts/mon-compte.php',
         'themes/imagine/functions.php', 'plugins/imagine-site/imagine-site.php']
wp = c14.wp


def snapshot():
    # Empreintes seulement : ni secrets ni données personnelles dans les reçus.
    return wp('''global $wpdb;$out=[];
foreach(['users','posts','postmeta','wc_orders','wc_order_addresses','wc_order_operational_data','wc_orders_meta','woocommerce_order_items','woocommerce_order_itemmeta'] as $suffix){
$t=$wpdb->prefix.$suffix;if($wpdb->get_var($wpdb->prepare('SHOW TABLES LIKE %s',$wpdb->esc_like($t)))!==$t){continue;}
$r=$wpdb->get_results("SELECT * FROM `{$t}`",ARRAY_A);if($suffix==='posts'){$own=get_option('imagine_c09_fixture')['subscriptions']['A-CARTE'];foreach($r as &$row){if((int)$row['ID']===$own){unset($row['comment_count']);}}unset($row);}usort($r,static fn($a,$b)=>strcmp(wp_json_encode($a),wp_json_encode($b)));$out[$suffix]=hash('sha256',serialize($r));}
$out['roles']=hash('sha256',serialize($wpdb->get_results("SELECT * FROM {$wpdb->usermeta} WHERE meta_key LIKE '%capabilities' OR meta_key LIKE '%user_level' ORDER BY umeta_id",ARRAY_A)));
$r=$wpdb->get_results("SELECT option_name,option_value FROM {$wpdb->options} WHERE (option_name LIKE 'imagine_%' OR option_name LIKE '%user_roles') AND option_name NOT LIKE 'imagine_envoi_releve_%' ORDER BY option_name",ARRAY_A);$out['options']=hash('sha256',serialize($r));
echo wp_json_encode($out);''')


def journal():
    return wp('''global $wpdb;$rows=$wpdb->get_results("SELECT option_name,option_value FROM {$wpdb->options} WHERE option_name LIKE 'imagine_envoi_releve_%' ORDER BY option_name",ARRAY_A);$out=[];foreach($rows as $r){$out[$r['option_name']]=hash('sha256',$r['option_value']);}echo wp_json_encode($out);''')


def run(deploy=False, http=True):
    PROOF.mkdir(exist_ok=True)
    c14.c10.guard()
    before = snapshot()
    journal_before = journal()
    protected = c14.preserve()
    result = {'scope': 'imagine-test-demo', 'at': datetime.now(timezone.utc).isoformat(), 'status': 'EN_COURS'}
    def save():
        (PROOF / 'resultats.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    save()
    if deploy:
        # Bootstrap partagé : uniquement l'inclusion B02, jamais perte d'un lot précédent.
        old = base64.b64decode(c14.c10.b00.wp('eval', 'echo base64_encode(file_get_contents(WP_PLUGIN_DIR . "/imagine-site/imagine-site.php"));')['stdout'])
        source = (ROOT / 'wp/plugins/imagine-site/imagine-site.php').read_bytes()
        addition = b"require_once __DIR__ . '/MonCompte.php';\nMonCompte::register();\n\n"
        if old != source and old != source.replace(addition, b''):
            raise RuntimeError('Bootstrap partagé divergent : arrêt sans écriture')
        for rel in FILES:
            c14.upload(rel, ROOT / 'wp' / rel)
    result['deployed_bytes'] = {}
    for rel in FILES:
        actual = c14.c10.b00.wp('eval', '$p=WP_CONTENT_DIR . ' + json.dumps('/' + rel) + ';token_get_all(file_get_contents($p),TOKEN_PARSE);echo hash_file("sha256",$p);')['stdout'].strip()
        expected = hashlib.sha256((ROOT / 'wp' / rel).read_bytes()).hexdigest()
        result['deployed_bytes'][rel] = actual == expected
    for name in ['b02-runtime.php', 'b02-state.php']:
        if not (ROOT / 'wp/tests/demo' / name).exists():
            continue
        c14.upload('imagine-demo-build/' + name, ROOT / 'wp/tests/demo' / name)
        result[name] = wp('require WP_CONTENT_DIR . "/imagine-demo-build/' + name + '";')
        save()
    if http:
        test = c14.module('b02_http', 'b02-http.py')
        result['http'] = test.verify()
        save()
    result['native_snapshot_preserved'] = before == snapshot()
    journal_after = journal()
    added = set(journal_after) - set(journal_before)
    own = wp('echo wp_json_encode(get_option("imagine_c09_fixture")["subscriptions"]["A-CARTE"]);')
    result['postal_journal_append_only'] = all(journal_after.get(k) == v for k, v in journal_before.items()) and len(added) == (2 if http else 0) and all(k.startswith('imagine_envoi_releve_' + str(own) + '_') for k in added)
    result['postal_observations_added'] = len(added)
    result['closed_and_prior_lots_preserved'] = protected == c14.preserve()
    result['snapshot_before'] = before
    result['snapshot_after'] = snapshot()
    result['acceptance_blockers'] = [
        'A-4x-J45 absent de C09 et du site ; aucun alias ni état 2/4 inventé.',
        'Marge C05 non renseignée : quatre positions nommées A-SEPA4, aucune date théorique inventée.',
        'Historique activation C01 et factures/justificatifs non raccordés : emplacements nommés.'
    ]
    checks = {k + ':' + key: value for k, group in result.items() if k in ['deployed_bytes', 'b02-runtime.php', 'b02-state.php', 'http'] for key, value in group.items()}
    checks.update({k: result[k] for k in ['native_snapshot_preserved', 'closed_and_prior_lots_preserved', 'postal_journal_append_only']})
    result['total'] = len(checks)
    result['failures'] = [k for k, v in checks.items() if v is not True]
    result['status'] = 'TECHNIQUE_VERT_ACCEPTATION_PARTIELLE' if not result['failures'] else 'ECHEC'
    save()
    print(json.dumps({k: result[k] for k in ['status', 'total', 'failures', 'acceptance_blockers']}, ensure_ascii=False, indent=2))
    if result['failures']:
        raise SystemExit(1)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--deploy', action='store_true')
    parser.add_argument('--native-only', action='store_true')
    parser.add_argument('--require-complete', action='store_true')
    args = parser.parse_args()
    result = run(args.deploy, not args.native_only)
    if args.require_complete and result['acceptance_blockers']:
        raise SystemExit(2)
