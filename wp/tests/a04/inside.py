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
    check(storage+':baseline_versions',bool(seed['versions']),seed['versions'])
    server=subprocess.Popen(['php','-d','log_errors=0','-d','display_errors=0','-S','127.0.0.1:18803','-t',str(site)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    time.sleep(.5)
    def readonly():
        (site/'wp-config.php').write_text(config.replace("define('DB_USER', 'root')","define('DB_USER', 'a03_"+storage+"')"))
    try:
        readonly();p=a03.snapshot(site,settings,OUT/(storage+'-before'))
        check(storage+':a03_before',p.returncode==0,{'exit':p.returncode,'code':p.stderr[:150]})
        (site/'wp-config.php').write_text(config)
        # Explicit disposable file + DB backups, never any external archive or input.
        backup_dir=ROOT/('backup-'+storage);backup_dir.mkdir()
        sql=backup_dir/'database.sql'
        exported=a03.cmd(['mariadb-dump','--socket=/scratch/mariadb.sock','-uroot','--single-transaction',db]);sql.write_text(exported.stdout)
        files=backup_dir/'content.tar'
        with tarfile.open(files,'w') as tar:tar.add(site/'wp-content',arcname='wp-content')
        backup=ROOT/(storage+'-backup.json')
        backup_doc={'site':str(site),'created_at':int(time.time()),'database':{'path':str(sql),'sha256':sha(sql)},'files':{'path':str(files),'sha256':sha(files)}};write(backup,backup_doc)
        versions=seed['versions'];target_core=package_version('/opt/compatible-public/wordpress.zip','wordpress/wp-includes/version.php',True)
        target_wc=package_version('/opt/compatible-public/woocommerce.zip','woocommerce/woocommerce.php')
        keys=['core','woocommerce','woocommerce-subscriptions','woocommerce-memberships'];before=[versions['wordpress'],versions['woocommerce'],versions['subscriptions'],versions['memberships']]
        after=[target_core,target_wc,versions['subscriptions'],versions['memberships']]
        archives=['/opt/compatible-public/wordpress.zip','/opt/compatible-public/woocommerce.zip','/opt/a03/woocommerce-subscriptions.zip','/opt/a03/woocommerce-memberships.zip']
        steps=[{'component':k,'before':v,'after':t,'archive':p,'sha256':sha(p),'adapter':k,'hooks':[]} for k,v,t,p in zip(keys,before,after,archives)]
        plan=ROOT/(storage+'-plan.json');write(plan,{'schema':'imagine-a04-v1','site_status':'verified-staging','steps':steps})
        # Prove guards before the first update, with actual filesystem readbacks.
        denied=update(site,plan,backup,ROOT/(storage+'-no-maintenance'))
        check(storage+':maintenance_required',denied.returncode==1 and denied.stderr=='A04_MAINTENANCE\n')
        maintenance=site/'.maintenance';maintenance.write_text('<?php $upgrading = '+str(int(time.time()))+';\n')
        bad=ROOT/(storage+'-stale.json');bad_doc={**backup_doc,'created_at':int(time.time())-21601};write(bad,bad_doc)
        denied=update(site,plan,bad,ROOT/(storage+'-stale'))
        check(storage+':stale_backup_refused',denied.returncode==1 and denied.stderr=='A04_BACKUP_AGE\n')
        state=ROOT/(storage+'-state')
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
        denied=update(site,plan,backup,state)
        check(storage+':concurrent_refused',denied.returncode==1 and denied.stderr=='A04_ALREADY_RUNNING\n')
        lock.kill();lock.wait(timeout=10)
        check(storage+':real_updater_sigkill',lock.returncode==-9)
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
        check(storage+':current_step_resumed',current['steps']['woocommerce']['attempts']==3 and all(r['phase']=='verified' for r in current['steps'].values()))
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
        compared=a03.cmd(['php','/subject/comparer',str(OUT/(storage+'-before/non-regression.json')),str(OUT/(storage+'-after/non-regression.json'))],check=False)
        diff=json.loads(compared.stdout);write(OUT/(storage+'-comparison.json'),diff)
        for name in ['etat.json','journal.json','journal.txt','migrations.jsonl']:
            shutil.copyfile(state/name,OUT/(storage+'-'+name))
        sys.path.insert(0,'/subject/a04')
        from qualification import qualify
        qualified=qualify(json.loads((OUT/(storage+'-before/non-regression.json')).read_text()),json.loads((OUT/(storage+'-after/non-regression.json')).read_text()),{'wordpress':after[0],'woocommerce':after[1],'subscriptions':after[2],'memberships':after[3]})
        qualified['native_a03_exit']=compared.returncode
        qualified['native_a03_anormal']=diff['anormal']
        write(OUT/(storage+'-qualification.json'),qualified)
        check(storage+':only_exact_expected_changes_additive',compared.returncode in [0,2,3] and qualified['qualified'],qualified)
        write(OUT/(storage+'-versions.json'),{'before':dict(zip(keys,before)),'after':dict(zip(keys,after)),'baseline_public_woo':old_version})
    finally:
        server.terminate();server.wait(timeout=15)
def main():
    pathlib.Path('/scratch').mkdir()
    a03.cmd(['mariadb-install-db','--datadir=/scratch/mysql','--auth-root-authentication-method=normal','--skip-test-db','--user=root'])
    db=subprocess.Popen(['mariadbd','--user=root','--datadir=/scratch/mysql','--socket=/scratch/mariadb.sock','--skip-networking','--skip-log-bin','--pid-file=/scratch/mysql.pid','--log-error=/scratch/mysql.log'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:
        for _ in range(100):
            if a03.cmd(['mariadb-admin','--socket=/scratch/mariadb.sock','-uroot','ping'],check=False).returncode==0:break
            time.sleep(.2)
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
