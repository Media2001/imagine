"""C13 : cible unique, pas de reset, secrets hors dépôt, preuves proportionnées."""
import argparse
import base64
import importlib.util
import json
from pathlib import Path
import c10

ROOT = c10.ROOT
FILES = ['plugins/imagine-site/EnvoiRegles.php', 'plugins/imagine-site/EnvoiRelations.php',
         'plugins/imagine-site/EnvoiNatif.php', 'plugins/imagine-site/ListeEnvoiAdmin.php']


def upload(rel, source):
    data = source.read_bytes()
    c10.b00.upload(rel, data)
    out = c10.b00.wp('eval', '$p=WP_CONTENT_DIR . ' + json.dumps('/' + rel) + ';token_get_all(file_get_contents($p),TOKEN_PARSE);echo base64_encode(file_get_contents($p));')
    if out['stderr'] or out['stdout'].strip() != base64.b64encode(data).decode():
        raise RuntimeError('Relecture différente : ' + rel)


def runtime():
    upload('imagine-demo-build/c13-runtime.php', ROOT / 'wp/tests/demo/c13-runtime.php')
    out = c10.b00.wp('eval', 'require WP_CONTENT_DIR . "/imagine-demo-build/c13-runtime.php";', check=False)
    if out['code'] or out['stderr']:
        raise RuntimeError('Recette PHP C13 : ' + out['stderr'])
    checks = json.loads(out['stdout'])
    upload('imagine-demo-build/c13-corrections-runtime.php', ROOT / 'wp/tests/demo/c13-corrections-runtime.php')
    extra = c10.b00.wp('eval', 'require WP_CONTENT_DIR . "/imagine-demo-build/c13-corrections-runtime.php";', check=False)
    if extra['code'] or extra['stderr']:
        raise RuntimeError('Recette corrections PHP C13 : ' + str(extra))
    checks.update({'correction_' + k: v for k, v in json.loads(extra['stdout']).items()})
    print(json.dumps({'PHP': checks}, ensure_ascii=False))
    if not checks or not all(v is True for v in checks.values()):
        raise RuntimeError('Assertions C13 rouges')
    return checks


def protege():
    code = r'''global $wpdb;$out=[];$keys=['imagine_c08_fixture','imagine_c09_fixture','imagine_demo_manifest','imagine_demo_calendrier','imagine_acces_plans','imagine_acces_reglages','imagine_c05_reglages','imagine_envoi_colonnes_export','imagine_decouverte_reglages'];foreach($keys as $k){$out['options'][$k]=get_option($k,null);}$out['roles']=wp_roles()->roles;$f=get_option('imagine_c09_fixture');foreach($f['users'] as $k=>$id){$u=get_userdata($id);$out['users'][$k]=[$u->ID,$u->user_login,$u->user_email,$u->roles,$u->caps];}foreach($f['subscriptions'] as $k=>$id){$s=wcs_get_subscription($id);$out['subscriptions'][$k]=$s->get_data();}foreach($f['memberships'] as $k=>$id){$m=wc_memberships_get_user_membership($id);$out['memberships'][$k]=[$m->get_status(),$m->get_user_id(),$m->get_plan_id(),$m->get_start_date(),$m->get_end_date('mysql',false),get_post_meta($id,'_subscription_id',true)];}$out['editorial']=$wpdb->get_results("SELECT ID,post_title,post_content,post_excerpt,post_status,post_password FROM {$wpdb->posts} WHERE post_type IN ('post','imagine_numero') ORDER BY ID",ARRAY_A);echo wp_json_encode($out);'''
    r = c10.b00.wp('eval', code)
    if r['stderr']:
        raise RuntimeError('Lecture de protection C13 non propre')
    return json.loads(r['stdout'])


