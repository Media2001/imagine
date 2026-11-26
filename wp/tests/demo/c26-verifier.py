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


def restored(r):
    return (set(r.get('exact_restoration',{}))==set(EXACT)
            and all(v is True for v in r['exact_restoration'].values())
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
        own = {p.relative_to(ROOT).as_posix():sha(p) for folder in ['wp/outils/demo','wp/tests/demo'] for p in (ROOT/folder).glob('c26*') if p.is_file()}
        source_contract = {**own,'wp/tests/demo/c23-tests.py':sha(ROOT/'wp/tests/demo/c23-tests.py')}
        check('sources',manifest['sources']==source_contract)
        artifacts = manifest['artifacts']
        check('artifact_hashes',bool(artifacts) and all(Path(n).name==n and sha(packet/n)==h for n,h in artifacts.items()))
        required = {'tests.json','tests-utf8.log','tests-cp1252.log','image.json','image.log','A-VOIR.md','INVENTAIRE.md'}
        for label in labels:
            required.update(label+s for s in ['.json','.md','.log','-avant.json','-restauration.json','-privacy.json','-inventaire.json','-extension.json','-c23.json','-c23.md'])
        required.update(labels[1]+'-mutation-'+family+'.json' for family in c26.FAMILIES+['cooperateurs','cooperative'])
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
            check(label+'_catalogue',record['routes']==catalog and record['publics']==publics and record['coverage']=='C26-nouvelles-sorties' and record['c23_exit']==0)
            for key,val in matrix_checks(record,catalog,publics).items():
                check(label+'_'+key,val)
            privacy = read(label+'-privacy.json')
            wanted = {(p,family) for p in publics+['inverse-proprietaire'] for family in c26.FAMILIES}
            rows = privacy['results']
            check(label+'_privacy',privacy['total']==len(rows)==len(wanted) and {(x['public'],x['family']) for x in rows}==wanted and privacy['failures']==privacy['leaks']==0 and all(x['ok'] is True and x['leak'] is False and x['surface_present'] is True and (x['witnesses_found']>0 if x['positive'] else x['witnesses_found']==0) for x in rows))
            c23 = read(label+'-c23.json')
            expected = c26.c23.build_routes(f)
            # C23 possède des inverses/identités en plus du produit cartésien.
            normal = [x for x in c23['results'] if x['public'] in c23['publics'] and x['name'] in {p['name'] for p in expected}]
            c23copy = dict(c23,total=len(normal),results=normal)
            check(label+'_c23',c23['publics']==c26.c23.audience_order(f) and c23['total']==len(c23['results']) and c23['leaks']==c23['failures']==0 and c23['routes']==len(expected) and c23['command_sha256']==sha(ROOT/'wp/outils/demo/c23.py') and all(matrix_checks(c23copy,expected,c23['publics']).values()))
            check(label+'_b06_inverse',all(any(x['name']=='b06-'+str(p['id'])+'-'+kind and x['public']=='profil-p-coop' and x['ok'] is True and x['witnesses_found']>0 for x in c23['results']) for p in f['cooperator_pages'] for kind in ['html','rest','rest-route','collection','embed','recherche']))
            check(label+'_policy',c23['discovery']['policy']==f['discovery_policy'] and c23['discovery']['audience']==c26.c23.discovery_audience(f) and (c23['discovery']['exhausted_played'] is False if f['discovery_policy']['ouverture']=='fermee' else c23['discovery']['exhausted_played'] is True))
            if index==0:
                check('normal_not_mutation','mutations_detected' not in r)
            else:
                check('mutation_families',set(r.get('mutations_detected',[]))==set(c26.FAMILIES+['cooperateurs','cooperative']))
                for family in c26.FAMILIES:
                    m = read(label+'-mutation-'+family+'.json')
                    rows = m['results']
                    bad = [x for x in rows if x['family']==family and not x['positive']]
                    check('mutation_'+family,m['route']=='registered-native-exporter-callbacks' and m['mutation']==family and m['total']==len(rows)==len(wanted) and len(bad)==len(publics) and m['failures']==m['leaks']==len(bad) and all(x['leak'] is True and x['ok'] is False and x['witnesses_found']>0 and x['surface_present'] is True for x in bad))
                for family in ['cooperateurs','cooperative']:
                    m = read(label+'-mutation-'+family+'.json')
                    check('mutation_'+family,m.get('persisted_fixture') is True and m['total']==len(m['results'])==1 and all(x['leak'] is True and x['ok'] is False and x['witnesses_found']>0 and x['surface_present'] is True and x['status']==200 and x['bytes']>0 for x in m['results']))
        tests,image = read('tests.json'),read('image.json')
        check('tests',all(tests[k]['exit']==0 and tests[k]['tests']==41 and tests[k]['TMPDIR_present'] is False and tests[k]['network_blocked'] is True and 'Ran 41 tests' in (packet/('tests-'+k+'.log')).read_text(encoding='utf-8') and '\nOK\n' in (packet/('tests-'+k+'.log')).read_text(encoding='utf-8') for k in ['utf8','cp1252']))
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
