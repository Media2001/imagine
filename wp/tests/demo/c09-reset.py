"""C09 : altération contrôlée puis reset réel, jamais hors des objets C09."""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import profils


def run():
    profils.guard('imagine-test-demo')
    root = profils.b00.ROOT
    baseline = json.loads((root / 'production/C-09/installation.json').read_text(encoding='utf-8'))['native']['fixture']
    mutation = '''$f=get_option("imagine_c09_fixture");$out=[];
foreach($f["users"] as $key=>$id){if(get_user_meta($id,"_imagine_c09_fixture",true)!==$key)throw new RuntimeException("Propriété absente");
$u=new WP_User($id);$u->set_role("subscriber");$u->add_cap("manage_options");wp_update_user(["ID"=>$id,"user_email"=>strtolower($key)."-modifie@example.org"]);wp_set_password(wp_generate_password(40,true,true),$id);}
foreach($f["orders"] as $id){$o=wc_get_order($id);$o->remove_order_items();$o->set_status("pending");$o->save();}
foreach($f["subscriptions"] as $id){$s=wcs_get_subscription($id);$s->set_status("on-hold");$s->set_billing_interval(2);$s->save();}
foreach($f["memberships"] as $id){$m=wc_memberships_get_user_membership($id);$m->update_status("cancelled");delete_post_meta($id,"_subscription_id");}
$id=$f["users"]["A-CARTE"];$o=wc_create_order(["customer_id"=>$id,"status"=>"pending"]);$o->update_meta_data("_imagine_c09_fixture","A-CARTE");$o->save();$out["duplicate_order"]=$o->get_id();
$s=wcs_create_subscription(["customer_id"=>$id,"status"=>"pending","billing_period"=>"year","billing_interval"=>1]);if(is_wp_error($s))throw new RuntimeException("Duplicata natif impossible");$s->set_requires_manual_renewal(true);$s->update_meta_data("_imagine_c09_fixture","A-CARTE");$s->save();$out["duplicate_subscription"]=$s->get_id();
$m=wc_memberships_create_user_membership(["user_id"=>$id,"plan_id"=>$f["plan"]]);if(!is_wp_error($m)){$out["duplicate_membership"]=$m->get_id();update_post_meta($m->get_id(),"_imagine_c09_fixture","A-CARTE");}
// Objet additionnel possédé sur un profil qui ne doit rien avoir au départ.
$o=wc_create_order(["customer_id"=>$f["users"]["V-INSCRIT"],"status"=>"pending"]);$o->update_meta_data("_imagine_c09_fixture","V-INSCRIT");$o->save();$out["unexpected_owned_order"]=$o->get_id();
echo wp_json_encode($out);'''
    changed = json.loads(profils.b00.wp('eval', mutation)['stdout'])
    red = profils.b00.wp('eval', 'require WP_CONTENT_DIR . "/imagine-demo-build/c09-runtime.php";', check=False)
    red_data = json.loads(red['stdout'])
    (root / 'production/C-09/red-reset.json').write_text(json.dumps({'mutation': changed, 'exit': red['code'], 'runtime': red_data}, ensure_ascii=False, indent=2), encoding='utf-8')
    if red['code'] != 1 or not red_data['failures']:
        raise RuntimeError('La recette ne détecte pas les états altérés')
    record = profils.run(label='reset')
    checks = {'alterations_detectees': bool(red_data['failures']), 'ids_principaux_conserves': record['native']['fixture'] == baseline,
              'preservation_c08_b00': record['preserved_b00_c08'], 'aucun_doublon': not record['native']['failures']}
    result = {'total': len(checks), 'checks': checks, 'failures': [k for k,v in checks.items() if not v],
              'mutation': changed, 'red_failure_count': len(red_data['failures'])}
    (root / 'production/C-09/reset-preuve.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))
    if result['failures']:
        raise RuntimeError('Reset non vérifié')


if __name__ == '__main__':
    run()
