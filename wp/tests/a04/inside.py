"""A04 isolated real fixture; imports the existing bench read-only."""
import hashlib
import importlib.util
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tarfile
import time
import zipfile
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('a03','/opt/a03/inside.py');a03=importlib.util.module_from_spec(spec);spec.loader.exec_module(a03)
OUT=pathlib.Path('/report');ROOT=pathlib.Path('/opt/a04')
CHECKS=[]
def check(name,ok,detail=None):
    CHECKS.append({'check':name,'ok':bool(ok),'detail':detail});print(json.dumps(CHECKS[-1]),flush=True)
    if not ok:raise AssertionError(name)
def sha(p):
    with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def package_version(p,file,core=False):
    import re
    with zipfile.ZipFile(p) as z:s=z.read(file).decode()
    return re.search(r"\$wp_version\s*=\s*'([^']+)'" if core else r'^\s*\*?\s*Version:\s*([0-9.]+)',s,re.M|re.I)[1]
def update(site,plan,backup,state,extra=None):
    return a03.cmd(['python3','-B','/subject/mettre-a-jour','--wp-path='+str(site),'--plan='+str(plan),'--backup='+str(backup),'--state='+str(state)]+(extra or []),check=False,timeout=600)
def run_storage(storage):
    # Redirect only fixture dependency paths in memory; existing bench files remain unchanged.
    source='/opt/woocommerce/woocommerce';old=ROOT/'woocommerce-11.0.1.zip';old_version=None
    original=shutil.copytree
    baseline_core=ROOT/'baseline-core'
    if not (baseline_core/'wordpress').is_dir():
        with zipfile.ZipFile(ROOT/'wordpress-7.0.zip') as z:z.extractall(baseline_core)
    if old.is_file():
        old_version=package_version(old,'woocommerce/woocommerce.php')
        if not (ROOT/'baseline/woocommerce').is_dir():
            with zipfile.ZipFile(old) as z:z.extractall(ROOT/'baseline')
        def copy(src,dst,*args,**kwargs):
            selected = ROOT/'baseline/woocommerce' if str(src)==source else baseline_core/'wordpress' if str(src)=='/opt/wordpress/wordpress' else src
            return original(selected,dst,*args,**kwargs)
        shutil.copytree=copy
    try:site,db,seed,config,settings=a03.install(storage)
    finally:shutil.copytree=original
    a03.wp(site,['eval',"require_once WC_ABSPATH . 'includes/admin/wc-admin-functions.php'; wc_memberships()->get_lifecycle_handler()->init(); WC_Subscriptions_Upgrader::upgrade();"])
    rest=site/'wp-content/plugins/a04-rest/fiction-entry.php';rest.parent.mkdir()
    rest_source='<?php\n/*\nPlugin Name: Fiction A04 files only\nVersion: 1.0.0\nRequires PHP: 8.2\nRequires at least: 7.0\n*/\n'
    rest.write_text(rest_source);a03.wp(site,['plugin','activate','a04-rest/fiction-entry.php'])
    rest_zip=ROOT/(storage+'-rest.zip')
    with zipfile.ZipFile(rest_zip,'w') as z:z.writestr('a04-rest/fiction-entry.php',rest_source.replace('Version: 1.0.0','Version: 2.0.0'))
    old_file=site/'wp-content/plugins/woocommerce/a04-old-file-kept.txt';old_file.write_text('Fiction A04 preserve unlisted file')
    themes_before=a03.filemap(site/'wp-content/themes')
    check(storage+':baseline_versions',bool(seed['versions']),seed['versions'])
    log_path=json.loads(settings.read_text())['php_error_log']
    server=subprocess.Popen(['php','-d','log_errors=1','-d','display_errors=0','-d','date.timezone=UTC','-d','error_log='+log_path,'-S','127.0.0.1:18803','-t',str(site)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    time.sleep(.5)
    def readonly():
        (site/'wp-config.php').write_text(config.replace("define('DB_USER', 'root')","define('DB_USER', 'a03_"+storage+"')"))
    try:
        readonly();p=a03.snapshot(site,settings,OUT/(storage+'-before'))
        check(storage+':a03_before',p.returncode==0,{'exit':p.returncode,'code':p.stderr[:150]})
        photo_before=json.loads((OUT/(storage+'-before/non-regression.json')).read_text())
        check(storage+':a03_before_php_log_clean',photo_before['php_log']['checked'] is True and photo_before['php_log']['errors']==0,photo_before['php_log'])
        (site/'wp-config.php').write_text(config)
        # Explicit disposable file + DB backups, never any external archive or input.
        backup_dir=ROOT/('backup-'+storage);backup_dir.mkdir()
        sql=backup_dir/'database.sql'
        exported=a03.cmd(['mariadb-dump','--socket=/scratch/mariadb.sock','-uroot','--single-transaction',db]);sql.write_text(exported.stdout)
        files=backup_dir/'content.tar'
        with tarfile.open(files,'w') as tar:tar.add(site,arcname='site')
        backup=ROOT/(storage+'-backup.json')
        backup_doc={'site':str(site),'created_at':int(time.time()),'database':{'path':str(sql),'sha256':sha(sql)},'files':{'path':str(files),'sha256':sha(files)}};write(backup,backup_doc)
        versions=seed['versions'];target_core=package_version('/opt/compatible-public/wordpress.zip','wordpress/wp-includes/version.php',True)
        target_wc=package_version('/opt/compatible-public/woocommerce.zip','woocommerce/woocommerce.php')
        keys=['core','woocommerce','woocommerce-subscriptions','woocommerce-memberships'];before=[versions['wordpress'],versions['woocommerce'],versions['subscriptions'],versions['memberships']]
        after=[target_core,target_wc,versions['subscriptions'],versions['memberships']]
        archives=['/opt/compatible-public/wordpress.zip','/opt/compatible-public/woocommerce.zip','/opt/a03/woocommerce-subscriptions.zip','/opt/a03/woocommerce-memberships.zip']
        keys.append('a04-rest');before.append('1.0.0');after.append('2.0.0');archives.append(str(rest_zip))
        audit_file=ROOT/(storage+'-rest-audit.md')
        audit_file.write_text('# Audit fictif A-04 : a04-rest\n\nFichier principal : fiction-entry.php.\nLes versions source et cible ne contiennent que cet en-tête PHP sans hook, SQL, cron, batch ou tâche Action Scheduler ; aucune migration différée.\nSHA-256 source : '+hashlib.sha256(rest_source.encode()).hexdigest()+'\nSHA-256 cible : '+hashlib.sha256(rest_source.replace('Version: 1.0.0','Version: 2.0.0').encode()).hexdigest()+'\n',encoding='utf8')
        steps=[{'component':k,'main_file':None if k=='core' else 'fiction-entry.php' if k=='a04-rest' else k+'.php','before':v,'after':t,'archive':p,'sha256':sha(p),'adapter':k if k in keys[:4] else 'bootstrap-only','hooks':[]} for k,v,t,p in zip(keys,before,after,archives)]
        steps[-1]['audit']={'component':'a04-rest','path':str(audit_file),'sha256':sha(audit_file),'conclusion':'no-deferred-database-migrations'}
        plan=ROOT/(storage+'-plan.json');write(plan,{'schema':'imagine-a04-v1','site_status':'verified-staging','steps':steps})
        shutil.copyfile(plan,OUT/(storage+'-plan.json'));shutil.copyfile(audit_file,OUT/(storage+'-rest-audit.md'))
        # Prove guards before the first update, with actual filesystem readbacks.
        denied=update(site,plan,backup,ROOT/(storage+'-no-maintenance'))
        check(storage+':maintenance_required',denied.returncode==1 and denied.stderr=='A04_MAINTENANCE\n')
        maintenance=site/'.maintenance';maintenance.write_text('<?php $upgrading = '+str(int(time.time()))+';\n')
        bad=ROOT/(storage+'-stale.json');bad_doc={**backup_doc,'created_at':int(time.time())-21601};write(bad,bad_doc)
        denied=update(site,plan,bad,ROOT/(storage+'-stale'))
        check(storage+':stale_backup_refused',denied.returncode==1 and denied.stderr=='A04_BACKUP_AGE\n')
        audit_bytes=audit_file.read_bytes();audit_file.write_text('altered fictitious audit')
        audit_state=ROOT/(storage+'-bad-audit')
        denied=update(site,plan,backup,audit_state)
        check(storage+':audit_bytes_checked_before_bootstrap',denied.returncode==1 and denied.stderr=='A04_AUDIT_HASH\n' and not (audit_state/'etat.json').exists() and not (site/'wp-content/mu-plugins/001-imagine-a04-maintenance.php').exists())
        audit_file.write_bytes(audit_bytes)
        state=ROOT/(storage+'-state')
        # Kill the actual updater while a real WP-CLI child is still alive.
        # Its inherited kernel locks must prevent any overlapping resume.
        child_marker=ROOT/(storage+'-wp-child-started')
        delay=site/'wp-content/mu-plugins/998-a04-owned-delay.php'
        delay.write_text("<?php if (defined('WP_CLI') && WP_CLI) { file_put_contents("+json.dumps(str(child_marker))+", (string) getmypid()); sleep(4); }")
        interrupted=subprocess.Popen(['python3','-B','/subject/mettre-a-jour','--wp-path='+str(site),'--plan='+str(plan),'--backup='+str(backup),'--state='+str(state),'--stop-after=woocommerce'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        for _ in range(1000):
            if child_marker.exists() or interrupted.poll() is not None:break
            time.sleep(.02)
        check(storage+':native_child_started',child_marker.is_file())
        delay.unlink();interrupted.kill();interrupted.wait(timeout=10)
        concurrent=update(site,plan,backup,state)
        check(storage+':orphan_child_keeps_site_lock',interrupted.returncode==-9 and concurrent.returncode==1 and concurrent.stderr=='A04_ALREADY_RUNNING\n')
        time.sleep(5)
        stopped=update(site,plan,backup,state,['--stop-after=woocommerce'])
        check(storage+':controlled_interruption',stopped.returncode==75,{'exit':stopped.returncode,'code':stopped.stderr[:200]})
        initial=json.loads((state/'etat.json').read_text())
        check(storage+':durable_checkpoint',initial['steps']['core']['phase']=='verified' and initial['steps']['woocommerce']['phase']=='copied')
        # A real updater is paused after its durable checkpoint, then SIGKILLed.
        # No WP child is alive at this pause, so only the exact owned PID is killed.
        lock=subprocess.Popen(['python3','-B','/subject/mettre-a-jour','--wp-path='+str(site),'--plan='+str(plan),'--backup='+str(backup),'--state='+str(state),'--stop-after=woocommerce','--pause'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        paused=False
        for _ in range(200):
            checkpoint=json.loads((state/'etat.json').read_text())
            if checkpoint['steps']['woocommerce']['attempts']==2 and checkpoint['events'][-1]['stage']=='interruption_requested':paused=True;break
            if lock.poll() is not None:break
            time.sleep(.05)
        check(storage+':real_updater_paused',paused)
        maintenance.write_text('<?php $upgrading = '+str(int(time.time())-1200)+';\n')
        locked_maintenance=maintenance.read_bytes()
        denied=update(site,plan,backup,state)
        check(storage+':concurrent_refused',denied.returncode==1 and denied.stderr=='A04_ALREADY_RUNNING\n' and maintenance.read_bytes()==locked_maintenance)
        alternate=update(site,plan,backup,ROOT/(storage+'-alternate-state'))
        check(storage+':same_site_other_state_refused',alternate.returncode==1 and alternate.stderr=='A04_ALREADY_RUNNING\n' and maintenance.read_bytes()==locked_maintenance)
        lock.kill();lock.wait(timeout=10)
        check(storage+':real_updater_sigkill',lock.returncode==-9)
        # Resume a real interrupted site after the native ten-minute window.
        # A missing or changed persistent MU must never be repaired implicitly.
        persistent=site/'wp-content/mu-plugins/001-imagine-a04-maintenance.php'
        persistent_bytes=persistent.read_bytes()
        maintenance.write_text('<?php $upgrading = '+str(int(time.time())-1200)+';\n')
        refreshed=update(site,plan,backup,state,['--stop-after=woocommerce'])
        check(storage+':expired_resume_accepted_with_exact_mu',refreshed.returncode==75,{'exit':refreshed.returncode,'code':refreshed.stderr[:100],'stale_seconds':1200})
        boot_marker=ROOT/(storage+'-resume-bootstrap.marker')
        boot_probe=site/'wp-content/mu-plugins/996-a04-bootstrap-canary.php'
        boot_probe.write_text('<?php if (defined("WP_CLI") && WP_CLI) { file_put_contents('+json.dumps(str(boot_marker))+', "bootstrap\\n", FILE_APPEND); }')
        maintenance.write_text('<?php $upgrading = '+str(int(time.time())-1200)+';\n')
        expired_bytes=maintenance.read_bytes()
        checkpoint_bytes=(state/'etat.json').read_bytes()
        persistent.unlink()
        denied=update(site,plan,backup,state)
        check(storage+':expired_resume_missing_mu_refused',denied.returncode==1 and denied.stderr=='A04_MAINTENANCE_BYTES\n' and maintenance.read_bytes()==expired_bytes and (state/'etat.json').read_bytes()==checkpoint_bytes and not persistent.exists() and not boot_marker.exists(),{'exit':denied.returncode,'code':denied.stderr[:100]})
        persistent.write_bytes(persistent_bytes+b'\n// altered synthetic MU\n')
        denied=update(site,plan,backup,state)
        check(storage+':expired_resume_changed_mu_refused',denied.returncode==1 and denied.stderr=='A04_MAINTENANCE_BYTES\n' and maintenance.read_bytes()==expired_bytes and (state/'etat.json').read_bytes()==checkpoint_bytes and not boot_marker.exists())
        persistent.write_bytes(persistent_bytes)
        invalid_state=ROOT/(storage+'-invalid-state');invalid_state.mkdir()
        invalid_checkpoint=json.loads(checkpoint_bytes);invalid_checkpoint['config_sha256']='0'*64
        write(invalid_state/'etat.json',invalid_checkpoint)
        denied=update(site,plan,backup,invalid_state)
        check(storage+':expired_resume_invalid_checkpoint_refused',denied.returncode==1 and denied.stderr=='A04_STATE\n' and maintenance.read_bytes()==expired_bytes and not boot_marker.exists())
        refreshed=update(site,plan,backup,state,['--stop-after=woocommerce'])
        import re
        stamp=re.fullmatch(r'<\?php\s+\$upgrading\s*=\s*([0-9]+);\s*',maintenance.read_text())
        check(storage+':expired_resume_refreshes_under_locks',refreshed.returncode==75 and stamp is not None and 0<=time.time()-int(stamp[1])<600 and persistent.read_bytes()==persistent_bytes,{'exit':refreshed.returncode,'code':refreshed.stderr[:100],'stale_seconds':1200})
        check(storage+':expired_resume_preserves_verified_core',json.loads((state/'etat.json').read_text())['steps']['core']==initial['steps']['core'])
        check(storage+':resume_bootstrap_canary_exercised',boot_marker.is_file() and boot_marker.read_text().splitlines()==['bootstrap'])
        boot_probe.unlink()
        forged=a03.wp(site,['eval',"echo 'A04_ID=' . as_schedule_single_action(time(), 'woocommerce_run_update_callback', ['update_callback'=>'wp_delete_user'], 'woocommerce-db-updates');"])
        forged_id=int(forged.stdout.split('A04_ID=')[-1].strip())
        blocked=update(site,plan,backup,state)
        check(storage+':foreign_callback_refused',blocked.returncode==1 and blocked.stderr=='A04_CALLBACK_REFUSED\n')
        intact=a03.wp(site,['eval',"echo 'A04_INTACT=' . (int) (get_user_by('id', "+str(seed['ordinary'])+") !== false && ActionScheduler::store()->get_status("+str(forged_id)+") === 'pending');"])
        check(storage+':foreign_callback_not_executed',intact.stdout.strip().endswith('A04_INTACT=1'))
        a03.wp(site,['eval',"ActionScheduler::store()->delete_action("+str(forged_id)+");"])
        resumed=update(site,plan,backup,state)
        if resumed.returncode:
            for filename in ['etat.json','journal.json','journal.txt','migrations.jsonl']:
                shutil.copyfile(state/filename,OUT/(storage+'-failed-'+filename))
            pending=a03.sql(db,"SELECT hook,status,COUNT(*) AS count FROM wp_actionscheduler_actions WHERE status IN ('pending','in-progress','failed') GROUP BY hook,status ORDER BY hook,status")
            diagnostic=a03.sql(db,"SELECT action_id,JSON_KEYS(args) AS arg_keys,JSON_UNQUOTE(JSON_EXTRACT(args,'$.update_callback')) AS named_callback,JSON_UNQUOTE(JSON_EXTRACT(args,'$[0]')) AS positional_callback FROM wp_actionscheduler_actions WHERE hook='woocommerce_run_update_callback' AND status='pending'")
            batches=a03.sql(db,"SELECT option_name,OCTET_LENGTH(option_value) AS bytes FROM wp_options WHERE option_name LIKE '%\\\\_batch\\\\_%' ORDER BY option_name")
            process=a03.wp(site,['eval',"echo json_encode(get_option('wcs_pending_batch_processes'));"],check=False)
            (OUT/(storage+'-batch-process-classes.json')).write_text(process.stdout)
            (OUT/(storage+'-batch-identifiers.tsv')).write_text(batches.stdout)
            (OUT/(storage+'-callback-identifiers.tsv')).write_text(diagnostic.stdout)
            (OUT/(storage+'-pending-identifiers.tsv')).write_text(pending.stdout)
        check(storage+':resumed',resumed.returncode==0,{'exit':resumed.returncode,'code':resumed.stderr[:200]})
        current=json.loads((state/'etat.json').read_text())
        check(storage+':previous_step_not_replayed',current['steps']['core']==initial['steps']['core'])
        check(storage+':current_step_resumed',current['steps']['woocommerce']['attempts']==6 and all(r['phase']=='verified' for r in current['steps'].values()))
        repeat=update(site,plan,backup,state);again=json.loads((state/'etat.json').read_text())
        check(storage+':idempotent_repeat',repeat.returncode==0 and again['steps']==current['steps'])
        # No theme/data cleanup; maintenance remains and is explicitly removed by fixture only.
        check(storage+':maintenance_kept',maintenance.is_file())
        maintenance.unlink()
        persistent=site/'wp-content/mu-plugins/001-imagine-a04-maintenance.php'
        import urllib.request,urllib.error
        try:urllib.request.urlopen('http://127.0.0.1:18803/',timeout=5);status=200
        except urllib.error.HTTPError as error:status=error.code
        check(storage+':persistent_maintenance_503',persistent.is_file() and status==503)
        persistent.unlink();readonly()
        p=a03.snapshot(site,settings,OUT/(storage+'-after'))
        check(storage+':a03_after',p.returncode==0,{'exit':p.returncode,'code':p.stderr[:150]})
        photo_after=json.loads((OUT/(storage+'-after/non-regression.json')).read_text())
        check(storage+':a03_after_php_log_clean',photo_after['php_log']['checked'] is True and photo_after['php_log']['errors']==0,photo_after['php_log'])
        compared=a03.cmd(['php','/subject/comparer',str(OUT/(storage+'-before/non-regression.json')),str(OUT/(storage+'-after/non-regression.json'))],check=False)
        diff=json.loads(compared.stdout);write(OUT/(storage+'-comparison.json'),diff)
        for name in ['etat.json','journal.json','journal.txt','migrations.jsonl']:
            shutil.copyfile(state/name,OUT/(storage+'-'+name))
        native={'native_a03_exit':compared.returncode,'native_a03_anormal':diff['anormal'],'changes':diff['changes']}
        write(OUT/(storage+'-comparison-receipt.json'),native)
        check(storage+':native_a03_expected_only_code3',compared.returncode==3 and diff['anormal']==0 and bool(diff['changes']) and all(c['class']=='attendu' for c in diff['changes']),native)
        check(storage+':target_versions_exact',photo_after['versions']=={**photo_before['versions'],'wordpress':after[0],'woocommerce':after[1],'subscriptions':after[2],'memberships':after[3]})
        write(OUT/(storage+'-versions.json'),{'before':dict(zip(keys,before)),'after':dict(zip(keys,after)),'baseline_public_woo':old_version})
        # A production-mode rehearsal is still this same entirely fictitious,
        # disconnected fixture. Its local GO is synthetic, never an operator GO.
        production_config=config.replace("define('WP_ENVIRONMENT_TYPE', 'staging')","define('WP_ENVIRONMENT_TYPE', 'production')")
        check(storage+':production_fixture_config_distinct',production_config!=config)
        (site/'wp-config.php').write_text(production_config)
        safety=site/'wp-content/mu-plugins/000-imagine-staging-safety.php';safety_bytes=safety.read_bytes();safety.unlink()
        maintenance.write_text('<?php $upgrading = '+str(int(time.time()))+';\n')
        production_steps=[{**s,'before':s['after']} for s in steps]
        prod_plan=ROOT/(storage+'-production-plan.json');write(prod_plan,{'schema':'imagine-a04-v1','site_status':'frozen-production','steps':production_steps})
        denied=update(site,prod_plan,backup,ROOT/(storage+'-production-no-go'))
        check(storage+':production_requires_go',denied.returncode==1 and denied.stderr=='A04_PRODUCTION_GO_REQUIRED\n')
        go=ROOT/(storage+'-SYNTHETIC-ONLY-go.json');write(go,{'author':'Ced','task':'A-04-mise-a-jour','go':True,'site':str(site),'plan_sha256':sha(prod_plan),'expires_at':int(time.time())+3600})
        prod_state=ROOT/(storage+'-production-state')
        rehearsed=update(site,prod_plan,backup,prod_state,['--go='+str(go)])
        check(storage+':production_mode_synthetic_only',rehearsed.returncode==0,{'exit':rehearsed.returncode,'code':rehearsed.stderr[:100]})
        for name in ['etat.json','journal.json','journal.txt','migrations.jsonl']:
            shutil.copyfile(prod_state/name,OUT/(storage+'-production-'+name))
        (site/'wp-config.php').write_text(config);safety.write_bytes(safety_bytes)
        (site/'wp-content/mu-plugins/001-imagine-a04-maintenance.php').unlink();maintenance.unlink();readonly()
        p=a03.snapshot(site,settings,OUT/(storage+'-production-roundtrip'))
        after_prod=a03.cmd(['php','/subject/comparer',str(OUT/(storage+'-after/non-regression.json')),str(OUT/(storage+'-production-roundtrip/non-regression.json'))],check=False)
        roundtrip=json.loads(after_prod.stdout)
        write(OUT/(storage+'-production-roundtrip-comparison.json'),{'native_a03_exit':after_prod.returncode,**roundtrip})
        check(storage+':production_roundtrip_no_business_change',p.returncode==0 and after_prod.returncode==0 and roundtrip['changes']==[])
        photo_roundtrip=json.loads((OUT/(storage+'-production-roundtrip/non-regression.json')).read_text())
        check(storage+':a03_roundtrip_php_log_clean',photo_roundtrip['php_log']['checked'] is True and photo_roundtrip['php_log']['errors']==0,photo_roundtrip['php_log'])
        check(storage+':remaining_file_only_plugin_updated_last',current['steps']['a04-rest']['phase']=='verified' and 'Version: 2.0.0' in rest.read_text())
        check(storage+':themes_untouched_and_no_cleanup',themes_before==a03.filemap(site/'wp-content/themes') and old_file.read_text()=='Fiction A04 preserve unlisted file')
        trace=[json.loads(line) for line in (state/'migrations.jsonl').read_text().splitlines()]
        names=[row['callback'] for row in trace if row.get('stage')=='complete' and row.get('callback','').startswith('wc_update_')]
        check(storage+':native_callbacks_not_double_executed',bool(names) and len(names)==len(set(names)),names)
    finally:
        server.terminate();server.wait(timeout=15)
def legacy_compatibility():
    import secrets,re
    site=pathlib.Path('/scratch/legacy-691');site.mkdir()
    a03.sql('mysql','CREATE DATABASE a04_legacy')
    with zipfile.ZipFile(ROOT/'wordpress-6.9.1.zip') as z:z.extractall(ROOT/'legacy-core')
    shutil.copytree(ROOT/'legacy-core/wordpress',site,dirs_exist_ok=True)
    for package in [ROOT/'woocommerce-11.0.1.zip',pathlib.Path('/opt/a03/woocommerce-subscriptions.zip')]:
        with zipfile.ZipFile(package) as z:z.extractall(site/'wp-content/plugins')
    config="<?php define('DB_NAME','a04_legacy'); define('DB_USER','root'); define('DB_PASSWORD',''); define('DB_HOST','localhost:/scratch/mariadb.sock'); define('DB_CHARSET','utf8mb4'); define('DB_COLLATE',''); define('WP_ENVIRONMENT_TYPE','staging'); define('DISABLE_WP_CRON',true); define('WP_HTTP_BLOCK_EXTERNAL',true); $table_prefix='wp_'; define('ABSPATH',__DIR__.'/'); require_once ABSPATH.'wp-settings.php';"
    (site/'wp-config.php').write_text(config)
    a03.wp(site,['core','install','--url=https://a04-legacy.synthetic.test','--title=Fiction A04 legacy','--admin_user=a04-fiction','--admin_email=a04-fiction@example.org','--skip-email','--prompt=admin_password'],data=secrets.token_urlsafe(40)+'\n')
    woo=a03.wp(site,['plugin','activate','woocommerce'],check=False)
    sub=a03.wp(site,['plugin','activate','woocommerce-subscriptions'],check=False)
    header=(site/'wp-content/plugins/woocommerce-subscriptions/woocommerce-subscriptions.php').read_text()
    minimum=next(line.split('Requires at least:',1)[1].strip() for line in header.splitlines() if 'Requires at least:' in line)
    installed=a03.wp(site,['core','version']).stdout.strip()
    check('legacy691:native_guard_no_override',installed=='6.9.1' and minimum=='7.0' and sub.returncode!=0,{'wordpress':installed,'subscriptions_requires_wp':minimum,'woo_activation_exit':woo.returncode,'subscriptions_activation_exit':sub.returncode,'stderr_sha256':hashlib.sha256(sub.stderr.encode()).hexdigest()})

def main():
    pathlib.Path('/scratch').mkdir()
    a03.cmd(['mariadb-install-db','--datadir=/scratch/mysql','--auth-root-authentication-method=normal','--skip-test-db','--user=root'])
    db=subprocess.Popen(['mariadbd','--user=root','--datadir=/scratch/mysql','--socket=/scratch/mariadb.sock','--skip-networking','--skip-log-bin','--pid-file=/scratch/mysql.pid','--log-error=/scratch/mysql.log'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:
        for _ in range(100):
            if a03.cmd(['mariadb-admin','--socket=/scratch/mariadb.sock','-uroot','ping'],check=False).returncode==0:break
            time.sleep(.2)
        legacy_compatibility()
        for storage in ['classic','hpos']:
            try:run_storage(storage)
            except Exception as e:
                CHECKS.append({'check':storage+':exception','ok':False,'class':type(e).__name__,'code':str(e)[:500]});print(json.dumps(CHECKS[-1]),flush=True)
        check('network_none',[p.name for p in pathlib.Path('/sys/class/net').iterdir()]==['lo'])
        for p in ['/proc/net/tcp','/proc/net/tcp6']:
            check('no_listener:'+p,not any(l.split()[3]=='0A' for l in pathlib.Path(p).read_text().splitlines()[1:]))
    finally:
        db.terminate();db.wait(timeout=30)
        result={'suite':'A04-real-synthetic-classic-hpos','checks':CHECKS,'exit_code':int(any(not c['ok'] for c in CHECKS))};write(OUT/'result.json',result)
    return result['exit_code']
if __name__=='__main__':sys.exit(main())
