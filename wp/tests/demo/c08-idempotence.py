"""Rejeu réel du seed C08 : mêmes IDs, contenus et objets natifs, zéro doublon."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import c08


def state():
    code = '''$f=get_option('imagine_c08_fixture');$out=['fixture'=>$f,'articles'=>[],'subscriptions'=>[],'counts'=>[]];
foreach(['article','automatique'] as $k){$p=get_post($f[$k]);$out['articles'][$k]=['id'=>$p->ID,'hash'=>hash('sha256',$p->post_content . $p->post_excerpt),'numero'=>get_post_meta($p->ID,'imagine_numero_id',true)];}
foreach($f['subscriptions'] as $k=>$id){$s=wcs_get_subscription($id);$out['subscriptions'][$k]=['id'=>$id,'user'=>$s->get_customer_id(),'status'=>$s->get_status(),'start'=>$s->get_date('start'),'end'=>$s->get_date('end'),'manual'=>$s->is_manual(),'gateway'=>$s->get_payment_method(),'grace'=>$s->get_meta('_imagine_acces_grace_fin')];}
$out['counts']['articles']=count(get_posts(['post_type'=>'post','numberposts'=>-1,'post_status'=>'any','meta_key'=>'imagine_c08_fixture']));
$out['counts']['plans']=count(get_posts(['post_type'=>'wc_membership_plan','numberposts'=>-1,'post_status'=>'any','name'=>'c08-lecture-fictive']));
$out['counts']['users']=count(get_users(['login__in'=>['imagine-c08-actif','imagine-c08-grace','imagine-c08-sans-droit']]));
$out['counts']['memberships']=0;$out['counts']['subscriptions']=0;
foreach($f['users'] as $id){foreach(wc_memberships_get_user_memberships($id) ?? [] as $m){if($m->get_plan_id()===$f['plan']){$out['counts']['memberships']++;}}foreach(wcs_get_users_subscriptions($id) as $s){if($s->get_meta('_imagine_c08_fixture')){$out['counts']['subscriptions']++;}}}
echo wp_json_encode($out);'''
    return json.loads(c08.b00.wp('eval', code)['stdout'])


def run():
    c08.guard()
    before = state()
    c08.run(seed=True)
    after = state()
    checks = {'same_native_state_after_replay': before == after,
              'exact_counts_no_duplicates': after['counts'] == {'articles': 2, 'plans': 1, 'users': 3, 'memberships': 2, 'subscriptions': 2},
              'no_gateway': all(s['gateway'] == '' for s in after['subscriptions'].values()),
              'only_manual_subscriptions': all(s['manual'] for s in after['subscriptions'].values())}
    failures = [k for k, ok in checks.items() if not ok]
    record = {'scope': c08.b00.SLUG, 'total': len(checks), 'passed': len(checks)-len(failures), 'failures': failures,
              'checks': checks, 'before': before, 'after': after}
    (c08.PROOF / 'idempotence.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: record[k] for k in ['total', 'passed', 'failures']}, ensure_ascii=False))
    if failures:
        raise SystemExit(1)


if __name__ == '__main__':
    run()
