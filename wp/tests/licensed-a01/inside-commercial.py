"""Targeted commercial behavior only. Runs inside network-none fixture."""
import hashlib,json,pathlib,secrets,shutil,sys,traceback,zipfile,re
import inside as base
from inside import command,wp,wp_json,record,assert_true
ROOT=pathlib.Path('/opt/e2e')
def case(site,phase): return wp_json(site,'cases.php',env={'A01_PHASE':phase})
def rights(site,storage,phase):
    v=case(site,'rights')
    assert_true(v['restricted'],storage+':'+phase+':restriction_real',{'restricted':v['restricted']})
    for name,r in v['rights'].items():
        expected=name=='active'
        assert_true(r['private']==expected and r['public'] and v['shortcodes'][name]==expected,storage+':'+phase+':rights:'+name,{'private':r['private'],'public':r['public'],'shortcode_contains_private':v['shortcodes'][name]})
    return v

def install(storage):
    database='imagine_e2e_'+storage+'_test'
    command(['mariadb','--socket='+base.SOCKET,'--user=root','-e','CREATE DATABASE '+database])
    site=base.SCRATCH/('site-'+storage);shutil.copytree('/opt/wordpress/wordpress',site)
    shutil.copytree('/opt/woocommerce/woocommerce',site/'wp-content/plugins/woocommerce')
    config="""<?php
    define('DB_NAME', '%s');define('DB_USER','root');define('DB_PASSWORD','');define('DB_HOST','localhost:/scratch/mariadb.sock');define('DB_CHARSET','utf8mb4');define('DB_COLLATE','');define('WP_ENVIRONMENT_TYPE','staging');define('WP_HTTP_BLOCK_EXTERNAL',true);define('DISABLE_WP_CRON',true);define('AUTOMATIC_UPDATER_DISABLED',true);define('WP_AUTO_UPDATE_CORE',false);define('WP_DEBUG',false);$table_prefix='wp_';define('ABSPATH',__DIR__.'/');require_once ABSPATH.'wp-settings.php';
    """%database
    (site/'wp-config.php').write_text(config)
    wp(site,['core','install','--url=https://fixture.synthetic.test','--title=Invented commercial fixture','--admin_user=fiction-admin','--admin_email=fiction-admin@example.org','--skip-email','--prompt=admin_password'],input_text=secrets.token_urlsafe(40)+'\n')
    wp(site,['plugin','activate','woocommerce'],timeout=240)
    wp(site,['option','update','woocommerce_custom_orders_table_data_sync_enabled','no'])
    wp(site,['option','update','woocommerce_custom_orders_table_enabled','yes' if storage=='hpos' else 'no'])
    available={}
    # Memberships activation deliberately independent, even if Subscriptions fails.
    for slug in ['woocommerce-memberships','woocommerce-subscriptions']:
        package=ROOT/(slug+'.zip');assert hashlib.sha256(package.read_bytes()).hexdigest()==base.LICENSED[slug+'.zip']
        with zipfile.ZipFile(package) as z:
            for e in z.infolist():
                parts=pathlib.PurePosixPath(e.filename).parts
                assert parts and parts[0]==slug and '..' not in parts and '\\' not in e.filename and ':' not in e.filename and e.external_attr>>16 & 0o170000 in (0,0o040000,0o100000)
            z.extractall(site/'wp-content/plugins')
        p=wp(site,['plugin','activate',slug],check=False,timeout=240)
        available[slug]=p.returncode==0
        record(storage+':activate:'+slug,'PASS' if p.returncode==0 else 'BLOCKED',{'exit':p.returncode,'output_sha256':hashlib.sha256((p.stdout+p.stderr).encode()).hexdigest()})
    if available['woocommerce-subscriptions']:
        wp(site,['option','update','wc_subscriptions_siteurl','_[wc_subscriptions_siteurl]_https://production.synthetic.invalid'])
    return site,database,available

def raw(storage,database):
    # Direct SQL through CLI, no WordPress bootstrap. Only counts/coordinates.
    table='wp_wc_orders' if storage=='hpos' else 'wp_posts'
    predicate="type='shop_subscription'" if storage=='hpos' else "post_type='shop_subscription'"
    n=int(command(['mariadb','--socket='+base.SOCKET,'--user=root','--skip-column-names',database,'-e','SELECT COUNT(*) FROM '+table+' WHERE '+predicate]).stdout.strip())
    assert_true(n==6,storage+':direct_sql_subscription_rows',{'table':table,'rows':n})
    if storage=='hpos':
        p=command(['mariadb','--socket='+base.SOCKET,'--user=root','--skip-column-names',database,'-e',"SELECT a.order_id,a.address_type,a.country FROM wp_wc_order_addresses a JOIN wp_wc_orders o ON a.order_id=o.id WHERE o.type='shop_subscription' ORDER BY a.order_id,a.address_type"])
        coords=p.stdout
        assert_true(len(coords.splitlines())==12,storage+':direct_sql_address_rows',{'rows':len(coords.splitlines())})
        return hashlib.sha256(coords.encode()).hexdigest()
    return None

