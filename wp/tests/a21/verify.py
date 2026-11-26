"""Read-only A21 candidate verifier; never claims the parent readiness gates."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
OWN=['wp/tests/a21','wp/outils/bascule/a21']
DEPENDENCIES=['wp/tests/a02-audit','wp/tests/a19','wp/outils/bascule/audit',
              'wp/outils/bascule/a11','wp/outils/bascule/a12','wp/outils/staging','wp/outils/bascule/stream_guard.py','wp/outils/bascule/stream_refusals.json','wp/outils/bascule/stream_bridge.php','wp/tests/a22/run.py','wp/tests/a22/replay.py','wp/tests/a22/channels.py']

def inventory(roots):
    paths=[]
    for key in roots:
        p=ROOT/key
        paths.extend([p] if p.is_file() else [f for f in p.rglob('*') if f.is_file() and '__pycache__' not in f.parts])
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}

def readme_contract(document,appendix):
    lines=appendix.splitlines(keepends=True)
    return len(lines)==2 and len(set(lines))==2 and all(line.endswith(b'\n') and b'\r' not in line and document.splitlines(keepends=True).count(line)==1 for line in lines)

def packet_manifest(packet):
    expected=inventory(OWN+[packet.relative_to(ROOT).as_posix(),'production/A-21/readme-ajout.txt',
                            'production/A-21/readme-delta.txt','production/A-21/notes.md'])
    expected.pop((packet/'manifest.json').relative_to(ROOT).as_posix(),None)
    return expected

def verify(packet):
    checks=[]
    counts={}
    load=lambda p:json.loads(p.read_text(encoding='utf-8'))
    def check(name,ok):
        checks.append({'check':name,'status':'PASS' if ok else 'FAIL'})
    source=load(packet/'sources.json')
    check('exact_current_sources',source==inventory(OWN))
    dependencies=inventory(DEPENDENCIES)
    # The shared README is verified by its exact lot contract, never a full hash.
    dependencies.pop('wp/tests/a02-audit/README.md',None)
    check('exact_current_dependencies',load(packet/'dependency-snapshot.json')==dependencies)
    required=['fixture_native_readback','a02_audit','documented_three_argument_command','default_clock_actual_utc',
              'keys_exact','webhooks_exact','store_connection_native_boolean','zero_outbound_attempts',
              'no_secrets_fragments_addresses_names_paths','private_permissions','frozen_replay_identical',
              'unconfined_refused','closed_symlink:False','closed_symlink:True','closed_config:define','closed_config:const',
              'closed_invalid_clock','all_tables_scheduler_identical','all_files_identical','config_never_executed',
              'real_kernel_sql_mail_http_cron_guards','guard_probe_database_unchanged','real_neutraliser_observed',
              'neutralised_unknown_not_zero','neutralised_database_unchanged','neutralised_files_unchanged','all_produced_artifacts_canary_absent']
    required += ['output_guard:'+x for x in ['exists','site','repo','ancestor','root']]
    required += ['closed_dropin:'+str(i) for i in range(6)]
    required += [kind+str(i) for kind in ['closed_site_exception:','exception_database_unchanged:'] for i in range(3)]
    required += ['neutralised_supervisor_return']
    required += [kind+label for kind in ['supervised_bootstrap:','hostile_artifacts_absent:',
                 'hostile_confinement_unchanged:'] for label in ['stdout','stderr','early_exit','empty_exit',
                 'forged_success','shutdown_stdout','shutdown_stderr','oversized_stdout','binary_stderr',
                 'shutdown_duplicate_success','shutdown_missing_json','shutdown_artifact_canary']]
    for console,folder in [('cp1252',packet),('utf8',packet/'utf8')]:
        for kind in ['unit','result','runner']:
            data=load(folder/(kind+'.json'))
            names=[r['check'] for r in data['checks']]
            counts[console+':'+kind]=len(names)
            check(console+':'+kind+':green_unique',data['exit_code']==0 and bool(names) and len(names)==len(set(names)) and all(r['status']=='PASS' for r in data['checks']))
        pure=load(folder/'pure-include.json') if (folder/'pure-include.json').is_file() else {}
        check(console+':pure_include_complete',pure.get('count')==counts[console+':unit']
              and all(pure.get(key) is True for key in ['green','quiet','files_unchanged','native_absent']))
        pure_names={r['check'] for r in load(folder/'unit.json')['checks']}
        check(console+':literal_ip_ipv6_pure_cases',{'literal_ipv4_ipv6_external_by_exact_host',
              'literal_ipv6_string_not_dns_or_binary_equivalence','literal_ip_addresses_never_projected'}.issubset(pure_names))
        check(console+':executed_source_snapshot',load(folder/'sources.json')==source)
        check(console+':executed_dependency_snapshot',load(folder/'dependency-snapshot.json')==dependencies)
        names={r['check'] for r in load(folder/'result.json')['checks']}
        for storage in ['classic','hpos']:
            check(console+':'+storage+':required_native_cases',all(storage+':'+name in names for name in required))
            before=load(folder/(storage+'-db-before.json'))
            check(console+':'+storage+':all_table_equality',before==load(folder/(storage+'-db-after.json')) and {'wp_options','wp_wc_webhooks','wp_woocommerce_api_keys','wp_actionscheduler_actions','wp_actionscheduler_logs'}.issubset(before['tables']))
            d=load(folder/(storage+'-portes/portes.json'))
            check(console+':'+storage+':audit_bound',d['schema']=='imagine-a21-external-doors-v1' and d['read_only'] is True and d['storage']==storage and d['audit_sha256']==hashlib.sha256((folder/(storage+'-audit/audit.json')).read_bytes()).hexdigest())
            check(console+':'+storage+':replay_equal',d==load(folder/(storage+'-repeat/portes.json')))
            nd=load(folder/(storage+'-neutralised/portes.json'))
            check(console+':'+storage+':unknown_never_zero',nd['api_keys']=={'status':'inconnu après neutralisation','counts':None} and nd['webhooks']=={'status':'inconnu après neutralisation','counts':None} and nd['extension_store']=={'status':'inconnu après neutralisation','connected':None})
        runner=load(folder/'runner.json')
        channels=load(folder/'a22-channels.json')
        check(console+':common_guard_native_channels_and_mutation',channels['exit_code']==0 and len(channels['checks'])==21 and all(x['status']=='PASS' for x in channels['checks']))
        check(console+':owned_cleanup',runner['mode']=='native' and any(r['check']=='cleanup_exact_owned_runner' and r['status']=='PASS' for r in runner['checks']))
        env=load(packet/(console+'-environment.json'))
        check(console+':windows_console_measured',env['platform']=='win32' and env['version_info'][:2]==[3,14] and env['stdout']==('cp1252' if console=='cp1252' else 'utf-8') and env['utf8_mode']==int(console=='utf8'))
        log=(packet/(console+'-python-tests.log')).read_text(encoding='utf-8')
        tests=re.search(r'Ran (\d+) tests?\b',log)
        counts[console+':python_tests']=int(tests[1]) if tests else 0
        expected_tests=sum(len(re.findall(r'^    def test_',file.read_text(encoding='utf-8'),re.M))
                           for file in (ROOT/'wp/tests/a21').glob('test_*.py'))
        check(console+':portable_python_tests_executed',bool(tests) and counts[console+':python_tests']==expected_tests and '\nOK\n' in log)
    style=load(packet/'style/style.json')
    check('strict_psr12_sources_current',style['exit_code']==style['phpcs_exit']==0 and style['totals']['errors']==style['totals']['warnings']==0 and style['sources']==source)
    matrix=load(packet/'windows-matrix.json')
    check('windows_matrix_actual_green',matrix['exit_code']==0 and len(matrix['rows'])==6 and all(r['exit_code']==0 for r in matrix['rows']))
    candidate=load(packet/'candidate.json')
    check('candidate_not_parent_gate_claim',candidate=={'status':'CANDIDAT_GATE_PARENT','parent_preparation':'pending','parent_global_T01':'pending','readiness_claimed':False})
    check('own_two_shared_lines_only',readme_contract((ROOT/'wp/tests/a02-audit/README.md').read_bytes(),(ROOT/'production/A-21/readme-ajout.txt').read_bytes()))
    check('exact_final_packet_manifest',load(packet/'manifest.json')==packet_manifest(packet))
    result={'status':'CANDIDAT_GATE_PARENT','readiness_claimed':False,'exit_code':int(any(r['status']!='PASS' for r in checks)),'counts':counts,'checks':checks}
    print(json.dumps(result,indent=2))
    return result['exit_code']
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('packet',type=Path)
    args=ap.parse_args()
    try:
        sys.exit(verify(args.packet.resolve()))
    except Exception as error:
        print(json.dumps({'exit_code':1,'error':type(error).__name__}))
        sys.exit(1)
