"""Vérification locale du paquet C23 : reçus réels, matrice, mutation, empreintes."""
import ast
from pathlib import Path
import hashlib
import importlib.util
import json
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
PROOF=ROOT/'production/C-23'


def read(name):
    return json.loads((PROOF/name).read_text(encoding='utf-8'))


def business_original_exact(state, *receipts):
    if not state or not receipts:
        return False
    expected = hashlib.sha256(json.dumps(state, sort_keys=True).encode()).hexdigest()
    return all(r.get('native_before_sha256') == r.get('native_after_sha256') == expected for r in receipts)


def verify():
    final=read('livraison.json')
    restoration=read('livraison-restauration.json')
    red=read('mutation-publics-complets.json')
    red_restore=read('mutation-publics-complets-restauration.json')
    fixture=read('inventaire-source.json')
    spec=importlib.util.spec_from_file_location('c23_delivery',ROOT/'wp/outils/demo/c23.py')
    core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)
    checks={}
    checks['scope_exact']=all(r.get('scope')=='imagine-test-demo' for r in [final,restoration,red,red_restore,fixture])
    checks['last_command_exit_0']=restoration['command_exit']==0
    checks['count_exact']=final['total']==len(final['results'])
    checks['leaks_exact_zero']=final['leaks']==sum(bool(r['leak']) for r in final['results'])==0
    checks['failures_exact_zero']=final['failures']==sum(not r['ok'] for r in final['results'])==0
    expected=core.build_routes(fixture)
    checks['route_count_exact']=final['routes']==len(expected)
    checks['audience_count_exact']=final['publics']==core.audience_order(fixture)
    checks['matrix_complete']=all(sum(r['name']==route['name'] and r['public']==public for r in final['results'])==1 for route in expected for public in final['publics'])
    checks['matrix_pairs_unique']=len({(r['name'],r['public']) for r in final['results']})==len(final['results'])
    checks['final_stdout_summary_exact']=final['summary'] in (PROOF/'livraison.txt').read_text(encoding='utf-8')
    checks['source_current']=final['command_sha256']==hashlib.sha256((ROOT/'wp/outils/demo/c23.py').read_bytes()).hexdigest()
    checks['red_source_current']=red['command_sha256']==final['command_sha256']
    checks['fixture_bound']=final['fixture_sha256']==hashlib.sha256(json.dumps(fixture,sort_keys=True).encode()).hexdigest()
    checks['restoration_exact']=all(restoration[k] is True for k in ['metadata_restored_exactly','profiles_and_scheduled_actions_restored_exactly','business_unchanged_during_GETs'])
    checks['red_restoration_exact']=all(red_restore[k] is True for k in ['metadata_restored_exactly','profiles_and_scheduled_actions_restored_exactly','mutation_red_detected'])
    checks['schedule_exact']=restoration['schedule_before']==restoration['schedule_after']==red_restore['schedule_before']==red_restore['schedule_after']
    baseline = read('baseline-V2.json')['state'] if (PROOF/'baseline-V2.json').is_file() else {}
    checks['business_original_exact']=business_original_exact(baseline, restoration, red_restore)
    checks['red_detected']=red_restore['command_exit']==1 and red['leaks']>0 and any(r['name']=='article' and r['public']=='anonyme' and r['leak'] for r in red['results'])
    checks['inverse_article_pdf']=all(any(r['name']==name and r['public']=='abonne-actif' and r['ok'] and r['witnesses_found']>0 for r in final['results']) for name in ['inverse-article','inverse-pdf','inverse-C08'])
    checks['C14_owned_allowed_other_denied']=any(r['name']=='pdf-inventorie-11-endpoint' and r['public']=='acheteur-autre-numero' and r['ok'] and r['witnesses_found']>0 for r in final['results']) and any(r['name']=='pdf-telechargement' and r['public']=='acheteur-autre-numero' and r['ok'] and not r['witnesses_found'] for r in final['results'])
    source_checks={}
    for receipt in [restoration,red_restore]:
        for name,expected_sha in receipt['sources_sha256'].items():
            if name.startswith('wp/outils/demo/c23') or name.startswith('wp/tests/demo/c23'):
                source_checks[name]=source_checks.get(name,True) and hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected_sha
            else:
                source_checks[name]=False
    checks['all_recorded_own_sources_current']=all(source_checks.values())
    tree=ast.parse((ROOT/'wp/outils/demo/c23.py').read_text(encoding='utf-8'))
    methods=[k.value.value for n in ast.walk(tree) if isinstance(n,ast.Call) for k in n.keywords if k.arg=='method' and isinstance(k.value,ast.Constant)]
    checks['main_GET_only']=methods==['GET'] and not any(isinstance(n,ast.alias) and n.name in ['subprocess','profils','construire','b05'] for n in ast.walk(tree))
    checks['no_session_dump']=not any('wordpress_logged_in_' in p.read_text(encoding='utf-8',errors='replace') or 'X-WP-Nonce' in p.read_text(encoding='utf-8',errors='replace') for p in PROOF.glob('*.json'))
    checks['image_prepared']=read('image-preparation.json')['exit']==0 and 'T01 IMAGE READY' in (PROOF/'image-preparation.txt').read_text(encoding='utf-8',errors='replace')
    checks['unit_tests_both_encodings']=all(read('tests-finaux.json')[key]['exit']==0 for key in ['utf8','cp1252'])
    result={'scope':'imagine-test-demo','checks':checks,'total':len(checks),'failures':[k for k,v in checks.items() if v is not True],
            'last_matrix':{k:final[k] for k in ['total','leaks','failures','routes','publics','summary']},'mutation':{'total':red['total'],'leaks':red['leaks'],'exit':red_restore['command_exit']}}
    print(json.dumps(result,ensure_ascii=True,indent=2))
    return not result['failures']


if __name__=='__main__':
    raise SystemExit(0 if verify() else 1)
