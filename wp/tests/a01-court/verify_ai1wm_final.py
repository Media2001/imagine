"""Verify the A-01/2 receipts/current hashes; never open an input archive."""
import argparse
import ast
import datetime
import hashlib
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'wp/outils/staging-court'))
import publish


def counts(path):
    text=path.read_text(encoding='utf-8')
    assert '\nFAILED (' not in text and '\nOK' in text
    run=int(re.search(r'Ran (\d+) tests',text)[1])
    match=re.search(r'OK \(skipped=(\d+)\)',text)
    skipped=int(match[1]) if match else 0
    return {'run':run,'executed_passed':run-skipped,'skipped_platform_branches':skipped,'failures':0,'errors':0}


def verify(qualification):
    qualification=qualification.resolve()
    assert qualification.is_relative_to(ROOT/'production/A-01/archive-reelle-2')
    result=json.loads(qualification.read_bytes())
    folder=qualification.parent
    prepared=json.loads((folder/'prepare.json').read_bytes())
    assert result['status']=='PASS' and result['synthetic_only'] and result['sources_unchanged']
    assert prepared['status']=='PREPARED' and prepared['created'] and prepared['name']==result['name']
    for rel,digest in result['source_manifest'].items():
        assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==digest, 'SOURCE_DRIFT:'+rel
    assert result['native_file_policy_exit']==0 and all(row['exit']==0 for row in result['units'])
    assert result['capacity_preflight']['before_any_creation'] and result['capacity_test_synthetic_host_directory_removed']
    assert result['capacity_preflight']['free_bytes']>=result['capacity_preflight']['required_bytes']
    assert result['sanitized_dump_pipe']['exact_counts_and_content_bytes'] is True
    assert result['sanitized_dump_pipe']['total_content_bytes']>128*1024**2
    cases=result['subject']['cases']
    assert len(cases)==2 and {row['case'] for row in cases}=={'small','large'}
    for case in cases:
        assert case['status']=='PASS' and case['diagnostic_exit']==0
        assert case['root_prefix']=='.' and case['eof_v2']
        assert case['payload_never_read'] and case['excluded_read_guard_intervals']>0
        assert case['streamed_sql_import'] and case['native_three_phases_pass']
        assert case['real_manifest_plugins_theme_restored']
        assert case['genuine_generated_png_validated']
        assert case['diagnostic_memory_limit_bytes']==256*1024**2
        assert case['summary_lines']<=25
        diag=case['diagnostic']; native=case['native_offline']
        assert diag['complete'] and not diag['blockers'] and diag['read_only']
        assert diag['extracted_files']==diag['downloads']==0 and diag['created_sites']==[]
        assert any(row['code']=='SECRET_OU_IDENTIFIANT' and not row['blocking'] for row in diag['rules'])
        assert native['data_verified'] and native['status']=='verified-offline'
        assert native['manifest_settings_restored_readback']==['active_plugins','stylesheet','template']
        assert [(row['phase'],row['exit']) for row in native['steps']]==[('neutraliser',0),('anonymiser',0),('verifier',0)]
        assert all(row['report']['ok'] for row in native['steps'])
        assert prepared[case['case']]['plugin_version']=='7.109'
        assert prepared[case['case']]['steps'][0]=='Ai1wm_Export_Init::execute'
        assert prepared[case['case']]['steps'][-1]=='Ai1wm_Export_Clean::execute'
    small=next(row for row in cases if row['case']=='small')
    assert {row['flag'] for row in small['cli_limits']}=={'--max-bytes','--max-entries','--max-sql-bytes'}
    assert all(row['exit']==1 and row['archive_limit'] for row in small['cli_limits'])
    large=next(row for row in cases if row['case']=='large')
    diag=large['diagnostic']
    media=sum(row['bytes'] for row in diag['inventory']['uploads'] if row['directory']=='2026')
    assert diag['entries']>30000 and media>1024**3 and diag['database_bytes']>128*1024**2
    assert large['restored_generated_posts']==1500
    cleanups=[]
    # Exact names were created by these receipts, never by a global scan.
    for run in ('da5698b02266','8f6e3d24930d',folder.name):
        owned=ROOT/'production/A-01/archive-reelle-2'/run
        p=json.loads((owned/'prepare.json').read_bytes())
        c=json.loads((owned/'cleanup.json').read_bytes())
        assert p['created'] and c['name']==p['name'] and c['absent']
        process=publish.call(['inspect',c['name']],check=False)
        assert process.returncode!=0 and ('no such object: '+c['name']).encode() in process.stderr.lower()
        cleanups.append(c)
    unit=next(row for row in result['units'] if row['key']=='archive')
    harness=next(row for row in result['units'] if row['key']=='harness')
    test_path=ROOT/'wp/tests/a01-court/test_archive_reelle_2.py'
    methods=[node.name for node in ast.walk(ast.parse(test_path.read_text())) if isinstance(node,ast.FunctionDef) and node.name.startswith('test_')]
    assert len(methods)==6
    for method in methods:
        assert re.search(r'^'+method+r'.*\.\.\. ok$',(folder/unit['log']).read_text(),re.M)
    assert (ROOT/'production/A-01/PRET-archive-reelle-23nov-historique-avant-archive-reelle-2.txt').is_file()
    return {'status':'PASS','scope':'A-01 archive-reelle-2; no real data or site publication',
        'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'qualification':str(qualification.relative_to(ROOT)).replace('\\','/'),
        'qualification_sha256':hashlib.sha256(qualification.read_bytes()).hexdigest(),
        'host':counts(ROOT/'production/A-01/archive-reelle-2-host-livraison.log'),
        'linux':counts(folder/unit['log']),'harness':counts(folder/harness['log']),
        'native_data':next(row['receipt'] for row in result['units'] if row['key']=='data'),
        'new_test_methods':len(methods),'real_exports':len(cases),
        'large':{'entries':diag['entries'],'archive_bytes':large['archive_bytes'],'media_bytes':media,'database_bytes':diag['database_bytes'],
                 'generated_posts_restored':large['restored_generated_posts'],'summary_lines':large['summary_lines'],
                 'diagnostic_memory_limit_bytes':large['diagnostic_memory_limit_bytes']},
        'owned_resources_removed':cleanups,'no_real_archive':True,'new_full_publication_executed':False,
        'source_manifest':result['source_manifest']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qualification',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    target=args.output.resolve()
    assert target.is_relative_to(ROOT/'production/A-01') and not target.exists()
    result=verify(args.qualification)
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({key:result[key] for key in ('status','host','linux','harness','large','new_test_methods')},ensure_ascii=False))


if __name__=='__main__':
    main()
