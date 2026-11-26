"""B06 : mutations en mémoire de chaque réponse HTTP native, pas du paywall."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'wp/outils/demo'))
import c23
import b06
spec = importlib.util.spec_from_file_location('c23_preparation', ROOT/'wp/outils/demo/c23-preparer.py')
prep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prep)


def sha(value):
    return hashlib.sha256(value).hexdigest()


def inject(body, marker):
    try:
        value = json.loads(body)
    except (ValueError, UnicodeError):
        return body+b'<!-- '+marker.encode()+b' -->'
    if isinstance(value, dict):
        value['c23_mutation_fictive'] = marker
    elif isinstance(value, list):
        value.append({'c23_mutation_fictive':marker})
    else:
        raise ValueError('B06 réponse JSON inattendue')
    return json.dumps(value, ensure_ascii=False).encode()


def run(label='b06-reponses-mutations-V2'):
    if not re.fullmatch('[a-zA-Z0-9-]+',label):
        raise ValueError('Nom refusé')
    path = prep.PROOF/(label+'.json')
    if path.exists():
        raise ValueError('Reçu existant')
    b06.guard()
    f = prep.inventory()
    ids = list(f['users'].values())
    original = prep.metadata_snapshot(ids,f['article'])
    pages = prep.cooperator_snapshot(f)
    before = prep.b05.state()
    result = {'scope':'imagine-test-demo','coverage':'B06-mutations-reponses',
              'site_leak_injected':False,'rows':[]}
    try:
        prep.seed_cooperator_witness(pages)
        sessions = prep.create_sessions(f)
        f = prep.inventory()
        coop = sessions['profil-p-coop']
        headers = {'Cookie':coop['cookie'],'X-WP-Nonce':coop['nonce']}
        for route in c23.cooperator_routes(f):
            native = c23.fetch(route['path'])
            status, hs, body = native
            clean = c23.assess_cooperator(route,native,False)
            inverse = c23.assess_cooperator(route,c23.fetch(route['path'],headers),True)
            mutated = inject(body,route['cooperator_marker'])
            red = c23.assess_cooperator(route,(status,hs,mutated),False)
            restored = bytes(body)
            restored_verdict = c23.assess_cooperator(route,(status,hs,restored),False)
            result['rows'].append(dict(name=route['name'],surface_present=clean['surface_present'],
                clean_ok=clean['ok'],inverse_ok=inverse['ok'],mutant_leak=red['leak'],mutant_failed=not red['ok'],
                original_sha256=sha(body),mutant_sha256=sha(mutated),restored_sha256=sha(restored),
                restored_ok=restored_verdict['ok']))
    finally:
        try:
            prep.restore_cooperator(pages)
        finally:
            prep.restore(original,ids,f['article'])
        result['metadata_restored_exactly'] = prep.metadata_snapshot(ids,f['article'])==original
        result['pages_restored_exactly'] = prep.cooperator_snapshot(f)==pages
        after = prep.b05.state()
        result['profiles_actions_restored_exactly'] = before==after
        result['native_before_sha256'] = sha(json.dumps(before,sort_keys=True).encode())
        result['native_after_sha256'] = sha(json.dumps(after,sort_keys=True).encode())
        result['sources_sha256']={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for folder in [ROOT/'wp/outils/demo',ROOT/'wp/tests/demo'] for p in folder.glob('c23*') if p.is_file()}
        result['total']=len(result['rows'])
        result['failures']=[r['name'] for r in result['rows'] if not all(r[k] for k in ['surface_present','clean_ok','inverse_ok','mutant_leak','mutant_failed','restored_ok']) or r['original_sha256']!=r['restored_sha256'] or r['original_sha256']==r['mutant_sha256']]
        result['success']=result['total']==35 and not result['failures'] and all(result[k] for k in ['metadata_restored_exactly','pages_restored_exactly','profiles_actions_restored_exactly'])
        path.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['scope','total','failures','success']},ensure_ascii=True))
    return 0 if result['success'] else 1


if __name__=='__main__':
    raise SystemExit(run(*sys.argv[1:]))
