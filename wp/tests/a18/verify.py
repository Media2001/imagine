"""Read-only final packet verifier; no sealing or verdict writes."""
import argparse,hashlib,json,re,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3];LOT=Path(__file__).resolve().parent.name;UP='A-'+LOT[1:]
OWN=['wp/tests/'+LOT,'wp/outils/bascule/'+LOT]
def inventory(roots):
    paths=[p for key in roots for p in (ROOT/key).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
def verify(packet,candidate=False):
    checks=[];load=lambda p:json.loads(p.read_text(encoding='utf-8'))
    def check(name,ok):checks.append({'check':name,'status':'PASS' if ok else 'FAIL'})
    source=load(packet/'sources.json');check('exact_current_sources',source==inventory(OWN));counts={}
    required=['cli_and_actual_readonly_guards','media_contents_never_opened','exact_group:account:_a18_card','exact_group:account:_a18_rr','exact_group:order:_a18_bank','exact_group:subscription:_a18_bank','exact_group:option:a18_bank_setting','invalid_and_canary_values_not_counted','tokens_references_separate','known_and_other_folders_exact','no_values_names_ids_or_paths','replay_identical','unconfined_refused','all_tables_scheduler_identical','files_identical','config_not_executed','neutralised_unknown_not_zero','neutralised_database_unchanged','rule_presence_not_false_assurance','rule_variant_files_unchanged','all_produced_artifacts_canary_absent','symlink_private_code_only:False','symlink_private_code_only:True']
    required += ['plugin_exception_code_closed','plugin_exception_variant_database_unchanged']
    required += ['closed_dropin:'+str(i) for i in range(6)]
    required += ['r1_inactive_store:order','r1_inactive_store:subscription','r1_physical_rows_not_logical_dedup','r1_closed_store_labels','r2_card:scan_to_groups','r2_register:scan_to_groups','r3_card:scan_to_groups','r3_iban:scan_to_groups']
    required_unit=['memo_iban_registry_single_load','national_11_digits_not_a_card']
    required_unit += ['r3_'+form+'_scan_to_groups_'+label for form in ['iban','card'] for label in ['multiple_spaces','line_feed','tabs','crlf','nbsp','narrow_nbsp']]
    required_unit += ['r2_'+form+'_'+side for form,sides in [('card',['trailing_digits','leading_digits','both_sides']),('register',['trailing_year','leading_year','both_sides'])] for side in sides]
    required_unit += ['r2_no_arbitrary_fragment_'+label for label in ['card_contiguous_suffix','card_contiguous_prefix','register_contiguous_suffix','register_contiguous_prefix','card_attached_letters','register_attached_letters']]
    for console,folder in [('cp1252',packet),('utf8',packet/'utf8')]:
        for kind in ['unit','result','runner']:
            data=load(folder/(kind+'.json'));names=[r['check'] for r in data['checks']];counts[console+':'+kind]=len(names)
            check(console+':'+kind+'_green_unique',data['exit_code']==0 and bool(names) and len(names)==len(set(names)) and all(r['status']=='PASS' for r in data['checks']))
        check(console+':executed_source_snapshot',load(folder/'sources.json')==source)
        check(console+':required_unit_regressions',set(required_unit).issubset({r['check'] for r in load(folder/'unit.json')['checks']}))
        native=load(folder/'result.json');names={r['check'] for r in native['checks']}
        for storage in ['classic','hpos']:
            check(console+':'+storage+':required_native_cases',all(storage+':'+key in names for key in required))
            before=load(folder/(storage+'-db-before.json'));after=load(folder/(storage+'-db-after.json'))
            check(console+':'+storage+':all_table_equality',before==after and {'wp_options','wp_actionscheduler_actions','wp_actionscheduler_logs'}.issubset(before['tables']))
            data=load(folder/(storage+'-retention/conservation.json'))
            check(console+':'+storage+':audit_bound',data['read_only'] is True and data['storage']==storage and data['audit_sha256']==hashlib.sha256((folder/(storage+'-audit/audit.json')).read_bytes()).hexdigest())
        runner=load(folder/'runner.json');check(console+':cleanup_owned_runner',runner['mode']=='native' and any(r['check']=='cleanup_exact_owned_runner' and r['status']=='PASS' for r in runner['checks']))
        deps=load(folder/'dependency-snapshot.json');check(console+':common_refusal_runtime_unchanged',deps['wp/outils/bascule/a11/Runtime.php']==hashlib.sha256((ROOT/'wp/outils/bascule/a11/Runtime.php').read_bytes()).hexdigest())
    style=load(packet/'style/style.json');check('strict_psr12_current_sources',style['exit_code']==style['phpcs_exit']==0 and style['totals']['errors']==style['totals']['warnings']==0 and style['sources']==source)
    if candidate:
        gate=load(packet/'parent-gate.json')
        check('candidate_parent_gate_explicitly_pending',gate['status']=='pending_parent' and not (ROOT/'production/A-18/PRET').exists() and not (packet/'preparation.json').exists())
    else:
        prepared=(packet/'preparation.json').is_file() and (packet/'preparation.log').is_file()
        prep=load(packet/'preparation.json') if prepared else {}
        check('preparer_image_actual_exit',prepared and prep.get('exit_code')==0 and prep.get('command',[''])[-1]=='wp/tests/preparer-image.ps1' and 'image verifiee' in (packet/'preparation.log').read_text(encoding='utf-8'))
    matrix=load(packet/'windows-matrix.json');check('matrix_actual_green',matrix['exit_code']==0 and len(matrix['rows'])==4 and all(r['exit_code']==0 for r in matrix['rows']))
    for console in ['utf8','cp1252']:
        env=load(packet/(console+'-environment.json'));check(console+':windows_measured_console',env['platform']=='win32' and env['version'].startswith('3.14.') and env['stdout']==env['stderr']==('cp1252' if console=='cp1252' else 'utf-8') and env['utf8_mode']==int(console=='utf8'))
        check(console+':python_launcher_tests_actual', 'Ran 3 tests' in (packet/(console+'-launcher-tests.log')).read_text(encoding='utf-8') and '\nOK\n' in (packet/(console+'-launcher-tests.log')).read_text(encoding='utf-8'))
    appendix=(ROOT/'production'/UP/'readme-ajout.txt').read_bytes().splitlines(keepends=True);doc=(ROOT/'wp/tests/a02-audit/README.md').read_bytes().splitlines(keepends=True)
    check('own_two_shared_readme_lines',len(appendix)==2 and all(doc.count(line)==1 for line in appendix))
    expected=inventory(OWN+[packet.relative_to(ROOT).as_posix()]);expected.pop((packet/'manifest.json').relative_to(ROOT).as_posix(),None)
    check('exact_final_packet_manifest',load(packet/'manifest.json')==expected)
    result={'exit_code':int(any(r['status']!='PASS' for r in checks)),'mode':'candidate_without_parent_gate' if candidate else 'full','pending_gates':['parent_preparer_image','parent_independent_verification'] if candidate else [],'check_count':len(checks),'counts':counts,'checks':checks};print(json.dumps(result,indent=2));return result['exit_code']
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('packet',type=Path);parser.add_argument('--candidate',action='store_true');a=parser.parse_args()
    try:sys.exit(verify(a.packet.resolve(),a.candidate))
    except Exception as error:print(json.dumps({'exit_code':1,'error':type(error).__name__}));sys.exit(1)
