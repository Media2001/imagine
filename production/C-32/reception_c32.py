"""Réception C32 corrigée ; aucun appel site en mode --local."""
import sys
sys.dont_write_bytecode = True
import hashlib
import importlib.util
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'wp/outils/demo'), str(ROOT/'wp/tests/demo')]
import c32 as owner
import c32_browser_policy as policy
s = importlib.util.spec_from_file_location('contract', ROOT/'wp/tests/demo/b13-contract.py')
c = importlib.util.module_from_spec(s)
s.loader.exec_module(c)
OUT = owner.OUT
RECEIPT = 'reception-corrections-V2.json'
LOCAL = 'corrections-local-final-V2.json'
NATIVE = 'native-corrections-V2.json'
BROWSER = 'browser-corrections-V2.json'
STRICT = 'strict-reading-corrections-V2.json'
STANDARD = 'standard-corrections-V2.json'
IMAGE = 'image-corrections-V2.json'
REPLAY = 'replay-corrections-V2.json'
OFFICIAL = 'official-corrections-V2.json'


def load(name):
    return json.loads((OUT/name).read_text(encoding='utf-8'))


def verify_local():
    local = load(LOCAL)
    assert local['scope']=='C32_LOCAL_OFFLINE_ONLY' and local['pass']
    assert local['live_validated'] is local['global_replay'] is local['image_prepared'] is False
    assert {r['name'] for r in local['runs']}=={'image-inspect', 'python', 'php-lint', 'phpunit', 'python-syntax'}
    for path, digest in local['sources'].items():
        assert c.core.digest(ROOT/path)==digest, 'Preuve locale périmée : '+path
    with c.bound(owner):
        section = c.core.section('C32')
    assert hashlib.sha256(section.encode()).hexdigest()==local['readme_section']
    for run in local['runs']:
        assert run['exit']==0 and c.core.digest(OUT/run['log'])==run['log_sha256']
    php = (OUT/next(r['log'] for r in local['runs'] if r['name']=='phpunit')).read_text(encoding='utf-8')
    py = (OUT/next(r['log'] for r in local['runs'] if r['name']=='python')).read_text(encoding='utf-8')
    assert re.search(r'OK \(\d+ tests?, \d+ assertions?\)', php)
    assert re.search(r'Ran \d+ tests?', py) and '\nOK\n' in py
    answer = {'C32':'PASS_LOCAL_OFFLINE_ONLY', 'live_validated':False, 'global_replay':False, 'image_prepared':False, 'receipt':LOCAL}
    print(json.dumps(answer, ensure_ascii=False))
    return answer


def verify_browser(data):
    assert data['sources']==owner.sources(owner)
    extension_path = ROOT/'production/C-26/mutations-livraison-extension.json'
    extension = json.loads(extension_path.read_text(encoding='utf-8'))
    assert data['c26_extension_sha256']==c.core.digest(extension_path)
    f = data['public_inventory']
    paths = policy.public_paths(f['fixture'], f['pages'], extension)
    reading = [row for row in data['rows'] if row['kind']=='lecture']
    coverage = policy.coverage([row['path'] for row in reading], paths)
    assert coverage['pass'] and data['public_coverage']==coverage
    expected = {'page_liste_unique', 'page_texte_vide', 'connexion_liste_fermee', 'connexion_native_reussie', 'mutation_header_mutation_detectee', 'mutation_script_mutation_detectee', 'aucun_tiers', policy.STRICT_CHECK, 'lecture_ecart_natif_borne', 'couverture_publique_identique'}
    for i in range(1, len(paths)+1):
        expected.update('lecture_'+str(i)+'_'+suffix for suffix in ['200', 'liste_fermee', 'etanche', 'ecart_natif_borne'])
    for i, kind in enumerate(['code', 'panier', 'langue'], len(paths)+1):
        expected.update(kind+'_'+str(i)+'_'+suffix for suffix in ['200', 'liste_fermee', 'etanche'])
        expected.add(kind+'_cookies_natifs_observes')
    assert set(data['checks'])==expected and data['total']==len(expected)
    inventory_checks = expected-{policy.STRICT_CHECK}
    assert len(data['inventory_checks'])==len(inventory_checks) and set(data['inventory_checks'])==inventory_checks
    assert all(data['checks'][name] for name in inventory_checks)
    verdict = policy.reading_verdict(data['rows'])
    assert data['reading']==verdict and verdict['inventory_pass']
    strict_ok = verdict['strict_pass']
    assert data['checks'][policy.STRICT_CHECK] is strict_ok and data['zero_cookie_reading'] is strict_ok
    assert data['verdicts']=={'inventory':'PASS', 'strict_zero_cookie':'PASS' if strict_ok else 'FAIL'}
    assert len(data['rows'])==len(paths)+6
    assert sorted(r['kind'] for r in data['rows'] if r['kind']!='lecture')==['code', 'connexion', 'langue', 'mutation_header', 'mutation_script', 'panier']
    for row in data['rows']:
        if row['kind'].startswith('mutation_'):
            assert row['unknown']==['c32_sonde_hors_liste']
        else:
            assert row['status']==200 and not row['unknown']
        if row['kind']=='lecture':
            assert row['zero_cookie_expected'] is True
            assert row['zero_cookie_pass'] is (not row['header_names'] and not row['browser'])
    assert data['error'] is None and data['restored'] and data['sessions_restored'] and data['probe_removed'] and not data['external']
    assert data['sessions_cleanup']=={'restored':True, 'foreign_changes':0, 'write_conflicts':0, 'owned_remaining':0}
    return verdict


