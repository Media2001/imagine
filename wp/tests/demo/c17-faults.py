"""C17 real deletion refusal and simultaneous duplicate-decision gate."""
from pathlib import Path
import sys,json,concurrent.futures
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import c17_http as t

def run():
    t.c17.profils.guard('imagine-test-demo')
    a=json.loads((Path.home()/'.imagine-demo/identifiants.json').read_text())['c09_accounts']
    abo=t.h.login(a['E-ABO']);abo2=t.h.login(a['E-ABO']);owner=t.h.login(a['P-SOL-ATT'])
    uid=t.c17.wp('echo wp_json_encode(get_option("imagine_c09_fixture")["users"]["P-SOL-ATT"]);')
    before=t.c17.state();checks={};source=t.stored(uid);path=source['path'];backup=path+'.c17-owned-backup'
    assert source['exists']
    def disk(code):return t.c17.wp('$p='+json.dumps(path)+';$b='+json.dumps(backup)+';'+code)
    try:
        disk('if(file_exists($b)||!is_file($p)||is_link($p))throw new RuntimeException("Unowned target");if(!rename($p,$b)||!mkdir($p,0700))throw new RuntimeException("Probe setup failed");echo "true";')
        q=t.form(abo,uid)
        s,_,_=t.decision(abo,q)
        checks['decision_si_suppression_impossible_refusee']=s==409
        checks['pas_de_decision_enregistree']=t.stored(uid)['state']==source['state']
        s,_,_=t.upload(owner,t.form(owner),t.dummy_pdf('C17 FICTIF'))
        checks['remplacement_si_suppression_impossible_refuse']=s==409
    finally:
        restored=disk('if(is_dir($p)&&!is_link($p)&&is_file($b)){if(!rmdir($p)||!rename($b,$p))throw new RuntimeException("Probe restoration failed");}echo wp_json_encode(is_file($p)&&!file_exists($b)?hash_file("sha256",$p):false);')
        checks['disque_exactement_restaure']=restored==source['sha256']
    try:
        q=t.form(abo,uid);q2=t.form(abo2,uid)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            futures=[pool.submit(t.decision,client,text) for client,text in [(abo,q),(abo2,q2)]]
            statuses=[f.result()[0] for f in futures]
        checks['decision_concurrente_une_seule_reussite']=sorted(statuses)==[200,409]
        checks['decision_concurrente_disque_supprime']=t.absent(path) and t.stored(uid)['state']['decision']=='valide'
    finally:
        reset=t.c17.reset()
        checks['reset_C09_cible']=reset['P-SOL-ATT']['decision']=='en_attente' and reset['P-SOL-OK']['decision']=='valide'
        checks['etat_commercial_acces_preserve']=t.c17.state()==before
        result={'checks':checks,'total':len(checks),'failures':[k for k,v in checks.items() if v is not True],'concurrent_statuses':statuses,'physical_path_tested':path}
        t.c17.save('faults-final',result);print(json.dumps(result,ensure_ascii=False))
    return int(bool(result['failures']))
if __name__=='__main__':sys.exit(run())
