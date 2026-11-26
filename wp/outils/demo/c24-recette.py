"""Recette C24 partielle : règles/natif/mutations ; le premier HTTP reste bloquant."""
import sys
sys.dont_write_bytecode=True
import json,hashlib
from pathlib import Path
import c24

def sources():
    files=list((c24.ROOT/'wp/plugins/imagine-site').glob('Personnalisation*.php'))
    files += list((c24.ROOT/'wp/tests/demo').glob('c24*'))
    files += list((c24.ROOT/'wp/outils/demo').glob('c24*'))
    return {p.relative_to(c24.ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files) if p.is_file()}

def run(label):
    assert label.endswith('-V2') and not (c24.PROOF/(label+'.json')).exists()
    prefix=label[:-3];recorded=sources();identity=c24.guard()
    closed_names=['plugins/imagine-site/'+n for n in ['Confidentialite.php','ConfidentialiteRegles.php','Newsletters.php','NewslettersReglages.php','NewslettersRegles.php','Cooperateurs.php','CooperateursRegles.php','Paywall.php']]
    closed=c24.hashes(closed_names)
    normal=[]
    for kind in ['rules','runtime']:
        name=prefix+'-'+kind+'-V2';getattr(c24,kind)(name)
        r=json.loads((c24.PROOF/(name+'.json')).read_text(encoding='utf-8'))
        assert not r['failures'] and not r['exit']
        normal.append({'receipt':name,'total':r['total']})
    mutations={'sansmail':'sansmail_rubrique_presente_sans_case','listener':'accroche_sans_ecouteur','mail':'aucun_mail_tente','http':'aucun_http_tente','export_empty':'export_reponses_consentement_resultat','export_other':'export_tiers_absent','erase_noop':'effacement_resultat_absence_deux_metas'}
    negative=[]
    for mutation,expected in mutations.items():
        name=prefix+'-mutation-'+mutation.replace('_','-')+'-V2'
        try:c24.runtime(name,mutation)
        except AssertionError:pass
        r=json.loads((c24.PROOF/(name+'.json')).read_text(encoding='utf-8'))
        assert r['exit']==1 and expected in r['failures'] and r['state_preserved'] and not r['stderr'],(mutation,r)
        negative.append({'receipt':name,'required_failure':expected})
    assert sources()==recorded and c24.hashes(closed_names)==closed
    recovered=json.loads((c24.PROOF/'recovery-borned-V2.json').read_text(encoding='utf-8'))
    assert recovered['baseline_native_equal'] and recovered['business_actions_equal']
    final={'identity':identity,'sources':recorded,'bootstrap_contract':c24.BLOCK in (c24.ROOT/'wp/plugins/imagine-site/imagine-site.php').read_text(encoding='utf-8'),'remote_sources':c24.hashes(c24.NAMES),'closed_sources':closed,'normal_receipts':normal,'positive_checks':sum(r['total'] for r in normal),'mutations':negative,'mutation_count':len(negative),'result':'BLOCKED','pret':False,'blockers':[recovered['blocker'],'Parcours HTTP corrigé mais non rejoué après la récupération ; mutations des gardes de réutilisation d’identifiants et du consentement encore à qualifier. Image T01 non repréparée : aucun PRET.']}
    c24.save(label,final);print(json.dumps({'result':final['result'],'checks':final['positive_checks'],'mutations':len(negative),'pret':False},ensure_ascii=False))

if __name__=='__main__':run(sys.argv[1])