def verify(live=False, manifest=None, require_pret=True, strict_mode=False):
    c.integrity(owner, manifest if manifest is not None else load(RECEIPT))
    verify_local()
    native = load(NATIVE)
    result = json.loads(native['native']['stdout'])
    assert native['sources']==owner.sources(owner) and native['restored'] and native['before']==native['after'] and native['native']['code']==0 and not native['native']['stderr']
    assert result['total']==len(result['checks'])==21 and all(result['checks'].values())
    browser = load(BROWSER)
    reading = verify_browser(browser)
    strict = load(STRICT)
    assert strict=={'status':'PASS' if reading['strict_pass'] else 'FAIL', 'expected':0, 'pages':reading['pages'], 'observed_cookie_names':reading['observed_names'], 'native_order_attribution_unchanged':True, 'browser_receipt':BROWSER}
    standard = load(STANDARD)
    assert standard['sources']==owner.sources(owner) and len(standard['official'])==3 and standard['native']['attribution']=='yes'
    official = load(OFFICIAL)
    assert official['pass'] and len(official['official'])==5 and official['demo_accessed'] is False
    image = load(IMAGE)
    assert image['exit']==0 and 'image verifiee sha256:' in (OUT/image['log']).read_text(encoding='utf-8')
    replay = load(REPLAY)
    text = (OUT/replay['log']).read_text(encoding='utf-8')
    matches = re.findall(r'^T01_RESULT (.+)$', text, re.M)
    assert replay['exit']==0 and len(matches)==1 and 'CookiesC32Test' in text
    r = json.loads(matches[0])
    assert r['pass'] and r['tests']>0 and r['assertions']>0 and r['failures']==r['errors']==r['skipped']==r['tools']['failures']==0
    assert all(x['lot'] in ['A-32', 'A-33', 'A-34'] for x in r['packets']['failures'])
    if require_pret:
        assert RECEIPT in (OUT/'PRET').read_text(encoding='utf-8')
    if live:
        owner.guard()
        import b06
        assert b06.hashes(owner.FILES)=={name:c.core.digest(ROOT/'wp'/name) for name in owner.FILES}
        with c.bound(owner):
            c.core.live_registration('C32', owner.wp, owner.php)
    answer = {'C32':'PASS_INVENTAIRE', 'simple_lecture_zero_cookie':strict['status'], 'native':result['total'], 'browser':browser['total'], 'pages':reading['pages'], 'tests':r['tests'], 'assertions':r['assertions'], 'tools':r['tools'], 'packets':r['packets']}
    print(json.dumps(answer, ensure_ascii=False))
    if strict_mode:
        assert reading['strict_pass'], 'Aucun cookie en lecture : FAIL ; inventaire séparé'
    return answer


def main():
    args = sys.argv[1:]
    assert len(args)==len(set(args)) and set(args)<={'--local', '--live', '--strict'}
    if '--local' in args:
        assert args==['--local']
        verify_local()
    else:
        verify('--live' in args, strict_mode='--strict' in args)