def scheduled(database):
    p=command(['mariadb','--socket='+base.SOCKET,'--user=root','--skip-column-names',database,'-e',"SELECT status,COUNT(*) FROM wp_actionscheduler_actions WHERE hook LIKE 'woocommerce_scheduled_subscription_%' GROUP BY status ORDER BY status"])
    return {row.split('\t')[0]:int(row.split('\t')[1])for row in p.stdout.splitlines()}

def run_storage(storage):
    site,database,available=install(storage)
    if not available['woocommerce-memberships']: return
    record(storage+':memberships_seed','PASS',case(site,'seed'))
    rights_before=rights(site,storage,'before')
    if not available['woocommerce-subscriptions']:
        record(storage+':subscriptions_scope','BLOCKED','Memberships exercised independently; subscription activation failed');return
    assert_true(case(site,'seed-subscriptions')['created']==6,storage+':subscriptions_seed',{'created':6})
    before=case(site,'snapshot');record(storage+':actual_versions','PASS',before['versions'])
    assert_true(before['versions']['hpos']==(storage=='hpos'),storage+':actual_authoritative_store',before['versions'])
    assert_true(not any(p['email_safe'] for p in before['personal']),storage+':personal_oracle_sensitive',{'outside_domain':6})
    sql_before=raw(storage,database)
    native_before=scheduled(database)
    assert_true(native_before.get('pending',0)>0,storage+':native_subscription_scheduler_seeded',native_before)
    pristine=base.export(database,'before-renewal-control')
    # Real WCS/Action Scheduler callback creates a manual renewal while isolated.
    control=case(site,'renewal')
    assert_true(control['duplicate_site'] and control['callback_calls']==1 and control['status']=='complete' and control['renewals_after']==control['renewals_before']+1,storage+':real_renewal_positive_control',control)
    # Reimport only SQL generated in this same container, restoring original statuses.
    base.restore(database,pristine)
    assert_true(case(site,'snapshot')['business']==before['business'],storage+':renewal_control_rollback','Fixture SQL restored; original subscription business state retained')
    (site/'.imagine-staging-offline').write_text('OFFLINE_COPY\n')
    context=base.SCRATCH/('context-'+storage+'.json')
    context.write_text(json.dumps({'environment':'staging','isolated':True,'restored':True,'database':database,'production_hosts':['production.synthetic.invalid'],'target_url':'https://fixture.synthetic.test','wp_path':str(site)}))
    password=secrets.token_urlsafe(40)
    for name in ['neutraliser','anonymiser','verifier']:
        p=base.subject_command(site,name,password,context)
        if name=='verifier':
            refusal=json.loads(p.stdout)
            pending={t['name']:t['personal_columns']for t in refusal.get('unknown_tables',[])if t.get('personal_columns') and t.get('decision') is None}
            assert_true(p.returncode==1 and refusal.get('issues')==['TABLE_PERSONNELLE_A_TRANCHER'] and pending=={'wp_wc_email_unsubscribes':['email_hash','email_kind']},storage+':new_woo_table_requires_decision',{'issues':refusal.get('issues'),'pending':pending})
            c=json.loads(context.read_text());c['table_decisions']={'wp_wc_email_unsubscribes':{'action':'garder'}};context.write_text(json.dumps(c))
            record(storage+':synthetic_woo_table_decision','PASS',{'table':'wp_wc_email_unsubscribes','action':'garder','decision_is_synthetic_not_Ced_approval':True})
            p=base.subject_command(site,name,password,context)
        detail={'exit':p.returncode,'stdout_sha256':hashlib.sha256(p.stdout.encode()).hexdigest(),'stderr_sha256':hashlib.sha256(p.stderr.encode()).hexdigest()}
        if name=='verifier':
            v=json.loads(p.stdout);detail['issues']=v.get('issues',[]);detail['unknown_personal_tables']=[{'name':t['name'],'columns':t['personal_columns']}for t in v.get('unknown_tables',[])if t.get('personal_columns') and t.get('decision') is None]
        assert_true(p.returncode==0,storage+':subject:'+name,detail)
    native_after=scheduled(database)
    assert_true(native_after.get('pending',0)==0 and native_after.get('in-progress',0)==0 and native_after.get('canceled',0)>=native_before.get('pending',0),storage+':native_subscription_actions_neutralized',{'before':native_before,'after':native_after})
    after=case(site,'snapshot')
    for field in ['business','membership','rules_sha256']:
        assert_true(before[field]==after[field],storage+':preserve:'+field,{'before_sha256':hashlib.sha256(json.dumps(before[field],sort_keys=True).encode()).hexdigest(),'after_sha256':hashlib.sha256(json.dumps(after[field],sort_keys=True).encode()).hexdigest()})
    assert_true(all(all(v for k,v in p.items()if k!='id')for p in after['personal']),storage+':actual_subscription_personal_cleanup',{'subscriptions':len(after['personal']),'checks':after['personal']})
    assert_true(raw(storage,database)==sql_before,storage+':sql_address_coordinates_preserved',{'hpos':storage=='hpos'})
    assert_true(rights(site,storage,'after')==rights_before,storage+':rights_unchanged_after_subject','Fresh plugin bootstrap; API + restrict shortcode')
    runtime=case(site,'runtime')
    assert_true(all(v is True for v in runtime.values()),storage+':actual_runtime_staging_and_locks',runtime)
    canary=site/'wp-content/mu-plugins/zzz-a01-nonstaging-canary.php'
    try:
        # Preserve exact subject MU bytes: its file-integrity guard must remain valid.
        canary.write_text("<?php add_action('plugins_loaded', static function (): void { remove_all_filters('woocommerce_subscriptions_is_duplicate_site'); update_option('wc_subscriptions_siteurl', '_[wc_subscriptions_siteurl]_' . get_option('siteurl')); }, PHP_INT_MAX);\n")
        mutation=case(site,'runtime')
        assert_true(mutation['subscriptions_staging'] is False,storage+':real_nonstaging_canary',mutation)
        p=base.subject_command(site,'verifier',password,context);v=json.loads(p.stdout)
        if p.returncode!=1:
            d=command(['php','/opt/e2e/diagnostic.php'],env={'E2E_CONTEXT':str(context),'WP_ENVIRONMENT_TYPE':'staging'})
            record(storage+':negative_diagnostic','OBSERVED',json.loads(next(l[9:]for l in d.stdout.splitlines()if l.startswith('E2E_JSON='))))
        d=command(['php','/opt/e2e/diagnostic.php'],env={'E2E_CONTEXT':str(context),'WP_ENVIRONMENT_TYPE':'staging','A01_DIAGNOSTIC_ENGINE_ONLY':'1'})
        engine=json.loads(next(l[9:]for l in d.stdout.splitlines()if l.startswith('E2E_JSON=')))
        assert_true('SUBSCRIPTIONS_NON_STAGING' in engine.get('issues',[]),storage+':engine_refuses_actual_nonstaging',engine)
        assert_true(p.returncode!=0,storage+':cli_refuses_nonstaging_copy',{'exit':p.returncode,'issues':v.get('issues',[]),'exact_subscription_tag_from_engine_only':True})
    finally:canary.unlink(missing_ok=True)
    # Purge only synthetic files using the unchanged subject's real file treatment.
    command(['php','-r',"require '/subject/files.php'; (new Imagine\\Staging\\Files($argv[1]))->purge();",str(site)])
    record(storage+':purge_generated_fixture_logs','OBSERVED','Unchanged subject Files::purge replayed after deliberate nonstaging mutation; no source/data changes')
    p=base.subject_command(site,'verifier',password,context);v=json.loads(p.stdout)
    assert_true(p.returncode==0,storage+':final_verifier',{'exit':p.returncode,'issues':v.get('issues',[])})
    blocked=case(site,'renewal')
    assert_true(blocked['callback_calls']==0 and blocked['renewals_after']==blocked['renewals_before'] and blocked['status']=='failed' and blocked['cron_empty'] and blocked['async_disabled'] and blocked['runner_removed'],storage+':renewal_scheduler_blocked',blocked)
    record(storage+':post_deliberate_scheduler_attempt_files','OBSERVED',{'generated_logs':[str(p.relative_to(site))for p in site.rglob('*.log')]})

def main():
    process=None
    try:
        process=base.database_start()
        for filename in ['cases.php']:
            command(['php','-l',str(ROOT/filename)])
        for storage in ['classic','hpos']:
            try:run_storage(storage)
            except Exception as e:
                record(storage+':exception','FAIL',{'class':type(e).__name__,'message':str(e)[-5000:],'frames':[{'file':pathlib.Path(f.filename).name,'line':f.lineno,'function':f.name}for f in traceback.extract_tb(e.__traceback__)]})
        base.isolation()
    finally:
        if process:process.terminate();process.wait(timeout=30)
        result={'suite':'A01-actual-commercial-behavior','checks':base.CHECKS,'exit_code':1 if any(c['status'] in ['FAIL','BLOCKED']for c in base.CHECKS)else 0,'no_real_data':True,'no_license_or_account_connection':True,'operator_import_ready':False,'files_import_fidelity_tested':False}
        (pathlib.Path('/report')/'commercial-result.json').write_text(json.dumps(result,indent=2)+'\n')
    return result['exit_code']
if __name__=='__main__':sys.exit(main())
