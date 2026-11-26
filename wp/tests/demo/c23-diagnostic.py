"""Diagnostic ponctuel : présence réelle dans les listes, aucune session imprimée."""
import sys
sys.dont_write_bytecode=True
import importlib.util
from pathlib import Path
import json,re
TOOLS=Path(__file__).resolve().parents[2]/'outils/demo'
sys.path.insert(0,str(TOOLS))
import c23
s=importlib.util.spec_from_file_location('prep',TOOLS/'c23-preparer.py');p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
p.profils.guard('imagine-test-demo')
f=p.inventory();ids=list(f['users'].values());old=p.metadata_snapshot(ids,f['article'])
try:
    sessions=p.prepare(f)
    out=[]
    for name,path in [('archives',f['posts_archive']),('rss2','/?feed=rss2'),('atom','/?feed=atom')]:
        for public in ['connecte-sans-abonnement','acheteur-autre-numero']:
            session=sessions[public]
            status,_,body=c23.fetch(path,{'Cookie':session['cookie'],'X-WP-Nonce':session['nonce']})
            out.append(dict(name=name,public=public,status=status,
                primary_present=f['article_path'].encode() in body,
                open_present=b'/demo-2026-t4-ouvert/' in body,
                c08_present=b'/c08-article-reserve-article/' in body,
                known_post_slugs=sorted(set(re.findall(rb'(?:demo-2026-[a-z0-9-]+|c08-article-reserve-[a-z]+)',body)))[:30]))
    text=json.dumps(out,default=lambda x:x.decode(),indent=2)
    (p.PROOF/'diagnostic-listes.json').write_text(text,encoding='utf-8');print(text)
finally:
    p.restore(old,ids,f['article'])
    assert p.metadata_snapshot(ids,f['article'])==old
