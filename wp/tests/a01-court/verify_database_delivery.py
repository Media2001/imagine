"""Read-only final A01/3 receipts/source/cleanup verification. No site access."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode = True
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'wp/outils/staging-court'))
import publish


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser()
    for key in ('unit','e2e','global_log','ntfs_log'): p.add_argument('--'+key.replace('_','-'),required=True)
    args=p.parse_args()
    paths={k:(ROOT/getattr(args,k)).resolve() for k in ('unit','e2e','global_log','ntfs_log')}
    assert all(v.is_relative_to(ROOT/'production/A-01') for v in paths.values())
    unit=json.loads(paths['unit'].read_bytes()); e2e=json.loads(paths['e2e'].read_bytes())
    assert unit['status']==e2e['status']=='PASS'
    assert unit['cleanup']['absent'] is e2e['cleanup']['absent'] is True
    assert unit['sources_unchanged'] is e2e['sources_unchanged'] is True
    sources={**unit['source_manifest'],**e2e['source_manifest']}
    for rel,sha in sources.items():
        assert digest(ROOT/rel)==sha,'SOURCE_DRIFT:'+rel
    log=(paths['unit'].parent/'tests.log').read_text()
    count=int(re.search(r'Ran (\d+) tests',log)[1])
    assert count==100 and 'OK (skipped=1)' in log and 'FAILED' not in log
    new_tests=len(re.findall(r'^test_.*\(test_archive_reelle_3\.',log,re.M))
    assert new_tests==9
    ntfs=paths['ntfs_log'].read_text(); assert 'Ran 1 test' in ntfs and '\nOK' in ntfs and 'skipped' not in ntfs
    global_text=paths['global_log'].read_text()
    totals=json.loads(re.search(r'^T01_RESULT (\{.*\})$',global_text,re.M)[1])
    assert totals=={'tests':1012,'assertions':34006,'failures':0,'errors':0,'skipped':0,'pass':True}
    v=e2e['verification']
    assert e2e['native_policy_exit']==e2e['prepare_exit']==e2e['verify_exit']==v['diagnostic_exit']==0
    assert e2e['native_regression']['ok'] is True and e2e['native_regression']['cases']==9
    assert v['status']=='PASS' and len(v['cases'])==2
    assert all(c['data_verified'] and c['status']=='PASS' and not c['independent_residue_scan']['sentinel_residue'] for c in v['cases'])
    assert e2e['real_export']['plugin_version']=='7.109'
    assert e2e['fixture']['blob_bytes']==283
    assert v['actual_table_decisions_cli']['family_override_readback'] is True
    assert v['extra_literal_roundtrip']['status']=='PASS'
    assert all(n==0 for n in v['cases'][0]['tables'].values())
    assert len(v['cases'][0]['tables'])==11
    assert all(c['runtime']['mail_blocked'] is True for c in v['cases'])
    # Every runner created by this pass, including red attempts, by exact receipt name.
    names={unit['cleanup']['name'],e2e['cleanup']['name']}
    for result in (ROOT/'production/A-01/archive-reelle-3').glob('*/result.json'):
        r=json.loads(result.read_bytes())
        assert r['name'].startswith('imagine-test-a01-db3-')
        names.add(r['name'])
    for result in (ROOT/'production/A-01/archive-reelle').glob('*/result.json'):
        r=json.loads(result.read_bytes())
        if 'wp/tests/a01-court/test_archive_reelle_3.py' in r.get('source_manifest',{}):
            names.add(r['isolation_before']['name'])
    for file in (ROOT/'production/A-01').glob('archive-reelle-3-global*.log'):
        names.update(re.findall(r'absence verifiee de (imagine-t01-[a-f0-9]+)',file.read_text()))
    absent=[]
    for name in sorted(names):
        reply=publish.call(['inspect',name],check=False)
        assert reply.returncode!=0 and re.search(rb'no such (?:object|container)',reply.stderr,re.I),name
        absent.append(name)
    paths_to_hash=[ROOT/r for r in sources if r.startswith('wp/')]
    paths_to_hash += [Path(__file__), ROOT/'wp/outils/staging-court/README.md',ROOT/'production/A-01/archive-reelle-3-notes.md']
    manifest={str(f.relative_to(ROOT)).replace('\\','/'):digest(f) for f in sorted(set(paths_to_hash))}
    result={'status':'PASS','recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'scope':'A01/3 offline code qualification only; no real archive, site API or publication',
            'receipts':{k:str(v.relative_to(ROOT)).replace('\\','/') for k,v in paths.items()},
            'receipt_sha256':{k:digest(v) for k,v in paths.items()},
            'a01_unit':{'run':count,'passed':count-1,'failed':0,'skipped_linux_windows_branch':1,'new_tests':new_tests,'ntfs_complement_passed':1},
            'global':totals,'new_composer_package':False,'image_rebuild_required':False,
            'native_regression':{k:e2e['native_regression'][k] for k in ('ok','cases','assertions')},
            'real_extension':{'version':'7.109','sha256':e2e['plugin_sha256'],'wordpress':e2e['real_export']['wordpress'],'php':e2e['real_export']['php']},
            'proof':{'cases':2,'unknown_tables_empty_default':11,'blob_bytes':283,'blob_sha256':e2e['fixture']['blob_sha256'],
                     'default_skipped_inserts':v['default_skipped_inserts'],'actual_cli_override':True,
                     'real_export_literal_forms':v['real_export_blob_literal_forms'],'extra_literal_roundtrip':True,
                     'scans':[c['independent_residue_scan'] for c in v['cases']]},
            'owned_runner_absence_readback':absent,'source_manifest':manifest,
            'limits':['No Imagine archive access','No new HTTP publication or commercial-plugin qualification',
                      'Unknown editorial emails outside recognised operational options remain warnings',
                      'Kept SQL statements limited to 16 MiB; closed literal grammar; no charset/bit/function fallback',
                      'Large-volume receipts from the previous pass remain historical']}
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
