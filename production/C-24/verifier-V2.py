"""Vérificateur C24 hors réseau, lecture seule ; aucun import de client staging."""
import sys
sys.dont_write_bytecode=True
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PROOF=ROOT/'production/C-24'
count=0

def check(value,message):
    global count
    count+=1
    assert value,message

def read(name):return json.loads((PROOF/(name+'.json')).read_text(encoding='utf-8'))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    path=Path(sys.argv[1]) if len(sys.argv)>1 else PROOF/'manifest-final-V2.json'
    manifest=json.loads(path.read_text(encoding='utf-8'))
    check(manifest['scope']=='imagine-test-demo' and manifest['result']=='PASS' and manifest['pret_eligible'] is True,'périmètre/verdict')
    check(manifest['baseline']=='recovered-new-explicit' and manifest['historical_initial_snapshot_restored'] is False,'baseline historique')
    check(manifest['visual_approval'] is False and manifest['production_authorized'] is False,'absence de GO')
    for name,wanted in manifest['sources'].items():
        allowed=name.startswith(('wp/outils/demo/c24','wp/tests/demo/c24','wp/plugins/imagine-site/Personnalisation','production/C-24/'))
        check(allowed and '..' not in Path(name).parts,'hors lot : '+name)
        check(digest(ROOT/name)==wanted,'empreinte : '+name)
    initial=read('livraison-partielle-V2')
    unchanged=[p for p in initial['sources'] if p.startswith('wp/plugins/imagine-site/Personnalisation') or p in ['wp/tests/demo/c24-rules.php','wp/tests/demo/c24-runtime.php']]
    check(len(unchanged)==6,'périmètre de réemploi')
    for name in unchanged:check(digest(ROOT/name)==initial['sources'][name],'réemploi invalide : '+name)
    total=0
    for name in manifest['normal_receipts']:
        r=read(name)
        check(r['scope']=='imagine-test-demo' and not r['failures'],'nominal rouge : '+name)
        check(len(r['checks'])==r['total'] and all(v is True for v in r['checks'].values()),'nominal vide/incohérent : '+name)
        check(r.get('exit',0)==0 and r.get('error') is None and r.get('stderr','')=='','sortie nominale : '+name)
        total+=r['total']
    check(total==manifest['positive_checks']==110,'total nominal')
    check(manifest['reused_checks']==64 and manifest['fresh_checks']==46,'réemploi/frais')
    for item in manifest['mutations']:
        r=read(item['receipt'])
        check(r['exit']==1 and item['required_failure'] in r['failures'],'mutation non détectée : '+item['receipt'])
        check(r['state_preserved'] is True and r.get('all_business_rows_preserved',True) is True and not r['stderr'],'mutation non restaurée')
        check(r['source_sha256']==digest(ROOT/('wp/tests/demo/c24-mutations.php' if 'mutations-qualifiees' in item['receipt'] else 'wp/tests/demo/c24-runtime.php')),'source de mutation')
        if 'mutations-qualifiees' in item['receipt']:check(r['mutation_replacements']==1,'mutation source non exercée')
    check(len(manifest['mutations'])==manifest['mutation_count']==12,'total mutations')
    h=read('http-metier-final-V2')
    check(h['source_sha256']==digest(ROOT/'wp/tests/demo/c24-http.py'),'source HTTP')
    check(h['restored'] is True and h['mail_attempts']==0 and h['http_attempts']==h['http_blocked'] and h['observed_requests']>20,'HTTP/sorties/restauration')
    check(h['private_snapshot']['retained'] is True and len(h['private_snapshot']['sha256'])==64,'snapshot durable')
    rb=read(manifest['readback'])
    check(not rb['failures'] and all(rb['checks'].values()) and rb['private_snapshot']==h['private_snapshot'],'readback final')
    for name,wanted in rb['remote_product_sources'].items():check(wanted==digest(ROOT/'wp'/name),'source installée différente')
    bootstrap=(ROOT/'wp/plugins/imagine-site/imagine-site.php').read_text(encoding='utf-8')
    check(bootstrap.count(manifest['bootstrap_contract'])==1,'contrat additif bootstrap')
    recovery=read('recovery-borned-V2')
    check(recovery['exact_initial_snapshot_restored'] is False,'incident historique effacé')
    for name in ['preparation-finale-V2','regression-finale-V2']:
        r=read(name)
        check(r['exit']==0 and not r['failures'] and all(r['checks'].values()),'porte commune rouge')
        check(digest(PROOF/r['log'])==r['log_sha256'],'journal porte commune')
    suite=read('regression-finale-V2')['result']
    check(suite['pass'] is True and suite['tests']==1126 and suite['assertions']==35550 and all(suite[k]==0 for k in ['failures','errors','skipped']) and suite['tools']=={'tools':16,'checks':311,'failures':0,'excluded':[]},'bilan régression')
    # Le rouge et le mutant masqué intermédiaires restent des faits historiques.
    check(bool(read('http-requalification-final-V2')['failures']),'rouge intermédiaire disparu')
    check(read('mutations-finales-id-question-V2')['exit']==0,'mutant masqué historique réécrit')
    print(json.dumps({'result':'PASS','checks':count,'positive_checks':total,'detected_mutations':len(manifest['mutations']),'PRET_eligible':True,'historical_initial_snapshot_restored':False},ensure_ascii=False))

if __name__=='__main__':
    try:main()
    except Exception as exc:
        print(json.dumps({'result':'FAIL','checks':count,'error':str(exc)},ensure_ascii=False));sys.exit(1)
