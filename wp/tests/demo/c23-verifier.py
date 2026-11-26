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


def matrix_checks(core, record, fixture, only_b06=False):
    routes = core.cooperator_routes(fixture) if only_b06 else core.build_routes(fixture)
    rows, publics = record['results'], core.audience_order(fixture)
    return {
        'nonempty': bool(rows) and bool(routes) and bool(publics),
        'counts': record['total'] == len(rows) and record['routes'] == len(routes),
        'audiences': record['publics'] == publics,
        'complete': all(sum(x['name']==r['name'] and x['public']==p for x in rows)==1 for r in routes for p in publics),
        'unique': len({(r['name'],r['public']) for r in rows}) == len(rows),
        'no_leaks': record['leaks'] == sum(bool(r['leak']) for r in rows) == 0,
        'no_failures': record['failures'] == sum(not r['ok'] for r in rows) == 0,
        'fixture_bound': record['fixture_sha256'] == hashlib.sha256(json.dumps(fixture,sort_keys=True).encode()).hexdigest(),
    }


def verify(label='livraison-arbitrage1930', b06_label='b06-arbitrage1930', mutation_label='mutation-arbitrage1930', discovery_label='decouverte-ouverte-epuisee-arbitrage1930'):
    import re
    checks, details = {}, {}
    spec=importlib.util.spec_from_file_location('c23_delivery',ROOT/'wp/outils/demo/c23.py')
    core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)
    current=hashlib.sha256((ROOT/'wp/outils/demo/c23.py').read_bytes()).hexdigest()
    for name, role in [(label,'delivery'),(b06_label,'B06'),(mutation_label,'mutation'),(discovery_label,'discovery')]:
        if not re.fullmatch('[a-zA-Z0-9-]+',name):
            raise ValueError('Nom de reçu refusé')
        try:
            record, restoration, fixture = read(name+'.json'), read(name+'-restauration.json'), read(name+'-inventaire.json')
            checks[role+'_scope'] = all(x.get('scope')=='imagine-test-demo' for x in [record,restoration,fixture])
            checks[role+'_source'] = record['command_sha256']==current
            sources=restoration.get('sources_sha256',{})
            checks[role+'_all_sources'] = bool(sources) and all(
                (p.startswith('wp/outils/demo/c23') or p.startswith('wp/tests/demo/c23'))
                and hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==sha for p,sha in sources.items())
            checks[role+'_restoration'] = all(restoration.get(k) is True for k in [
                'metadata_restored_exactly','profiles_and_scheduled_actions_restored_exactly',
                'business_unchanged_during_GETs','cooperator_pages_restored_exactly'])
            checks[role+'_native_derived'] = business_original_exact(read(name+'-etat.json')['state'],restoration)
            checks[role+'_schedule'] = restoration['schedule_before']==restoration['schedule_after']
            checks[role+'_private_preimage'] = restoration.get('private_snapshot',{}).get('private') is True
            checks[role+'_summary'] = record['summary'] in (PROOF/(name+'.txt')).read_text(encoding='utf-8')
            details[role] = {k:record[k] for k in ['total','leaks','failures','summary','coverage']}
            if role=='delivery':
                checks['delivery_prerequisites'] = not bool(record.get('prerequisite'))
                checks['delivery_exit'] = restoration['command_exit']==0
                checks['delivery_nonempty'] = bool(record['results'])
                if record.get('prerequisite'):
                    details['prerequisite']=record['prerequisite']
                    continue
                checks['delivery_full_scope'] = record['coverage']=='livraison'
            if role=='mutation':
                checks['mutation_red'] = restoration.get('mutation_red_detected') is True and restoration['command_exit']==1 and record['leaks']>0 and any(
                    r['name']=='article' and r['public']=='anonyme' and r['leak'] for r in record['results'])
                continue
            checks.update({role+'_'+k:v for k,v in matrix_checks(core,record,fixture,role=='B06').items()})
            if role in ['delivery','discovery']:
                closed=fixture['discovery_policy']['ouverture']=='fermee'
                case=record.get('discovery',{})
                checks[role+'_discovery_actual_policy'] = case.get('policy')==fixture['discovery_policy'] and case.get('exhausted_played') is (not closed)
                checks[role+'_discovery_audience'] = case.get('audience')==core.discovery_audience(fixture) and case.get('audience') in record['publics']
                checks[role+'_discovery_trace'] = bool(case.get('note')) and (not closed or 'non joué' in case['note'])
            if role=='discovery':
                checks['discovery_separate_open_exhausted'] = record['coverage']=='recette-decouverte-ouverte-epuisee' and not closed and restoration.get('discovery_recipe') is True and restoration.get('discovery_open_exhausted_proved') is True and restoration['command_exit']==0
            if role=='delivery':
                checks['delivery_no_forced_policy'] = restoration.get('mutation') is False and restoration.get('discovery_recipe') is False
            if role=='B06':
                checks['B06_explicit_scope'] = record['coverage']=='B06-only' and restoration['command_exit']==0
                checks['B06_inverse_nonempty'] = all(any(r['name']=='b06-'+str(p['id'])+'-'+kind and r['public']=='profil-p-coop' and r['ok'] and r['witnesses_found']>0 for r in record['results']) for p in fixture['cooperator_pages'] for kind in ['html','rest','rest-route','collection','embed','recherche'])
        except (OSError,KeyError,ValueError,TypeError) as error:
            checks[role+'_receipt_complete']=False
            details[role+'_error']=type(error).__name__
    tree=ast.parse((ROOT/'wp/outils/demo/c23.py').read_text(encoding='utf-8'))
    methods=[k.value.value for n in ast.walk(tree) if isinstance(n,ast.Call) for k in n.keywords if k.arg=='method' and isinstance(k.value,ast.Constant)]
    checks['main_GET_only']=methods==['GET'] and not any(isinstance(n,ast.alias) and n.name in ['subprocess','profils','construire','b05','b06'] for n in ast.walk(tree))
    checks['no_session_dump']=not any('wordpress_logged_in_' in p.read_text(encoding='utf-8',errors='replace') or 'X-WP-Nonce' in p.read_text(encoding='utf-8',errors='replace') for p in PROOF.glob('*.json'))
    for key,filename in [('tests','tests-arbitrage1930.json'),('image','image-preparation-arbitrage1930.json')]:
        try:
            value=read(filename)
            checks[key]=all(value[k]['exit']==0 for k in ['utf8','cp1252']) if key=='tests' else value['exit']==0 and 'T01 IMAGE READY' in (PROOF/'image-preparation-arbitrage1930.txt').read_text(encoding='utf-8')
        except (OSError,KeyError,ValueError):
            checks[key]=False
    result={'scope':'imagine-test-demo','checks':checks,'total':len(checks),
            'failures':[k for k,v in checks.items() if v is not True],'details':details}
    print(json.dumps(result,ensure_ascii=True,indent=2))
    return not result['failures']


if __name__=='__main__':
    raise SystemExit(0 if verify(*sys.argv[1:]) else 1)
