"""Recette native C27, préimage et inverses relues, site fictif unique."""
import sys
sys.dont_write_bytecode = True
import json
import hashlib
import os
from pathlib import Path
import c27


def compare(saved, current):
    names=['users','usermeta','posts','postmeta','comments','commentmeta','navigation','wc_orders','wc_orders_meta','wc_order_addresses','wc_order_operational_data','woocommerce_order_items','woocommerce_order_itemmeta','actionscheduler_actions','actionscheduler_logs','actionscheduler_groups','actionscheduler_claims']
    exact={k:saved.get(k)==current.get(k) for k in names}
    opts=lambda db:[r for r in db['options'] if r['option_name'].startswith('imagine_') or r['option_name']=='cron']
    exact['options_metier']=opts(saved)==opts(current)
    return exact


def restore_options(saved):
    # Seuls les réglages/journaux/observations C27 nés dans la recette sont concernés.
    prior={r['option_name']:r for r in saved['options']}
    current=c27.wp('global $wpdb;echo wp_json_encode($wpdb->get_results("SELECT * FROM {$wpdb->options}",ARRAY_A));')
    owned=[]
    for row in current:
        key=row['option_name']
        if key.startswith('imagine_acquisition_') or key=='imagine_c27_observations':
            owned.append(key)
        elif key.startswith('imagine_reglages_journal_') and key not in prior:
            event=c27.wp('echo wp_json_encode(get_option('+c27.php(key)+'));')
            if isinstance(event,dict) and event.get('option')=='imagine_acquisition_choix': owned.append(key)
    original=[r for k,r in prior.items() if k in owned or k.startswith('imagine_acquisition_')]
    c27.wp('global $wpdb;foreach('+c27.php(owned)+' as $key){$wpdb->delete($wpdb->options,["option_name"=>$key]);}foreach('+c27.php(original)+' as $row){$wpdb->replace($wpdb->options,$row);}wp_cache_flush();echo wp_json_encode(true);')


def restore_users(saved, ids):
    rows=[r for r in saved['usermeta'] if int(r['user_id']) in ids]
    c27.wp('global $wpdb;foreach('+c27.php(list(ids))+' as $id){$wpdb->delete($wpdb->usermeta,["user_id"=>$id]);}foreach('+c27.php(rows)+' as $row){$wpdb->insert($wpdb->usermeta,$row);}wp_cache_flush();echo wp_json_encode(true);')


def restore_order_edges(saved, ids):
    """C16 garde des adresses classiques en HPOS ; les seuls IDs créés sont nettoyés.

    Le rapport Subscriptions natif invalide une tâche de cache à la lecture de C16.
    Inverse ciblée avec comparaison de toutes les colonnes ; pas de reset global.
    """
    assert not any(int(r['ID']) in ids for r in saved['posts'])
    assert not any(int(r['id']) in ids for r in saved['wc_orders'])
    c27.wp('global $wpdb;foreach('+c27.php(list(ids))+' as $id){if(wc_get_order($id)){throw new RuntimeException("Commande non supprimée");}$wpdb->delete($wpdb->postmeta,["post_id"=>$id]);}echo wp_json_encode(true);')
    current=c27.snapshot()
    old={r['action_id']:r for r in saved['actionscheduler_actions']}
    now={r['action_id']:r for r in current['actionscheduler_actions']}
    changed={k for k in old.keys()|now.keys() if old.get(k)!=now.get(k)}
    for key in changed:
        for row in [old.get(key),now.get(key)]:
            if row is None:continue
            assert row['hook']=='wcs_report_update_cache' and row['args']=='{"report_class":"WCS_Report_Subscription_By_Product"}' and row['status'] in ['pending','canceled'] and row['attempts']=='0' and row['claim_id']=='0', 'Dérive action étrangère'
    before_logs={r['log_id']:r for r in saved['actionscheduler_logs']}
    after_logs={r['log_id']:r for r in current['actionscheduler_logs']}
    logids={k for k in before_logs.keys()|after_logs.keys() if before_logs.get(k)!=after_logs.get(k)}
    assert all(after_logs[k]['action_id'] in changed and k not in before_logs for k in logids), 'Dérive journal étrangère'
    targets=[('actionscheduler_logs','log_id',logids,before_logs,after_logs),('actionscheduler_actions','action_id',changed,old,now)]
    for table,pk,keys,before,after in targets:
        payload=[{'before':before.get(k),'after':after.get(k)} for k in keys]
        c27.wp('global $wpdb;$table=$wpdb->prefix.'+c27.php(table)+';foreach('+c27.php(payload)+' as $pair){$old=$pair["before"];$now=$pair["after"];if($now!==null&&$wpdb->delete($table,$now)!==1){throw new RuntimeException("Dérive pendant inverse");}if($old!==null&&$wpdb->insert($table,$old)!==1){throw new RuntimeException("Inverse action refusée");}}echo wp_json_encode(true);')


def run(label):
    identity=c27.guard();saved=c27.snapshot();before=c27.state()
    durable=c27.private('c27-'+label,{'database':saved,'business':before})
    name='imagine-demo-build/c27-runtime.php'
    assert c27.wp('echo wp_json_encode(file_exists(WP_CONTENT_DIR."/'+name+'"));') is False
    outcome={};cleanup={}
    try:
        c27.upload(name,(c27.ROOT/'wp/tests/demo/c27-runtime.php').read_bytes())
        result=c27.wp('require WP_CONTENT_DIR."/'+name+'";')
        outcome.update(result)
    finally:
        for key,fn in [('options',lambda:restore_options(saved)),('profils',lambda:restore_users(saved,{28})),('runner',lambda:c27.b09.remove_remote([name]))]:
            try: fn();cleanup[key]=True
            except Exception as e: cleanup[key]=False;outcome[key+'_error']=type(e).__name__+': '+str(e)
        exact=compare(saved,c27.snapshot());preserved=before==c27.state()
        c27.save(label,{**outcome,'identity':identity,'private_snapshot':durable,'cleanup':cleanup,'restoration':exact,'business_preserved':preserved})
        print(json.dumps({**outcome,'cleanup':cleanup,'restoration':exact,'business_preserved':preserved},ensure_ascii=False))
        assert all(cleanup.values()) and all(exact.values()) and preserved
    assert result['checks'] and all(result['checks'].values())


if __name__=='__main__': run(sys.argv[1])
