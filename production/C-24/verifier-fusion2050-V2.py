"""Vérification C24 fusion 20h50 hors réseau et sans client de site."""
import sys
sys.dont_write_bytecode=True
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PROOF=ROOT/'production/C-24'
count=0

def check(value,name):
    global count
    count+=1
    assert value,name

def read(name):return json.loads((PROOF/(name+'.json')).read_text(encoding='utf-8'))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    path=Path(sys.argv[1]) if len(sys.argv)>1 else PROOF/'manifest-fusion2050-V2.json'
    m=json.loads(path.read_text(encoding='utf-8'))
    check(m['scope']=='imagine-test-demo' and m['result']=='PASS' and m['pret_eligible'] is True,'verdict')
    check(m['baseline']=='recovered-new-explicit' and m['historical_initial_snapshot_restored'] is False,'historique')
    check(m['production_authorized'] is False and m['visual_approval'] is False,'pas de GO')
    for name,sha in m['sources'].items():
        check(name.startswith(('wp/plugins/imagine-site/Personnalisation','wp/tests/demo/c24','wp/outils/demo/c24','production/C-24/')) and '..' not in Path(name).parts,'périmètre')
        check(digest(ROOT/name)==sha,'empreinte '+name)
    section=(ROOT/m['README_contract']).read_text(encoding='utf-8').strip()
    readme=(ROOT/'wp/plugins/imagine-site/README.md').read_text(encoding='utf-8')
    check(readme.count(section)==1,'README contrat C24')
    total=0
    for name in m['normal_receipts']:
        r=read(name)
        check(r['scope']=='imagine-test-demo' and not r['failures'] and r.get('exit',0)==0 and r.get('error') is None and not r.get('stderr',''),'nominal '+name)
        check(r['total']==len(r['checks'])>0 and all(v is True for v in r['checks'].values()),'contrôles '+name)
        check(r.get('state_preserved',True) is True and r.get('all_business_rows_preserved',True) is True,'restauration '+name)
        if 'product_sources' in r:
            check(all(digest(ROOT/'wp'/n)==sha for n,sha in r['product_sources'].items()),'produit '+name)
        total+=r['total']
    check(total==m['positive_checks']==148,'total nominal')
    for item in m['mutations']:
        r=read(item['receipt'])
        check(item['required_failure'] in r['failures'],'mutation '+item['receipt'])
        if item.get('http_mutation'):
            check(r['restored'] is True and r['error'].startswith('AssertionError: Section absente'),'C10 absence réelle/restauration')
        else:
            check(r['exit']==1 and not r['stderr'] and r['state_preserved'] is True and r.get('all_business_rows_preserved',True) is True,'mutation propre/restaurée')
            if r.get('mutation') in ['restauration','origine','id-question','id-choix','consentement','newsletter','email']:
                check(r['mutation_replacements']==1,'vraie mutation source')
        test=item.get('test') or ('wp/tests/demo/c24-mutations.php' if 'gardes-' in item['receipt'] else 'wp/tests/demo/c24-runtime.php')
        check(r['source_sha256']==digest(ROOT/test),'source mutant '+item['receipt'])
    check(len(m['mutations'])==m['mutation_count']==16,'total mutants')
    for case in ['question','choix']:
        r=read('fusion2050-scratch-final-'+case+'-V2')
        check(r['journal_inserts_refused']==1 and r['dies']==[] and r['checks']['preimage_restauree_exacte'] and r['checks']['readback_SQL_preimage_exacte'],'journal réel '+case)
    nl=read('fusion2050-scratch-final-newsletter-V2')
    check(nl['checks']['vraie_creation_newsletter_defaut'] and nl['checks']['vraie_creation_defaut_projection_fermee'] and nl['checks']['origine_lecteur'],'création newsletter et lecteur')
    h=read(m['http'])
    check(h['source_sha256']==digest(ROOT/'wp/tests/demo/c24-http.py'),'source HTTP')
    check(h['restored'] is True and h['mail_attempts']==0 and h['http_attempts']==h['http_blocked'] and h['observed_requests']>20,'HTTP sans envoi/restauré')
    for c in ['C10_vraie_section_entre_ouverture_et_fermeture','C10_insertion_sous_bouton_existante','journal_question_POST_reel_sans500','journal_choix_POST_reel_sans500','journal_refus_SQL_deux_parcours']:
        check(h['checks'][c] is True,c)
    rb=read(m['readback'])
    check(not rb['failures'] and all(rb['checks'].values()) and rb['private_snapshot']==h['private_snapshot'],'readback durable final')
    check(all(digest(ROOT/'wp'/n)==sha for n,sha in rb['remote_product_sources'].items()),'installation produit')
    for name in [m['prepare'],m['regression']]:
        r=read(name)
        check(r['exit']==0 and not r['failures'] and all(r['checks'].values()),'porte '+name)
        check(digest(PROOF/r['log'])==r['log_sha256'],'log '+name)
    suite=read(m['regression'])['result']
    check(suite==m['suite'] and suite['pass'] is True and suite['tests']==1128 and suite['assertions']==35565 and all(suite[k]==0 for k in ['failures','errors','skipped']),'suite complète')
    check(suite['tools']=={'tools':16,'checks':331,'failures':0,'excluded':[]},'outils complets')
    check(read('recovery-borned-V2')['exact_initial_snapshot_restored'] is False,'incident conservé')
    for name in ['fusion2050-red-question2-V2','fusion2050-red-choix-V2','fusion2050-red-newsletter-V2']:
        r=read(name);check(r['exit']==1 and bool(r['failures']) and r['state_preserved'] is True,'TDD RED réel')
    print(json.dumps({'result':'PASS','checks':count,'positive_checks':total,'detected_mutations':len(m['mutations']),'PRET_eligible':True},ensure_ascii=False))

if __name__=='__main__':
    try:main()
    except Exception as exc:
        print(json.dumps({'result':'FAIL','checks':count,'error':str(exc)},ensure_ascii=False));sys.exit(1)
