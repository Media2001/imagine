"""Read-only A20 candidate verifier; does not seal evidence or claim parent gates."""
import argparse,hashlib,json,re,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
OWN=['wp/tests/a20','wp/outils/bascule/a20']
def inventory(roots):
    files=[]
    for key in roots:
        p=ROOT/key
        files.extend([p] if p.is_file() else [x for x in p.rglob('*') if x.is_file() and '__pycache__' not in x.parts])
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(files))}
def verify(packet,parent_proof=None):
    checks=[];counts={}
    def check(name,ok):checks.append({'check':name,'status':'PASS' if ok else 'FAIL'})
    def load(p):return json.loads(p.read_text(encoding='utf-8'))
    source=load(packet/'sources.json');check('exact_current_owned_sources',source==inventory(OWN))
    required=['commercial_fixture','native_fixture','a02_audit','native_confined_success','exact_product_counts','all_counts_explained',
        'privacy_no_names_paths_ids_rare_amount_country','private_output_permissions','replay_identical',
        'documented_command_only_given_arguments','unconfined_refused','transaction_readonly_even_root',
        'audit_guard:schema','audit_guard:storage','all_tables_scheduler_identical','files_identical','config_not_executed',
        'plugin_exception_closed','exception_database_identical','all_artifacts_canary_absent']
    required+=['guard:'+x for x in ['exists','site','repo','ancestor','root']]
    required+=['symlink_closed:'+x for x in ['False','True']]+['closed_dropin:'+str(i) for i in range(6)]
    required+=['config_closed:'+x for x in ['define','const']]
    required+=['exact:'+x for x in ['live_subscriptions','multiple_product_lines','without_product_line','with_fee_line',
        'with_shipping_line','foreign_currency','zero_recurring_total','countries','other_countries','unknown_country']]
    required+=['closed_'+kind+':'+label for kind in ['process','artifacts'] for label in ['forged_success','invalid_utf8_stream','shutdown_invalid_json','report_extra_field','markdown_extra','direct_stdout','direct_stderr','echo_exit','silent_exit','die_message','shutdown_stdout','shutdown_stderr','shutdown_echo','shutdown_partial','shutdown_extra_file']]
    for console in ['utf8','cp1252']:
        base=packet/console;folder=base/'native'
        env=load(base/'environment.json')
        check(console+':measured_windows_console',env['platform']=='win32' and env['version_info'][:2]==[3,14]
            and env['stdout']==('utf-8' if console=='utf8' else 'cp1252') and env['stderr']==env['stdout']
            and env['utf8_mode']==int(console=='utf8'))
        tests=(base/'launcher-tests.log').read_text(encoding='utf-8')
        check(console+':thirty_four_python_tests',re.search(r'Ran 34 tests in ',tests) is not None and '\nOK\n' in tests)
        for kind,total in [('unit',23),('result',158),('runner',9)]:
            d=load(folder/(kind+'.json'));names=[c['check'] for c in d['checks']];counts[console+':'+kind]=len(names)
            check(console+':'+kind+'_all_pass',d['exit_code']==0 and len(names)==total and len(names)==len(set(names)) and all(x['status']=='PASS' for x in d['checks']))
        check(console+':sources_really_executed',load(folder/'sources.json')==source)
        check(console+':pure_relocated_identical',load(folder/'relocated-unit.json')==load(folder/'unit.json') and (folder/'pure.log').read_text(encoding='utf-8')=='A20_PURE_OK 23\n')
        result=load(folder/'result.json');native={r['check']:r for r in result['checks']}
        for storage in ['classic','hpos']:
            prefix=console+':'+storage
            check(prefix+':all_named_cases',all(storage+':'+key in native for key in required))
            before=load(folder/(storage+'-db-before.json'));after=load(folder/(storage+'-db-after.json'))
            check(prefix+':independent_all_tables_equality',before==after and {'wp_options','wp_actionscheduler_actions','wp_actionscheduler_logs'}.issubset(before['tables']))
            files=native[storage+':files_identical']['detail'];check(prefix+':file_hash_equality',files['before']==files['after'] and re.fullmatch('[a-f0-9]{64}',files['before']) is not None)
            report=load(folder/(storage+'-prices/tarifs.json'));v=report['counts']
            check(prefix+':audit_bound_storage',report['read_only'] is True and report['storage']==storage and report['audit_sha256']==hashlib.sha256((folder/(storage+'-audit/audit.json')).read_bytes()).hexdigest())
            check(prefix+':exact_live_and_products',v['live_subscriptions']==8 and len(v['products'])==2 and [p['count'] for p in v['products']]==[7,2] and v['products'][0]['non_annual']==1 and v['zero_recurring_total']==v['foreign_currency']==v['multiple_product_lines']==v['with_fee_line']==1 and v['with_shipping_line']==2)
            check(prefix+':rare_amounts_and_countries_hidden',v['products'][0]['amounts']==[{'currency':'EUR','amount':'100.00','count':5}] and all(p['other_amounts']==2 for p in v['products']) and v['products'][1]['amounts']==[] and v['countries']==[{'country':'BE','count':5,'with_shipping':0}] and v['other_countries']=={'count':2,'with_shipping':2})
            for dest in ['repeat','documented','root-readonly']:
                check(prefix+':'+dest+'_same_report',load(folder/(storage+'-'+dest+'/tarifs.json'))==report)
            payload=''.join(p.read_text(encoding='utf-8') for p in (folder/(storage+'-prices')).iterdir())
            check(prefix+':report_private_values_absent',re.search(r'CANARY|@|/scratch|9\.17|80\.19|1234567\.89|"(?:FR|DE|US)"|"(?:user|customer|order_id|subscription_id|id)"',payload) is None)
            for top in ['live_subscriptions','products','countries','other_countries','unknown_country','multiple_product_lines','without_product_line','with_fee_line','with_shipping_line','foreign_currency','zero_recurring_total']:
                check(prefix+':definition:'+top,bool(v['definitions'].get(top)))
        runner=load(folder/'runner.json');check(console+':owned_cleanup_and_purity',runner['mode']=='native' and all(any(x['check']==key and x['status']=='PASS' for x in runner['checks']) for key in ['cleanup_exact_owned_runner','pure_no_extensions_no_writes','temporary_layout_pure_receipt_identical','isolation_before','isolation_after']))
        import importlib.util
        spec=importlib.util.spec_from_file_location('a20_runner',ROOT/'wp/tests/a20/run.py')
        runner_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner_module)
        deps=load(folder/'dependency-snapshot.json');check(console+':all_executed_dependencies_unchanged',deps==runner_module.manifest(runner_module.DEPENDENCIES))
        channels=load(folder/'a22-channels.json')
        check(console+':common_guard_native_channels_and_mutation',channels['exit_code']==0 and len(channels['checks'])==21 and all(x['status']=='PASS' for x in channels['checks']))
    style=load(packet/'style/style.json');check('strict_psr12_current_sources',style['exit_code']==style['phpcs_exit']==0 and style['totals']['errors']==style['totals']['warnings']==0 and style['sources']==source)
    matrix=load(packet/'windows-matrix.json');check('both_console_suites_executed',matrix['exit_code']==0 and len(matrix['rows'])==5 and all(r['exit_code']==0 for r in matrix['rows']))
    check('all_retained_artifacts_canary_absent',not any(b'CANARY' in p.read_bytes() for p in packet.rglob('*') if p.is_file()))
    # Candidate proof is historical; a later parent PRET must not invalidate it.
    candidate=load(packet/'candidate.json');check('parent_gates_explicitly_pending',candidate=={'status':'CANDIDAT_GATE_PARENT','parent_preparation':'pending','parent_global_T01':'pending','readiness_claimed':False})
    lines=(ROOT/'production/A-20/readme-ajout.txt').read_text(encoding='utf-8').splitlines();shared=(ROOT/'wp/tests/a02-audit/README.md').read_text(encoding='utf-8').splitlines();check('only_own_two_shared_lines',len(lines)==2 and all(shared.count(line)==1 for line in lines))
    expected=inventory(OWN+[packet.relative_to(ROOT).as_posix()]);expected.pop((packet/'manifest.json').relative_to(ROOT).as_posix(),None)
    check('exact_packet_inventory_and_hashes',load(packet/'manifest.json')==expected)
    if parent_proof is not None:
        proof=load(parent_proof)
        check('optional_parent_sources_current',proof['sources']==source)
        for gate in ['preparation','T01']:
            receipt=load(Path(proof[gate]));rows=[row for key in ['checks','tests'] for row in receipt.get(key,[])]
            check('optional_parent_'+gate,receipt.get('exit_code')==0 and bool(rows) and all(row.get('status')=='PASS' if 'status' in row else row.get('ok') is True for row in rows))
    result={'status':'CANDIDAT_GATE_PARENT','readiness_claimed':False,'exit_code':int(any(c['status']!='PASS' for c in checks)),'counts':counts,'checks':checks}
    print(json.dumps(result,indent=2));return result['exit_code']
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('packet',type=Path);ap.add_argument('--parent-proof',type=Path);a=ap.parse_args()
    try:sys.exit(verify(a.packet.resolve(),a.parent_proof))
    except Exception:print(json.dumps({'exit_code':1,'code':'A20_PACKET_INVALID'}));sys.exit(1)
