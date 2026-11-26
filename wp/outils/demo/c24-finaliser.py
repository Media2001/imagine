"""C24 : sceller les preuves achevées, sans rejouer les mutations acquises."""
import sys
sys.dont_write_bytecode=True
import json,hashlib,os,runpy
from pathlib import Path
import c24

def run():
    m=runpy.run_path(str(c24.ROOT/'wp/tests/demo/c24-http.py'))
    http=json.loads((c24.PROOF/'http-metier-final-V2.json').read_text(encoding='utf-8'))
    private=Path(os.environ['TMPDIR'])/http['private_snapshot']['file']
    assert hashlib.sha256(private.read_bytes()).hexdigest()==http['private_snapshot']['sha256']
    saved=json.loads(private.read_bytes())
    current=m['snapshot'](saved['ids'])
    classes=c24.NAMES[:-1];remote=c24.hashes(classes)
    local={n:hashlib.sha256((c24.ROOT/'wp'/n).read_bytes()).hexdigest() for n in classes}
    bootstrap=c24.wp('echo wp_json_encode(file_get_contents(WP_CONTENT_DIR."/plugins/imagine-site/imagine-site.php"));')
    checks={'snapshot_prive_intact':True,'baseline_metier_preservee':m['business_snapshot'](current)==m['business_snapshot'](saved['snapshot']),'etat_natif_preserve':c24.state()==saved['native'],'sources_produit_installees_exactes':remote==local,'bootstrap_contrat_C24':bootstrap.count(c24.BLOCK)==1 and c24.BLOCK in (c24.ROOT/'wp/plugins/imagine-site/imagine-site.php').read_text(encoding='utf-8'),'observateur_absent':c24.hashes(['mu-plugins/imagine-c24-observer.php'])['mu-plugins/imagine-c24-observer.php'] is None}
    assert all(checks.values()),checks
    c24.save('readback-final-V2',{'identity':c24.guard(),'checks':checks,'failures':[],'baseline':'recovered-new-explicit','historical_initial_snapshot_restored':False,'private_snapshot':http['private_snapshot'],'remote_product_sources':remote})
    files=list((c24.ROOT/'wp/plugins/imagine-site').glob('Personnalisation*.php'))
    files+=list((c24.ROOT/'wp/tests/demo').glob('c24*'))+list((c24.ROOT/'wp/outils/demo').glob('c24*'))
    files+=[c24.PROOF/n for n in ['A-VOIR.md','TRANSMISSION.md','verifier-V2.py']]
    names=['livraison-partielle-V2','recovery-borned-V2','readback-final-V2','http-metier-final-V2','http-requalification-final-V2','mutations-finales-normal-V2','mutations-finales-id-question-V2','mutations-qualifiees-V2','preparation-finale-V2','regression-finale-V2']
    old=json.loads((c24.PROOF/'livraison-partielle-V2.json').read_text(encoding='utf-8'))
    names += [r['receipt'] for r in old['normal_receipts']+old['mutations']]
    latest=json.loads((c24.PROOF/'mutations-qualifiees-V2.json').read_text(encoding='utf-8'))
    names += [r['receipt'] for r in latest['receipts']]
    files += [c24.PROOF/(n+'.json') for n in names]
    files += [c24.PROOF/n for n in ['preparation-finale-V2.log','regression-finale-V2.log','http-metier-final-V2-compte.png','http-metier-final-V2-sans-email.png','http-metier-final-V2-reglages.png']]
    sources={p.relative_to(c24.ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(files)) if p.is_file()}
    normal=[r['receipt'] for r in old['normal_receipts']]+['http-metier-final-V2','mutations-qualifiees-normal-V2']
    positive=sum(json.loads((c24.PROOF/(n+'.json')).read_text(encoding='utf-8'))['total'] for n in normal)
    mutations=old['mutations']+[r for r in latest['receipts'] if r['required_failure']]
    c24.save('manifest-final-V2',{'result':'PASS','pret_eligible':True,'baseline':'recovered-new-explicit','historical_initial_snapshot_restored':False,'visual_approval':False,'production_authorized':False,'sources':sources,'normal_receipts':normal,'positive_checks':positive,'mutations':mutations,'mutation_count':len(mutations),'reused_checks':old['positive_checks'],'fresh_checks':positive-old['positive_checks'],'readback':'readback-final-V2','bootstrap_contract':c24.BLOCK})
    print(json.dumps({'result':'PASS','positive_checks':positive,'mutations':len(mutations),'fresh_checks':positive-old['positive_checks'],'artifacts':len(sources)}))

if __name__=='__main__':run()
