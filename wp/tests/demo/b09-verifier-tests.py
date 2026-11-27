"""Qualification sémantique du vérificateur, uniquement dans des copies scratch privées."""
import sys
sys.dont_write_bytecode=True
import copy
import hashlib
import importlib.util
import json
import os
import shutil
import tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'wp/outils/demo'))
import b09
spec=importlib.util.spec_from_file_location('b09_verifier',ROOT/'production/B-09/verifier.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
packet=json.loads((ROOT/'production/B-09'/v.PACKET).read_text(encoding='utf-8'))
paths=set(packet['sources'])|set(packet['artifacts'])|{'wp/plugins/imagine-site/imagine-site.php','wp/themes/imagine/footer.php','wp/plugins/imagine-site/README.md'}
pre={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in paths}
rows=[]

def record(root,p,name,fn):
    rel=v.RENAMES.get('production/B-09/'+name,'production/B-09/'+name)
    f=root/rel;d=json.loads(f.read_text(encoding='utf-8'));fn(d)
    f.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
    p['artifacts'][rel]=v.digest(f.read_bytes())

def receipt(name,fn): return lambda root,p:record(root,p,name,fn)
def source(root,p):
    name='wp/plugins/imagine-site/Contact.php'
    f=root/name;f.write_text(f.read_text(encoding='utf-8')+'\n// mutation témoin\n',encoding='utf-8');p['sources'][name]=v.digest(f.read_bytes())
def section(root,p):
    f=root/'wp/plugins/imagine-site/README.md';s=f.read_text(encoding='utf-8').replace('wp_slash($meta)','mécanisme retiré');f.write_text(s,encoding='utf-8');p['readme_section_sha256']=v.digest(s.split('## B-09 — FAQ, pages légales et contact',1)[1].split('\n## ',1)[0].strip().encode())
def shared(root,p):
    for name in ['wp/plugins/imagine-site/imagine-site.php','wp/plugins/imagine-site/README.md']:
        f=root/name;f.write_text(('<?php\n// autre lot\n' + f.read_text(encoding='utf-8')[6:]) if name.endswith('.php') else '# Autre section commune\n\n'+f.read_text(encoding='utf-8'),encoding='utf-8')

cases=[
 ('baseline',lambda r,p:None,False),
 ('autres_sections_partagees',shared,False),
 ('controle_omis',receipt('recette-finale.json',lambda d:d['checks'].pop('absence_REST_recherche')),True),
 ('nettoyage_vide',receipt('recette-finale.json',lambda d:d.update(cleanup={})),True),
 ('restauration_rouge',receipt('recette-finale.json',lambda d:d['restoration'].update(posts=False)),True),
 ('mutation_live_pas_rouge',receipt('recette-finale.json',lambda d:d.update(mutation_isolation=v.ISOLATION)),True),
 ('observateur_toujours_zero',receipt('recette-finale.json',lambda d:d.update(positive_observers={'ambiance_mail':0,'ambiance_http':0})),True),
 ('email_tente',receipt('recette-finale.json',lambda d:d.update(observations={'b09_mail':1})),True),
 ('regression_rouge',receipt('regression-finale.json',lambda d:d['results'][0].update(pass_=False,errors=1)),True),
 ('paquet_B09_rouge',receipt('regression-finale.json',lambda d:d['results'][0]['packets']['failures'].append({'lot':'B-09','control':'ECHEC_TEMOIN'})),True),
 ('residu_contact',receipt('readback-final.json',lambda d:d['native'].update(contact_meta=1)),True),
 ('interruption_absente',receipt('pages-reprise-finale.json',lambda d:d.update(interrupted_exit=0)),True),
 ('pas_item_orphelin',receipt('pages-reprise-finale.json',lambda d:d['partial'].update(attached=3)),True),
 ('source_rescellee_non_retestee',source,True),
 ('preuve_omise',lambda r,p:p['artifacts'].pop(v.RENAMES['production/B-09/readback-final.json']),True),
 ('total_invente',lambda r,p:p['counts'].update(native_checks=p['counts']['native_checks']+1),True),
 ('mutation_junit_forgée',receipt('mutations-finales.json',lambda d:d['mutations'][0]['junit'].update(failures='0')),True),
 ('README_essentiel_retire_rescelle',section,True),
 ('temoin_nettoyage_reste',receipt('readback-final.json',lambda d:d['native'].update(contact_pending=1)),True),
 ('faux_done_partiel',receipt('corrections-effacement-natif.json',lambda d:d['first']['result'].update(done=True)),True),
 ('pas_interruption_marqueur_option',receipt('corrections-green-seed.json',lambda d:d.update(interrupted_exit=0)),True),
 ('item_encore_orphelin',receipt('corrections-green-seed.json',lambda d:d['native'][0].update(menus=[])),True),
 ('meme_cle_deux_items',receipt('corrections-green-seed.json',lambda d:d['native'][0].update(key=d['native'][1]['key'])),True),
]
for name,mutate,refused in cases:
    with tempfile.TemporaryDirectory(prefix='b09-verifier-',dir=os.environ['TMPDIR']) as folder:
        root=Path(folder)
        for path in paths:
            dest=root/path;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/path,dest)
        p=copy.deepcopy(packet);mutate(root,p)
        rejected=False
        try:v.validate(root,p)
        except (AssertionError,KeyError,ValueError):rejected=True
        ok=rejected==refused
        rows.append({'case':name,'expected_refusal':refused,'refused':rejected,'pass':ok})
        print(name,'PASS' if ok else 'FAIL')
assert {n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in paths}==pre
b09.save(sys.argv[1],{'cases':rows,'count':len(rows),'refusals':sum(r['refused'] for r in rows),'sources_unchanged':True})
assert all(r['pass'] for r in rows)
