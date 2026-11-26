"""Récupération bornée du seul rejeu interrompu matrice-finale (pas un lanceur courant)."""
import sys
sys.dont_write_bytecode=True
import json,hashlib
from pathlib import Path
import importlib.util
TOOLS=Path(__file__).resolve().parents[2]/'outils/demo'
sys.path.insert(0,str(TOOLS))
spec=importlib.util.spec_from_file_location('prep',TOOLS/'c23-preparer.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
p.profils.guard('imagine-test-demo')
start=int((p.PROOF/'mutation-rouge-restauration.json').stat().st_mtime)
end=int((p.PROOF/'matrice-finale.json').stat().st_mtime)
inspect='''$out=[];foreach([8,7,28,9] as $id){$s=get_user_meta($id,'session_tokens',true);$out[$id]=array_map(static fn($v)=>['login'=>$v['login'],'expiration'=>$v['expiration']],array_values(is_array($s)?$s:[]));}echo wp_json_encode($out);'''
print(json.dumps({'start':start,'end':end,'sessions_dates_only':p.wp(inspect)},indent=2))
if sys.argv[1:]==['--apply']:
    result=p.wp('''$start='''+str(start)+''';$end='''+str(end)+''';$removed=[];
foreach([8,7,28,9] as $id){$sessions=get_user_meta($id,'session_tokens',true);$keep=[];$n=0;
foreach($sessions as $key=>$value){if($value['login']>=$start && $value['login']<=$end && $value['expiration']-$value['login']===7200){$n++;}else{$keep[$key]=$value;}}
if($n!==1){throw new RuntimeException('C23 récupération ambiguë.');}
if($keep){update_user_meta($id,'session_tokens',$keep);}else{delete_user_meta($id,'session_tokens');}$removed[$id]=$n;}
delete_option('imagine_decouverte_reglages');delete_option('imagine_decouverte_relecture');echo wp_json_encode($removed);''')
    state=p.b05.state()
    digest=hashlib.sha256(json.dumps(state,sort_keys=True).encode()).hexdigest()
    assert digest=='4d81b43e4958a067678b12bfe1fbf6d57f83dcd382f92404a457e5850a935351'
    after=p.wp(inspect)
    assert all(not (start<=r['login']<=end and r['expiration']-r['login']==7200) for rows in after.values() for r in rows)
    record={'scope':'imagine-test-demo','interrupted_receipt':'matrice-finale','sessions_removed_counts':result,
        'business_native_state_restored_sha256':digest,'scheduled_action_restored':state['schedule_business'],
        'all_interrupted_sessions_removed':True,'policy_absent_restored':True,
        'limit':'Session antérieure expirée éventuellement purgée par WordPress non reconstituable sans le snapshot mémoire perdu ; aucun droit natif ni action planifiée modifié.'}
    (p.PROOF/'recuperation-timeout.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    print('C23 récupération bornée : état métier initial retrouvé et quatre sessions interrompues révoquées.')
