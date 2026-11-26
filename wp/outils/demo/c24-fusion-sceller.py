"""C24 fusion 20h50 : nouveau sceau, sans réécrire les reçus historiques."""
import sys
sys.dont_write_bytecode=True
import json,hashlib,os,runpy
from pathlib import Path
import c24

def run():
    proof=c24.PROOF
    def read(n):return json.loads((proof/(n+'.json')).read_text(encoding='utf-8'))
    http=read('fusion2050-http-V2')
    private=Path(os.environ['TMPDIR'])/http['private_snapshot']['file']
    assert hashlib.sha256(private.read_bytes()).hexdigest()==http['private_snapshot']['sha256']
    before=json.loads(private.read_bytes())
    m=runpy.run_path(str(c24.ROOT/'wp/tests/demo/c24-http.py'))
    remote=c24.hashes(c24.NAMES[:-1])
    local={n:hashlib.sha256((c24.ROOT/'wp'/n).read_bytes()).hexdigest() for n in c24.NAMES[:-1]}
    checks={'snapshot_prive_intact':True,'metier_exact':m['business_snapshot'](m['snapshot'](before['ids']))==m['business_snapshot'](before['snapshot']),'natif_exact':c24.state()==before['native'],'classes_installees_exactes':remote==local,'observateur_absent':c24.hashes(['mu-plugins/imagine-c24-observer.php'])['mu-plugins/imagine-c24-observer.php'] is None}
    assert all(checks.values()),checks
    c24.save('fusion2050-readback-V2',{'checks':checks,'failures':[],'private_snapshot':http['private_snapshot'],'remote_product_sources':remote})
    normal=['fusion2050-'+n+'-V2' for n in ['rules','runtime','http','gardes-normal','final-question','final-choix','final-newsletter']]
    mutations=read('fusion2050-historiques-V2')['receipts']+[r for r in read('fusion2050-gardes-V2')['receipts'] if r['required_failure']]
    mutations += [{'receipt':'fusion2050-final-mut-'+n+'-V2','required_failure':f,'test':'wp/tests/demo/c24-corrections.php'} for n,f in [('question','preimage_restauree_exacte'),('choix','preimage_restauree_exacte'),('origine','origine_defaut_creation')]]
    mutations += [{'receipt':'fusion2050-mut-c10-V2','required_failure':'C10_vraie_section_entre_ouverture_et_fermeture','test':'wp/tests/demo/c24-http.py','http_mutation':True}]
    total=sum(read(n)['total'] for n in normal)
    files=[c24.ROOT/'wp'/n for n in c24.NAMES[:-1]]
    files+=list((c24.ROOT/'wp/tests/demo').glob('c24*'))+list((c24.ROOT/'wp/outils/demo').glob('c24*'))
    files+=[proof/n for n in ['A-VOIR.md','TRANSMISSION.md','README-C24-section.md','verifier-fusion2050-V2.py']]
    files+=list(proof.glob('fusion2050-*.json'))+list(proof.glob('fusion2050-*.log'))+list(proof.glob('fusion2050-*.png'))
    files += [proof/'manifest-final-V2.json',proof/'recovery-borned-V2.json']
    sources={p.relative_to(c24.ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(files)) if p.is_file()}
    c24.save('manifest-fusion2050-V2',{'result':'PASS','pret_eligible':True,'baseline':'recovered-new-explicit','historical_initial_snapshot_restored':False,'production_authorized':False,'visual_approval':False,'sources':sources,'normal_receipts':normal,'positive_checks':total,'mutations':mutations,'mutation_count':len(mutations),'readback':'fusion2050-readback-V2','http':'fusion2050-http-V2','prepare':'fusion2050-preparation-V2','regression':'fusion2050-regression-V2','suite':read('fusion2050-regression-V2')['result'],'README_contract':'production/C-24/README-C24-section.md'})
    print(json.dumps({'result':'PASS','positive_checks':total,'mutations':len(mutations),'artifacts':len(sources)}))

if __name__=='__main__':run()
