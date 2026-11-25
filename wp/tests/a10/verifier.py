"""Parent-executable A10 verifier; hashes, named native checks and optional real replay."""
import argparse
import hashlib
import importlib.util
import json
import pathlib
import re
import subprocess
import sys
sys.dont_write_bytecode=True
HERE=pathlib.Path(__file__).resolve().parent
REPO=HERE.parents[2]
spec=importlib.util.spec_from_file_location('a10runner',HERE/'run.py')
r=importlib.util.module_from_spec(spec); spec.loader.exec_module(r)

def require(ok,message):
    if not ok: raise RuntimeError(message)

def load(path):
    return json.loads(path.read_text(encoding='utf8'))

def verify(evidence):
    require(evidence.is_dir(),'EVIDENCE_MISSING')
    receipt=load(evidence/'runner.json')
    require(receipt['exit_code']==0 and receipt['mode']=='native','NOT_A_GREEN_NATIVE_RUN')
    sources=load(evidence/'sources.json')
    require(sources==r.manifest(),'SOURCE_CONTENT_OR_INVENTORY_DRIFT')
    unit=load(evidence/'unit.json'); native=load(evidence/'result.json')
    require(native['suite']=='A10-native-coupon-inventory-on-A02-bench','WRONG_NATIVE_SUITE')
    for packet in [receipt,unit,native]:
        require(packet['checks'] and packet['exit_code']==0 and all(c['status']=='PASS' for c in packet['checks']),'NON_GREEN_CHECK')
        names=[x['check'] for x in packet['checks']]
        require(len(names)==len(set(names)),'DUPLICATE_ASSERTION_NAMES')
    names={x['check'] for x in native['checks']}
    for storage in ['classic','hpos']:
        for check in ['cli_success','native_renewal_carries_coupon','exact_inventory','distinct_subscription_counts','exact_12month_orders','privacy','database_identical_all_tables','site_files_identical','never_bootstrap','root_transaction_write_denied','guard:canonical_repository','guard:dynamic_config','guard:storage_mismatch']:
            require(storage+':'+check in names,'MISSING_NATIVE_ASSERTION:'+storage+':'+check)
        before=load(evidence/(storage+'-db-before.json')); after=load(evidence/(storage+'-db-after.json'))
        require(before==after and before['tables'],'DATABASE_FINGERPRINT_MISMATCH')
        require(any('actionscheduler_actions' in name for name in before['tables']) and any(name.endswith('options') for name in before['tables']),'SCHEDULER_NOT_IN_FINGERPRINT')
        data=load(evidence/(storage+'-codes/codes.json'))
        require(data['schema']=='imagine-a10-coupons-v1' and data['read_only'] is True and data['storage']==storage,'REPORT_CONTRACT')
        require(re.fullmatch(r'[a-f0-9]{64}',data['audit_sha256']) is not None,'AUDIT_HASH_MISSING')
        audit=evidence/(storage+'-audit/audit.json')
        require(hashlib.sha256(audit.read_bytes()).hexdigest()==data['audit_sha256'],'AUDIT_BINDING_DRIFT')
        rows={x['code']:x for x in data['codes']}
        oracle=load(evidence/(storage+'-oracle.json'))
        require(len(rows)==10 and set(rows)==set(oracle['expected']),'INVENTORY_COUNT')
        require(oracle['renewal_carries_coupon'] is True,'NO_NATIVE_RENEWAL')
        require(len(oracle['native_source_sha256'])==4 and all(re.fullmatch('[a-f0-9]{64}',x) for x in oracle['native_source_sha256'].values()),'NATIVE_SOURCE_HASHES')
        for code,expected in oracle['expected'].items():
            require(all(rows[code].get(k)==v for k,v in expected.items()),'NATIVE_GETTER_MISMATCH:'+code)
        rec=rows['a10-recurring-fee']
        require(rec['subscriptions']=={'active':1,'on_hold':1,'pending':1,'pending_cancel':1} and rec['orders_12_months']==5,'CARRIER_COUNTS')
        require(data['expired']==['a10-expired','a10-expired-never-used'] and data['never_used']==['a10-expired-never-used','a10-never-used'],'SEPARATE_LISTS')
        text=(evidence/(storage+'-codes/codes.json')).read_text()+(evidence/(storage+'-codes/codes.md')).read_text()
        require(re.search(r'@|PRIVATE_CANARY|customer_id|user_id|billing_|subscription_id|order_id',text) is None,'PRIVACY_LEAK')
        require(load(evidence/(storage+'-repeat/codes.json'))['codes']==data['codes'],'REPLAY_BUSINESS_DRIFT')
    # The only authorized A02 change is the exact two-line byte appendix.
    original,actual=r.a02_manifest()
    appendix=(REPO/'production/A-10/readme-ajout.txt').read_bytes()
    readme='wp/tests/a02-audit/README.md'
    current=(REPO/readme).read_bytes()
    require(len(appendix.splitlines())==2 and current.endswith(appendix),'README_APPENDIX')
    actual[readme]=hashlib.sha256(current[:-len(appendix)]).hexdigest()
    require(actual==original,'A02_ACCEPTED_SOURCES_CHANGED')
    preparation=load(REPO/'production/A-10/preparation/receipt.json')
    require(preparation['exit_code']==0,'T01_PREPARATION_NOT_GREEN')
    require(hashlib.sha256((REPO/'wp/tests/preparer-image.ps1').read_bytes()).hexdigest()==preparation['script_sha256'],'PREPARATION_SCRIPT_DRIFT')
    require(hashlib.sha256((REPO/'production/A-10/preparation/preparer-image.log').read_bytes()).hexdigest()==preparation['log_sha256'],'PREPARATION_LOG_DRIFT')
    # Inspect only this packet's exact owned name; never list/remove other containers.
    missing=r.b.call(['inspect',receipt['container']],check=False)
    require(missing.returncode!=0 and re.search(r'no such (object|container)',missing.stderr,re.I),'OWNED_CONTAINER_NOT_CONFIRMED_ABSENT')
    ledger=REPO/'production/A-10/manifest.json'
    if ledger.exists():
        payload=load(ledger)
        for relative,sha in payload['files'].items():
            file=REPO/relative
            require(file.is_file() and hashlib.sha256(file.read_bytes()).hexdigest()==sha,'SEALED_ARTIFACT_DRIFT:'+relative)
        require(payload['sources']==sources,'SEALED_SOURCE_MANIFEST_DRIFT')
    return {'evidence':evidence.relative_to(REPO).as_posix(),'exit_code':0,'unit_assertions':len(unit['checks']),'native_assertions':len(native['checks']),'runner_assertions':len(receipt['checks']),'source_files':len(sources),'a02_original_bytes_preserved':True,'cleanup_verified':True}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('evidence',nargs='?')
    ap.add_argument('--replay',action='store_true')
    args=ap.parse_args()
    if args.replay:
        p=subprocess.run([sys.executable,str(HERE/'run.py')],capture_output=True,text=True)
        require(p.returncode==0,'REAL_REPLAY_FAILED:'+p.stdout[-2000:])
        path=pathlib.Path(json.loads(p.stdout)['evidence'])
    elif args.evidence:
        path=pathlib.Path(args.evidence)
        if not path.is_absolute(): path=REPO/path
    else:
        pret=(REPO/'production/A-10/PRET').read_text().splitlines()[0]
        match=re.fullmatch('PRET([a-f0-9]{12})',pret)
        require(match is not None,'INVALID_PRET_POINTER')
        path=REPO/'production/A-10/preuves'/match[1]
    print(json.dumps(verify(path),indent=2))
if __name__=='__main__':
    try: main()
    except Exception as exc:
        print(json.dumps({'exit_code':1,'error':str(exc)})); sys.exit(1)
