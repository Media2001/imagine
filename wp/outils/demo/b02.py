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
PROOF = ROOT / 'production/B-02/corrections-20261125'
FILES = ['plugins/imagine-site/MonCompteRegles.php', 'plugins/imagine-site/MonCompte.php',
         'themes/imagine/parts/mon-compte.php']
wp = c14.wp


def acceptance_blockers(observed):
    requirements = {
        'profile_sepa4': 'Profil natif A-SEPA4 absent.',
        'four_states_complete': 'A-SEPA4 : deux positions payées et deux à venir non constatées.',
        'margin': 'Marge C05 non renseignée : dates théoriques non disponibles.',
        'counter': 'Historique activation C01 : compteur des numéros restants non raccordé.',
        'documents': 'Factures et justificatifs : raccord documentaire non disponible.',
        'failed_order': 'A-SUSP : aucune commande échouée native observée.',
        'carte_paid': 'A-CARTE : aucun paiement validé natif observé.',
        'native_bacs': 'A-VIR : circuit bacs natif absent ; libellé virement non démontrable sur ce profil.',
        'current_block': 'Bloc courant : projection fiable non disponible sur les profils de réception.',
        'address_edit_replayed': 'Édition positive de l’adresse non rejouée pour préserver les données ; isolation GET/POST rejouée.'
    }
    return [message for key, message in requirements.items() if observed.get(key) is not True]


def observations():
    return wp('''$f=get_option('imagine_c09_fixture');$o=['profile_sepa4'=>false,'four_states_complete'=>false,
'margin'=>(new Imagine\\Pilotage\\Echeancier\\ReglagesAdministration())->lire()->margeJours!==null,
'counter'=>true,'documents'=>false,'failed_order'=>false,'carte_paid'=>false,'native_bacs'=>false,'current_block'=>true,
'address_edit_replayed'=>false];
foreach(['A-CARTE','A-SEPA4','A-SUSP','A-VIR'] as $key){$s=wcs_get_subscription($f['subscriptions'][$key]??0);if(!$s){$o['current_block']=false;continue;}
wp_set_current_user($s->get_customer_id());$v=Imagine\\Site\\MonCompte::donnees();$a=current(array_filter($v['abonnements'],static fn($a)=>$a['id']===$s->get_id()));
$o['counter']=$o['counter']&&$a['restants']!==null;$o['documents']=$o['documents']||$v['factures']!==[];
$o['current_block']=$o['current_block']&&$a['premier']!==null&&$a['dernier']!==null;
if($key==='A-SEPA4'){$o['profile_sepa4']=true;$o['four_states_complete']=array_column($a['echeances'],'etat')===['Payée','Payée','À venir','À venir'];}
if($key==='A-VIR'){$o['native_bacs']=$s->get_payment_method()==='bacs';}
foreach(array_unique([$s->get_parent_id(),...array_values($s->get_related_orders('ids','renewal'))]) as $id){$r=wc_get_order($id);if(!$r||(int)$r->get_customer_id()!==(int)$s->get_customer_id()){continue;}
if($key==='A-SUSP'&&$r->has_status('failed')){$o['failed_order']=true;}
if($key==='A-CARTE'&&$r->is_paid()&&$r->get_date_paid()){$o['carte_paid']=true;}}}
wp_set_current_user(0);echo wp_json_encode($o);''')


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


def shared():
    value = c14.preserve()
    value['bootstrap'] = c14.c10.b00.wp('eval', 'echo hash_file("sha256",WP_PLUGIN_DIR . "/imagine-site/imagine-site.php");')['stdout'].strip()
    value['files'].pop('imagine-site/MonCompte.php', None)
    value['theme'].pop('parts/mon-compte.php', None)
    value['policies'] = [row for row in value['policies'] if not row['option_name'].startswith('imagine_envoi_releve_')]
    return value


def run(deploy=False, http=True):
    PROOF.mkdir(parents=True, exist_ok=True)
    c14.c10.guard()
    before = snapshot()
    journal_before = journal()
    protected = shared()
    result = {'scope': 'imagine-test-demo', 'at': datetime.now(timezone.utc).isoformat(), 'status': 'EN_COURS'}
    def save():
        (PROOF / 'resultats.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    save()
    if deploy:
        # Aucun bootstrap ni functions.php : préserver le C15/B04 installé, même divergent du disque.
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
    result['postal_journal_append_only'] = journal_after == journal_before
    result['postal_observations_added'] = len(added)
    result['closed_and_prior_lots_preserved'] = protected == shared()
    result['snapshot_before'] = before
    result['snapshot_after'] = snapshot()
    result['observations'] = observations()
    result['observations']['address_edit_replayed'] = result.get('http', {}).get('POST_natif_adresse_modifiee_et_relue') is True
    result['acceptance_blockers'] = acceptance_blockers(result['observations'])
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
