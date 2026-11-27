"""C26 vérificateur offline : stdout JSON seulement, aucune écriture ni réseau."""
import sys
sys.dont_write_bytecode = True
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import re
ROOT = Path(__file__).resolve().parents[3]
PROOF = ROOT / 'production/C-26'
sys.path.insert(0, str(ROOT/'wp/outils/demo'))
import c26
EXACT = ['users','usermeta','posts','postmeta','comments','commentmeta','wc_orders','wc_orders_meta','wc_order_addresses','wc_order_operational_data','woocommerce_order_items','woocommerce_order_itemmeta','navigation','business_options']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def matrix_checks(record, routes, publics):
    rows = record['results']
    expected = {(r['name'],p) for r in routes for p in publics}
    counts = Counter((r['name'],r['public']) for r in rows)
    paths = {r['name']:r['path'] for r in routes}
    return {'nonempty':bool(rows) and bool(routes) and bool(publics),
            'total':record['total']==len(rows)==len(expected),
            'cases':set(counts)==expected and all(n==1 for n in counts.values()),
            'leaks':record['leaks']==sum(r['leak'] is True for r in rows)==0,
            'failures':record['failures']==sum(r['ok'] is not True for r in rows)==0,
            'surfaces':all(r.get('surface_present') is True and r.get('status',0)>0 and r.get('bytes',0)>0 and re.fullmatch('[a-f0-9]{64}',r.get('body_sha256','')) and r.get('path')==paths.get(r['name']) for r in rows)}


def privacy_checks(record, publics, mutation=None):
    rows = record['results']
    wanted = {(p,family) for p in publics+['inverse-proprietaire'] for family in c26.FAMILIES}
    counts = Counter((x['public'],x['family']) for x in rows)
    def valid(x):
        owner = x['public'] == 'inverse-proprietaire'
        red = not owner and x['family'] == mutation
        return (x.get('positive') is owner and x.get('ok') is (not red)
                and x.get('leak') is red and x.get('surface_present') is True
                and (x.get('witnesses_found',0)>0 if owner or red else x.get('witnesses_found')==0)
                and bool(re.fullmatch('[a-f0-9]{64}',x.get('payload_sha256',''))))
    red_count = len(publics) if mutation else 0
    return {'cases':set(counts)==wanted and all(n==1 for n in counts.values()),
            'total':record['total']==len(rows)==len(wanted),
            'failures':record['failures']==sum(x.get('ok') is not True for x in rows)==red_count,
            'leaks':record['leaks']==sum(x.get('leak') is True for x in rows)==red_count,
            'semantics':all(valid(x) for x in rows)}


def c23_checks(record, f):
    routes = c26.c23.build_routes(f)
    publics = c26.c23.audience_order(f)
    expected = {(r['name'],p):r['path'] for r in routes for p in publics}
    identities = [p for p in publics if p not in ['anonyme','faux-robot']]+['abonne-actif']
    extras = {('identite-REST','controle-'+p):'/wp-json/wp/v2/users/me' for p in identities}
    extras.update({('inverse-article','abonne-actif'):f['article_path'],
        ('inverse-pdf','abonne-actif'):'/?imagine_pdf='+str(f['issue']),
        ('inverse-C08','abonne-actif'):'/?p='+str(f['c08']),
        ('inverse-achat-C14','acheteur-autre-numero'):'/?p='+str(f['c08']),
        ('faux-bing','faux-robot'):f['article_path']})
    expected.update(extras)
    rows = record['results']
    counts = Counter((x['name'],x['public']) for x in rows)
    by_name = {r['name']:r for r in routes}
    def positive(x):
        if x['name'].startswith('inverse-'):
            return True
        route = by_name.get(x['name'],{})
        return (('cooperator_kind' in route and x['public'] in f['cooperator_publics']
                 and route['cooperator_kind']!='oembed')
                or (x['public']=='acheteur-autre-numero'
                    and str(route.get('pdf_issue','')) in f['buyer_issues']))
    return {'cases':set(counts)==set(expected) and all(n==1 for n in counts.values()),
            'total':record['total']==len(rows)==len(expected),
            'leaks':record['leaks']==sum(x.get('leak') is True for x in rows)==0,
            'failures':record['failures']==sum(x.get('ok') is not True for x in rows)==0,
            'surfaces':all(x.get('surface_present') is True and x.get('structure') is True
                and x.get('status',0)>0 and x.get('bytes',0)>0
                and re.fullmatch('[a-f0-9]{64}',x.get('body_sha256',''))
                and x.get('path')==expected.get((x['name'],x['public'])) for x in rows),
            'witnesses':all(x.get('witnesses_found',0)>0 if positive(x)
                else x.get('witnesses_found')==0 for x in rows),
            'catalogue':record['routes']==len(routes) and record['publics']==publics}


