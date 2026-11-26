"""Read-only final packet verifier; no sealing or verdict writes."""
import argparse,hashlib,json,re,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3];LOT=Path(__file__).resolve().parent.name;UP='A-'+LOT[1:]
OWN=['wp/tests/'+LOT,'wp/outils/bascule/'+LOT,'wp/plugins/imagine-pilotage/tests/Administration/A19SubscriptionCoherenceTest.php']
def inventory(roots):
    paths=[]
    for key in roots:
        root=ROOT/key
        paths.extend([root] if root.is_file() else [p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts])
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}
def verify(packet):
    checks=[];load=lambda p:json.loads(p.read_text(encoding='utf-8'))
    def check(name,ok):checks.append({'check':name,'status':'PASS' if ok else 'FAIL'})
    source=load(packet/'sources.json');check('exact_current_sources',source==inventory(OWN));counts={}
    required=['native_fixture_relationships', 'cli_and_actual_readonly_guards', 'all_counts_explained', 'no_account_subscription_order_identifiers_names_paths', 'private_output_permissions', 'replay_identical', 'unconfined_refused', 'all_tables_scheduler_identical', 'files_identical', 'config_not_executed', 'unknown_reference_not_counted_absent', 'unknown_variant_database_unchanged', 'all_produced_artifacts_canary_absent', 'symlink_private_code_only:False', 'symlink_private_code_only:True', 'config_private_code_only:define', 'config_private_code_only:const', 'invalid_clock_code_only', 'exact_count:cross', 'exact_count:subscriptions_without_membership', 'exact_count:memberships_without_subscription', 'exact_count:memberships_missing_subscription', 'exact_count:multiple_active_subscription_accounts', 'exact_count:multiple_active_membership_accounts', 'exact_count:multiple_active_membership_accounts_by_plan', 'exact_count:automatic_without_saved_payment', 'exact_count:automatic_payment_reference_unknown', 'exact_count:active_past_next_payment', 'exact_count:active_without_paid_order', 'exact_count:manual_by_gateway']
    required += ['explicit_clock_retained','three_paths_without_date_native','default_clock_is_current_utc','default_clock_single_frozen_reference','repeated_clock_refused']
    required += ['plugin_exception_code_closed','plugin_exception_variant_database_unchanged']
    required += ['closed_dropin:'+str(i) for i in range(6)]
    for console,folder in [('cp1252',packet),('utf8',packet/'utf8')]:
        for kind in ['unit','result','runner']:
            data=load(folder/(kind+'.json'));names=[r['check'] for r in data['checks']];counts[console+':'+kind]=len(names)
            check(console+':'+kind+'_green_unique',data['exit_code']==0 and bool(names) and len(names)==len(set(names)) and all(r['status']=='PASS' for r in data['checks']))
        check(console+':executed_source_snapshot',load(folder/'sources.json')==source)
        native=load(folder/'result.json');names={r['check'] for r in native['checks']}
        for storage in ['classic','hpos']:
            check(console+':'+storage+':required_native_cases',all(storage+':'+key in names for key in required))
            before=load(folder/(storage+'-db-before.json'));after=load(folder/(storage+'-db-after.json'))
            check(console+':'+storage+':all_table_equality',before==after and {'wp_options','wp_actionscheduler_actions','wp_actionscheduler_logs'}.issubset(before['tables']))
            data=load(folder/(storage+'-coherence/coherence.json'))
            check(console+':'+storage+':audit_bound',data['read_only'] is True and data['storage']==storage and data['audit_sha256']==hashlib.sha256((folder/(storage+'-audit/audit.json')).read_bytes()).hexdigest())
            default=load(folder/(storage+'-default-clock/coherence.json'));frozen=load(folder/(storage+'-default-frozen/coherence.json'))
            check(console+':'+storage+':default_and_explicit_frozen_reports_identical',default==frozen and default['counts']==data['counts'] and default['audit_sha256']==data['audit_sha256'] and re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z',default['as_of_utc']) is not None)
        runner=load(folder/'runner.json');check(console+':cleanup_owned_runner',runner['mode']=='native' and any(r['check']=='cleanup_exact_owned_runner' and r['status']=='PASS' for r in runner['checks']))
        deps=load(folder/'dependency-snapshot.json');check(console+':common_refusal_runtime_unchanged',deps['wp/outils/bascule/a11/Runtime.php']==hashlib.sha256((ROOT/'wp/outils/bascule/a11/Runtime.php').read_bytes()).hexdigest())
    style=load(packet/'style/style.json');check('strict_psr12_current_sources',style['exit_code']==style['phpcs_exit']==0 and style['totals']['errors']==style['totals']['warnings']==0 and style['sources']==source)
    candidate=load(packet/'candidate.json');check('candidate_only_parent_gate_not_claimed',candidate['status']=='CANDIDAT_GATE_PARENT' and candidate['parent_preparation']=='pending' and candidate['parent_global_T01']=='pending')
    t01=load(packet/'t01/t01.json');counts['t01:rules']=len(t01['cases'])
    check('t01_current_sources_and_genuine_nine_cases',t01['exit_code']==0 and t01['sources']==source and len(t01['cases'])==9 and all(c['status']=='PASS' for c in t01['checks']))
    from xml.etree import ElementTree as ET
    junit=ET.parse(packet/'t01/t01-junit.xml');cases=junit.findall('.//testcase')
    check('t01_junit_nine_assertions_zero_skipped',len(cases)==9 and [c.get('name') for c in cases]==t01['cases'] and sum(int(c.get('assertions','0')) for c in cases)==9 and not any(junit.findall('.//'+tag) for tag in ['failure','error','skipped']))
    matrix=load(packet/'windows-matrix.json');check('matrix_actual_green',matrix['exit_code']==0 and len(matrix['rows'])==4 and all(r['exit_code']==0 for r in matrix['rows']))
    for console in ['utf8','cp1252']:
        env=load(packet/(console+'-environment.json'));check(console+':windows_measured_console',env['platform']=='win32' and env['version'].startswith('.'.join(map(str,env['version_info']))) and env['version_info'][:2]==[3,14] and env['stdout']==('cp1252' if console=='cp1252' else 'utf-8') and env['utf8_mode']==int(console=='utf8'))
        check(console+':python_launcher_tests_actual', 'Ran 5 tests' in (packet/(console+'-launcher-tests.log')).read_text(encoding='utf-8') and '\nOK\n' in (packet/(console+'-launcher-tests.log')).read_text(encoding='utf-8'))
    appendix=(ROOT/'production'/UP/'readme-ajout.txt').read_bytes().splitlines(keepends=True);doc=(ROOT/'wp/tests/a02-audit/README.md').read_bytes().splitlines(keepends=True)
    check('own_two_shared_readme_lines',len(appendix)==2 and all(doc.count(line)==1 for line in appendix))
    expected=inventory(OWN+[packet.relative_to(ROOT).as_posix()]);expected.pop((packet/'manifest.json').relative_to(ROOT).as_posix(),None)
    check('exact_final_packet_manifest',load(packet/'manifest.json')==expected)
    result={'status':'CANDIDAT_GATE_PARENT','readiness_claimed':False,'exit_code':int(any(r['status']!='PASS' for r in checks)),'counts':counts,'checks':checks};print(json.dumps(result,indent=2));return result['exit_code']
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('packet',type=Path);a=parser.parse_args()
    try:sys.exit(verify(a.packet.resolve()))
    except Exception as error:print(json.dumps({'exit_code':1,'error':type(error).__name__}));sys.exit(1)
