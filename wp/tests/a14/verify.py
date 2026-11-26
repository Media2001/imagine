"""Verify one sealed A14 packet; no Docker/PHP/network on the verifier host."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
OWN=['wp/tests/a14','wp/outils/bascule/a14','wp/outils/bascule/rapprocher-contacts','wp/tests/fixtures/a14-contacts-fictifs.csv']

def inventory(roots):
    paths=[]
    for key in roots:
        p=ROOT/key;paths.extend([p] if p.is_file() else [x for x in p.rglob('*') if x.is_file()])
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths) if '__pycache__' not in p.parts}

def verify(packet):
    checks=[]
    def check(name,ok):checks.append({'check':name,'status':'PASS' if ok else 'FAIL'})
    sources=json.loads((packet/'sources.json').read_text())
    check('exact_owned_sources_inventory',sources==inventory(OWN))
    for name in ['unit','runner','result']:
        d=json.loads((packet/(name+'.json')).read_text())
        check(name+'_green',d['exit_code']==0 and bool(d['checks']) and all(c['status']=='PASS' for c in d['checks']))
        if name=='runner':check('native_runner_required',d['mode']=='native' and any(x['check']=='cleanup_exact_owned_runner' for x in d['checks']))
    style=json.loads((packet/'style/style.json').read_text())
    check('strict_psr12_after_last_write',style['exit_code']==0 and style['phpcs_exit']==0 and style['totals']['errors']==style['totals']['warnings']==0 and style['sources']==sources)
    prep=json.loads((packet/'preparation.json').read_text())
    check('preparer_image_really_ran',prep['exit_code']==0 and prep['command'][-1]=='wp/tests/preparer-image.ps1' and 'image verifiee' in (packet/'preparation.log').read_text(encoding='utf-8'))
    for storage in ['classic','hpos']:
        before=json.loads((packet/(storage+'-db-before.json')).read_text());after=json.loads((packet/(storage+'-db-after.json')).read_text())
        check(storage+'_all_tables_equal',before==after and bool(before['tables']))
        data=json.loads((packet/(storage+'-contacts/resume.json')).read_text())
        c=data['counts'];check(storage+'_counts_partition',c['contacts_total']==sum(c[k] for k in ['contacts_with_account','contacts_without_account','ambiguous_contact_lines','invalid_contact_lines']))
    manifest=json.loads((packet/'manifest.json').read_text())
    expected=inventory(OWN+[packet.relative_to(ROOT).as_posix()])
    expected.pop((packet/'manifest.json').relative_to(ROOT).as_posix(),None)
    check('sealed_exact_owned_and_packet',manifest==expected)
    check('no_foreign_lot_pinned',all(k.startswith(tuple(OWN+[packet.relative_to(ROOT).as_posix()+'/'])) for k in manifest))
    result={'exit_code':int(any(x['status']!='PASS' for x in checks)),'checks':checks}
    print(json.dumps(result,indent=2));return result['exit_code']

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('packet',type=Path);a=ap.parse_args()
    try:sys.exit(verify(a.packet.resolve()))
    except Exception as e:print(json.dumps({'exit_code':1,'error':type(e).__name__}));sys.exit(1)