def run(deploy=False, php_only=False, require_complete=False):
    spec = importlib.util.spec_from_file_location('c13_unit', ROOT / 'wp/outils/demo/c13-unit.py')
    unit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(unit)
    pure = unit.run()
    _, before = c10.guard()  # Sonde read-only avant toute mutation de la cible.
    protected = protege()
    if deploy:
        for rel in FILES:
            upload(rel, ROOT / 'wp' / rel)
        upload('imagine-demo-build/c13-fixture.php', ROOT / 'wp/outils/demo/c13-fixture.php')
        seed = c10.b00.wp('eval', '(static function(){require WP_CONTENT_DIR . "/imagine-demo-build/c13-fixture.php";})();')
        if seed['stderr']:
            raise RuntimeError('Avertissement à l’initialisation C13')
        print('Témoins natifs C13 relus :', seed['stdout'].strip())
    for rel in FILES:
        actual = c10.b00.wp('eval', 'echo base64_encode(file_get_contents(WP_CONTENT_DIR . ' + json.dumps('/' + rel) + '));')['stdout'].strip()
        if actual != base64.b64encode((ROOT / 'wp' / rel).read_bytes()).decode():
            raise RuntimeError('Code installé différent des sources : ' + rel)
    checks = {'pur': pure, 'PHP': runtime()}
    checks['sources_installees_conformes'] = True
    if not php_only:
        path = ROOT / 'wp/tests/demo/c13-http.py'
        spec = importlib.util.spec_from_file_location('c13_http', path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        checks['HTTP'] = mod.verify()
        checks['manifestes_preserves'] = before == c10.guard()[1]
        checks['C09_roles_options_editorial_preserves'] = protected == protege()
        if not checks['manifestes_preserves'] or not checks['C09_roles_options_editorial_preserves']:
            raise RuntimeError('État protégé différent')
        gate_code = r'''$f=get_option('imagine_c09_fixture');$v=Imagine\Site\EnvoiNatif::apercu('DEMO-2027-T1');$included=array_column($v['liste']->lignes,'abonnement_id');$excluded=array_column($v['exclus'],'motif','abonnement_id');$out=['numero'=>'DEMO-2027-T1','abonnements_C09'=>count($f['subscriptions']),'sans_paiement_valide'=>0,'C09_destinataires'=>0,'A_SANSMAIL_inclus'=>in_array((string)$f['subscriptions']['A-SANSMAIL'],$included,true),'A_SANSMAIL_motif'=>$excluded[(string)$f['subscriptions']['A-SANSMAIL']]??null,'offert_natif_present'=>isset($f['subscriptions']['P-OFFERT']),'groupe_natif_present'=>isset($f['subscriptions']['P-BENEF'])];foreach($f['subscriptions'] as $id){$s=wcs_get_subscription($id);$out['sans_paiement_valide']+=!$s->get_date_paid()?1:0;$out['C09_destinataires']+=in_array((string)$id,$included,true)?1:0;}echo wp_json_encode($out);'''
        gate = c10.b00.wp('eval', gate_code)
        if gate['stderr']:
            raise RuntimeError('Lecture du blocage C09 non propre')
        checks['acceptation_C09'] = json.loads(gate['stdout'])
        checks['recette_complete'] = all(checks['PHP'].values()) and all(checks['HTTP'].values()) and all(
            checks['acceptation_C09'][k] for k in ('A_SANSMAIL_inclus', 'offert_natif_present', 'groupe_natif_present'))
        checks['statut'] = 'BLOQUE_ACCEPTATION_C09' if not checks['recette_complete'] else 'PRET_RELECTURE'
        (ROOT / 'production/C-13/resultats.json').write_text(json.dumps(checks, ensure_ascii=False, indent=2), encoding='utf-8')
        print('C13 :', len(checks['PHP']) + len(checks['HTTP']), 'assertions PHP/HTTP ; manifestes préservés')
        print('Acceptation C09 :', json.dumps(checks['acceptation_C09'], ensure_ascii=False), '; recette complète :', checks['recette_complete'])
        if require_complete and not checks['recette_complete']:
            raise SystemExit(2)
    return checks


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--deploy', action='store_true')
    parser.add_argument('--php-only', action='store_true')
    parser.add_argument('--require-complete', action='store_true', help='Exit 2 si une exigence C09 reste bloquée, même avec les tests techniques verts')
    args = parser.parse_args()
    if args.php_only and args.require_complete:
        parser.error('--require-complete exige le rejeu complet')
    run(args.deploy, args.php_only, args.require_complete)
