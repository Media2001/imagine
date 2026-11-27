"""Reprise de l'inverse B11 après interruption ; préimage privée nommée, pas de rejeu UI."""
import ast
import importlib.util
import json
import os
import sys
from pathlib import Path
sys.dont_write_bytecode=True
import b11

if __name__=='__main__':
    assert len(sys.argv)==2
    label=sys.argv[1]
    root=Path(os.environ['TMPDIR'])
    matches={}
    for p in root.glob('b11-private-*/snapshot.json'):
        data=json.loads(p.read_text(encoding='utf-8'))
        if data.get('label') in [label,label+'-ancillary']:
            assert data['scope']=='imagine-test-demo' and data['label'] not in matches
            matches[data['label']]=(p,data['payload'])
    assert len(matches)==2
    b11.guard()
    payload=matches[label][1]
    spec=importlib.util.spec_from_file_location('recipe',b11.ROOT/'wp/outils/demo/b11-recette.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    tree=ast.parse((b11.ROOT/'wp/outils/demo/b11-recette.py').read_text(encoding='utf-8'))
    run=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='run')
    inverse=next(n for n in run.body if isinstance(n,ast.Try))
    env=dict(module.__dict__,label=label+'-recovery',saved=payload['sessions'],settings0=payload['settings'],business=payload['business'],owned=payload['owned'],ancillary=matches[label+'-ancillary'][1],fixture=b11.wp('echo wp_json_encode(get_option("imagine_b11_fixture"));'),observer='mu-plugins/b11-observer.php',mutant='mu-plugins/b11-no-persist.php',hashes=b11.b10.b09.b08.c25.b06.hashes(b11.FILES),cleanup={},editors={},settings_evidence=[],external=[])
    # Réutilise exactement les inverses entretenues par la recette ; aucun nouveau chemin SQL.
    nodes=inverse.finalbody
    stop=next(i for i,n in enumerate(nodes) if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Attribute) and n.value.func.attr=='save')
    exec(compile(ast.Module(body=nodes[:stop],type_ignores=[]),str(b11.ROOT/'wp/outils/demo/b11-recette.py'),'exec'),env)
    b11.save(label+'-recovery',{'cleanup':env['cleanup'],'reason':'Nettoyage interrompu par suppression non idempotente du mutant absent ; inverse reprise seule.','business_exact':env['cleanup']['business_preserved']})
    print(json.dumps(env['cleanup']))
    assert all(env['cleanup'].values())
