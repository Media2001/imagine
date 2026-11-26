"""Final read-only source, privacy, native-coverage and manifest verifier."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3];LOT=Path(__file__).resolve().parent.name;UP='A-'+LOT[1:]
OWN=['wp/tests/'+LOT,'wp/outils/bascule/'+LOT]
def inventory(roots):
    paths=[p for key in roots for p in ([ROOT/key] if (ROOT/key).is_file() else (ROOT/key).rglob('*')) if p.is_file() and '__pycache__' not in p.parts]
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
def verify(packet):
    checks=[]
    def check(name,ok):checks.append({'check':name,'status':'PASS' if ok else 'FAIL'})
    load=lambda p:json.loads(p.read_text(encoding='utf-8'))
    source=load(packet/'sources.json');check('exact_current_sources',source==inventory(OWN))
    counts={}
    for name in ['unit','result','runner']:
        d=load(packet/(name+'.json'));names=[x['check'] for x in d['checks']];counts[name]=len(names)
        check(name+'_actual_green_unique',d['exit_code']==0 and bool(names) and len(names)==len(set(names)) and all(x['status']=='PASS' for x in d['checks']))
    native=load(packet/'result.json');names={x['check'] for x in native['checks']}
    common=['cli_and_actual_readonly_guards','replay_identical','unconfined_refused','dropin_named_no_execution','all_tables_scheduler_identical','files_identical','config_not_executed']
    required=common+['exact_role_and_security_counts','no_identity_secret_in_outputs','unknown_2fa_not_zero','known_2fa_adapter','actual_configuration_not_runtime_forced_values','isolated_management_roles_included_content_excluded','exact_boundary_not_old_and_future_unknown','coexisting_2fa_supported_scope_not_global_total','no_last_login_native_unknown_not_estimated','real_neutralisation_erases_application_passwords','neutralised_application_passwords_unknown_never_zero','neutralised_all_tables_and_files_readonly']
    for storage in ['classic','hpos']:
        check(storage+'_mandatory_cases',all(storage+':'+key in names for key in required))
        before=load(packet/(storage+'-db-before.json'));after=load(packet/(storage+'-db-after.json'));check(storage+'_all_table_snapshots',before==after and {'wp_options','wp_actionscheduler_actions','wp_actionscheduler_logs'}.issubset(before['tables']))
        folder=packet/(storage+('-issues' if LOT=='a16' else '-security'));d=load(folder/('numeros.json' if LOT=='a16' else 'securite.json'))
        check(storage+'_audit_bound',d['read_only'] is True and d['storage']==storage and d['audit_sha256']==hashlib.sha256((packet/(storage+'-audit/audit.json')).read_bytes()).hexdigest())
        payload=''.join(p.read_text(encoding='utf-8') for p in folder.iterdir());check(storage+'_privacy',not re.search(r'CANARY|@|DB_PASSWORD|/scratch',payload))
    refusal=load(packet/'refusal-common/refusal-common.json');rr=load(packet/'refusal-common/refusal-runner.json')
    expected_cases={lot+':'+case for lot in ['a11','a12','a14','a15','a16','a17'] for case in ['symlink-file','symlink-directory','config-define','config-const','wp-content/db.php','wp-content/object-cache.php','wp-content/advanced-cache.php','wp-content/sunrise.php','wordfence-waf.php','.user.ini']}
    check('six_real_refusal_boundaries_exact_coverage',refusal['exit_code']==rr['exit_code']==0 and {x['check'] for x in refusal['checks']}==expected_cases and all(x['status']=='PASS' for x in refusal['checks']))
    check('common_runtime_executed_current_bytes',rr['sources']['wp/outils/bascule/a11/Runtime.php']==hashlib.sha256((ROOT/'wp/outils/bascule/a11/Runtime.php').read_bytes()).hexdigest())
    for storage in ['classic','hpos']:
        provenance=load(packet/(storage+'-neutralisation.json'));neutral=load(packet/(storage+'-neutralised/securite.json'));no_login=load(packet/(storage+'-no-last-login/securite.json'))
        check(storage+'_real_import_provenance_and_unknown',provenance['application_password_rows_before']==1 and provenance['application_password_rows_after']==0 and provenance['neutralisation_marker_count']==1 and provenance['neutraliser_and_anonymiser_executed'] is True and all(r['application_password_accounts']=='inconnu après neutralisation' for r in neutral['roles']))
        check(storage+'_neutralised_database_readonly',load(packet/(storage+'-neutralised-db-before.json'))==load(packet/(storage+'-neutralised-db-after.json')))
        check(storage+'_no_last_login_exact_unknown',no_login['last_login_adapter']=='inconnu' and all(r['last_login']=={'status':'inconnu','no_recent_record':None,'unknown_accounts':r['accounts']} for r in no_login['roles']))
        for suffix in ['security','unknown','no-last-login','neutralised','repeat']:
            payload=''.join(p.read_text(encoding='utf8') for p in (packet/(storage+'-'+suffix)).iterdir())
            check(storage+'_all_variants_private:'+suffix,not re.search(r'CANARY|@|user_login|user_pass|a17-fictif|/scratch',payload))
    runner=load(packet/'runner.json');check('native_runner_cleanup',runner['mode']=='native' and any(x['check']=='cleanup_exact_owned_runner' and x['status']=='PASS' for x in runner['checks']))
    style=load(packet/'style/style.json');check('strict_psr12_final_sources',style['exit_code']==style['phpcs_exit']==0 and style['totals']['errors']==style['totals']['warnings']==0 and style['sources']==source)
    prep=load(packet/'preparation.json');check('preparer_image_executed',prep['exit_code']==0 and prep['command'][-1]=='wp/tests/preparer-image.ps1' and 'image verifiee' in (packet/'preparation.log').read_text(encoding='utf-8'))
    matrix=load(packet/'windows-matrix.json');check('windows_utf8_and_cp1252_matrix',matrix['exit_code']==0 and all(x['exit_code']==0 for x in matrix['rows']) and {x['environment']['PYTHONIOENCODING'] for x in matrix['rows']}=={'utf-8','cp1252'})
    for console in ['utf8','cp1252']:
        env=load(packet/(console+'-environment.json'));check(console+'_native_python_and_measured_encoding',env['version'].startswith('3.14.7') and env['stdout']==('cp1252' if console=='cp1252' else 'utf-8') and env['utf8_mode']==int(console=='utf8'))
    appendix=(ROOT/'production'/UP/'readme-ajout.txt').read_bytes().splitlines(keepends=True);doc=(ROOT/'wp/tests/a02-audit/README.md').read_bytes().splitlines(keepends=True);check('own_two_readme_lines_only',len(appendix)==2 and all(doc.count(x)==1 for x in appendix))
    manifest=load(packet/'manifest.json');expected=inventory(OWN+[packet.relative_to(ROOT).as_posix()]);expected.pop((packet/'manifest.json').relative_to(ROOT).as_posix(),None);check('exact_packet_manifest',manifest==expected)
    result={'exit_code':int(any(x['status']!='PASS' for x in checks)),'counts':counts,'checks':checks};print(json.dumps(result,indent=2));return result['exit_code']
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('packet',type=Path);a=ap.parse_args()
    try:sys.exit(verify(a.packet.resolve()))
    except Exception as e:print(json.dumps({'exit_code':1,'error':type(e).__name__}));sys.exit(1)