def restored(r):
    return (set(r.get('exact_restoration',{}))==set(EXACT)
            and all(v is True for v in r['exact_restoration'].values())
            and not r.get('run_error') and r.get('restoration_errors')==[]
            and set(r.get('restoration_steps',{}))=={'cleanup','b06','usermeta'}
            and all(x.get('attempted') is True and x.get('ok') is True for x in r['restoration_steps'].values())
            and all(r.get(k) is True for k in ['business_preserved','live_sources_preserved','business_unchanged_during_GETs','privacy_green'])
            and r.get('command_exit')==0 and r.get('before_sha256')==r.get('after_sha256')
            and bool(re.fullmatch('[a-f0-9]{64}',r.get('before_sha256',''))))


def verify(packet=PROOF):
    checks = {}
    def check(key, value):
        checks[key] = value is True
    try:
        manifest = json.loads((packet/'manifest.json').read_text(encoding='utf-8'))
        read = lambda name:json.loads((packet/name).read_text(encoding='utf-8'))
        labels = [manifest['delivery'],manifest['mutations']]
        check('scope',manifest.get('scope')=='imagine-test-demo')
        check('labels',all(bool(re.fullmatch('[a-zA-Z0-9-]+',x)) for x in labels) and len(set(labels))==2)
        own = c26.source_hashes()
        check('sources',manifest['sources']==own)
        artifacts = manifest['artifacts']
        check('artifact_hashes',bool(artifacts) and all(Path(n).name==n and sha(packet/n)==h for n,h in artifacts.items()))
        required = {'tests.json','tests-utf8.log','tests-cp1252.log','image.json','image.log','A-VOIR.md','INVENTAIRE.md'}
        for label in labels:
            required.update(label+s for s in ['.json','.md','.log','-avant.json','-restauration.json','-privacy.json','-inventaire.json','-extension.json','-c23.json','-c23.md'])
        required.update(labels[1]+'-mutation-'+family+'.json' for family in c26.MUTATIONS)
        check('required_artifacts',required.issubset(artifacts))
        for index,label in enumerate(labels):
            record, f, r = read(label+'.json'),read(label+'-inventaire.json'),read(label+'-restauration.json')
            before = read(label+'-avant.json')
            expected_hash = hashlib.sha256(json.dumps(before['business'],sort_keys=True).encode()).hexdigest()
            check(label+'_scope',all(x.get('scope')=='imagine-test-demo' for x in [record,f,r,before]))
            check(label+'_sources_run',before['sources']==own)
            check(label+'_restored',restored(r) and expected_hash==r['before_sha256'])
            check(label+'_private_preimage',r['private_snapshot']==before['private_snapshot'] and r['private_snapshot'].get('private') is True and bool(re.fullmatch('[a-f0-9]{64}',r['private_snapshot'].get('sha256',''))))
            catalog = c26.routes(f['extension'])
            publics = c26.c23.audience_order(f)+['abonne-actif']
            check(label+'_b06_oracle',set(c26.validate_cooperator(f))==set(f['cooperator_publics']))
            check(label+'_witness_oracle',bool(c26.denied_markers(f,'anonyme'))
                and all(re.fullmatch('C26_[A-Z_]+',m) is not None for m in f['extension']['markers'].values()))
            check(label+'_catalogue',record['routes']==catalog and record['publics']==publics and record['coverage']=='C26-nouvelles-sorties' and record['c23_exit']==0)
            for key,val in matrix_checks(record,catalog,publics).items():
                check(label+'_'+key,val)
            privacy = read(label+'-privacy.json')
            for key,value in privacy_checks(privacy,publics).items():
                check(label+'_privacy_'+key,value)
            c23 = read(label+'-c23.json')
            check(label+'_c23_source',c23['command_sha256']==sha(ROOT/'wp/outils/demo/c23.py'))
            for key,value in c23_checks(c23,f).items():
                check(label+'_c23_'+key,value)
            check(label+'_b06_inverse',all(any(x['name']=='b06-'+str(p['id'])+'-'+kind and x['public']=='profil-p-coop' and x['ok'] is True and x['witnesses_found']>0 for x in c23['results']) for p in f['cooperator_pages'] for kind in ['html','rest','rest-route','collection','embed','recherche']))
            check(label+'_policy',c23['discovery']['policy']==f['discovery_policy'] and c23['discovery']['audience']==c26.c23.discovery_audience(f) and (c23['discovery']['exhausted_played'] is False if f['discovery_policy']['ouverture']=='fermee' else c23['discovery']['exhausted_played'] is True))
            if index==0:
                check('normal_not_mutation','mutations_detected' not in r)
            else:
                check('mutation_families',Counter(r.get('mutations_detected',[]))==Counter(c26.MUTATIONS))
                for family in c26.FAMILIES:
                    m = read(label+'-mutation-'+family+'.json')
                    check('mutation_'+family,m['route']=='registered-native-exporter-callbacks' and m['mutation']==family and all(privacy_checks(m,publics,family).values()))
                for family in ['cooperateurs','cooperative']:
                    m = read(label+'-mutation-'+family+'.json')
                    check('mutation_'+family,m.get('persisted_fixture') is True and m['total']==len(m['results'])==1 and all(x['leak'] is True and x['ok'] is False and x['witnesses_found']>0 and x['surface_present'] is True and x['status']==200 and x['bytes']>0 for x in m['results']))
                    if family=='cooperative':
                        check('mutation_C08_et_B06',m.get('families')=={'C08':True,'B06':True}
                            and m['results'][0]['witnesses_found']>=2)
                for family,name in [('archive','themes/imagine/archive-imagine_evenement.php'),
                                    ('autorisation-b06','plugins/imagine-site/Cooperateurs.php')]:
                    m = read(label+'-mutation-'+family+'.json')
                    expected_sha = before['live_source_hashes'][name]
                    check('mutation_source_'+family,m.get('source')==name and m.get('source_restored') is True
                        and m.get('before_sha256')==m.get('restored_sha256')==expected_sha
                        and m.get('mutated_sha256')!=expected_sha
                        and bool(re.fullmatch('[a-f0-9]{64}',m.get('mutated_sha256',''))))
                    if family=='archive':
                        check('mutation_archive',m['total']==len(m['results'])==1
                            and all(x['name']=='agenda-archive' and x['public']=='anonyme'
                            and x['leak'] is True and x['ok'] is False and x['witnesses_found']>0
                            and x['surface_present'] is True and x['status']==200 and x['bytes']>0 for x in m['results']))
                    else:
                        check('mutation_autorisation_b06',all(m.get(k) is True for k in
                            ['oracle_rejected','inventory_after_mutation','roles_unchanged','actors_unchanged'])
                            and m['expected']==c26.cooperator_expected(f)
                            and set(m['observed'])==set(m['expected'])|{'connecte-sans-abonnement'}
                            and 'connecte-sans-abonnement' not in m['expected'])
        tests,image = read('tests.json'),read('image.json')
        check('tests',all(tests[k]['exit']==0 and tests[k]['tests']==52 and tests[k]['version'].startswith('3.11.') and tests[k]['TMPDIR_present'] is False and tests[k]['network_blocked'] is True and 'Ran 52 tests' in (packet/('tests-'+k+'.log')).read_text(encoding='utf-8') and '\nOK\n' in (packet/('tests-'+k+'.log')).read_text(encoding='utf-8') for k in ['utf8','cp1252']))
        check('image',image['exit']==0 and 'T01 IMAGE READY' in (packet/'image.log').read_text(encoding='utf-8'))
        check('no_session_dump',not any('wordpress_logged_in_' in (packet/n).read_text(encoding='utf-8',errors='replace') or 'X-WP-Nonce' in (packet/n).read_text(encoding='utf-8',errors='replace') for n in artifacts if n.endswith('.json')))
    except Exception as error:
        checks['packet_complete_'+type(error).__name__] = False
    result = {'scope':'imagine-test-demo','checks':checks,'total':len(checks),'failures':[k for k,v in checks.items() if v is not True]}
    print(json.dumps(result,ensure_ascii=True,indent=2))
    return not result['failures']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--packet',type=Path,default=PROOF)
    args = parser.parse_args()
    raise SystemExit(0 if verify(args.packet) else 1)
