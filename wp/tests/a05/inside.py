"""Real native classic/HPOS acceptance. Disposable synthetic data only."""
import importlib.util
import json
import pathlib
import shutil
import subprocess
import sys
import tarfile
import time
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('a03','/opt/a03/inside.py');a03=importlib.util.module_from_spec(spec);spec.loader.exec_module(a03)
ROOT=pathlib.Path('/opt/a05');OUT=pathlib.Path('/report');CHECKS=[]
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def check(name,ok,detail=None):
    CHECKS.append({'check':name,'ok':bool(ok),'detail':detail});print(json.dumps(CHECKS[-1]),flush=True)
    if not ok:raise AssertionError(name)
def clean(site,plan,backup,state,extra=None):
    return a03.cmd(['python3','-B','/subject/nettoyer','--wp-path='+str(site),'--plan='+str(plan),'--backup='+str(backup),'--state='+str(state)]+(extra or []),check=False,timeout=300)
def option_hashes(db):
    rows=a03.sql(db,"SELECT option_name, SHA2(option_value,256) AS digest FROM wp_options ORDER BY option_name").stdout.splitlines()[1:]
    return dict(line.split('\t',1) for line in rows)

def run_storage(storage):
    site,db,seed,config,settings=a03.install(storage)
    a03.wp(site,['eval',"require_once WC_ABSPATH . 'includes/admin/wc-admin-functions.php'; wc_memberships()->get_lifecycle_handler()->init(); WC_Subscriptions_Upgrader::upgrade();"])
    # Active removable plugin has a real uninstall routine; ordinary removal MUST NOT run it.
    fixtures={'a05-remove': 'Fiction active removable','a05-orphan':'Fiction inactive orphan','a05-keep':'Fiction retained','a05-base':'Fiction dependency','a05-dependent':'Fiction dependent','a05-gateway':'Fiction gateway'}
    for slug,title in fixtures.items():
        p=site/('wp-content/plugins/'+slug);p.mkdir()
        header='<?php\n/*\nPlugin Name: '+title+'\nVersion: 1.0.0\n'+('Requires Plugins: a05-base\n' if slug=='a05-dependent' else '')+'*/\n'
        (p/'entry.php').write_text(header)
        if slug=='a05-remove':(p/'uninstall.php').write_text("<?php if (!defined('WP_UNINSTALL_PLUGIN')) exit; delete_option('a05_uninstall_canary');")
    for slug in ['a05-remove','a05-keep','a05-base','a05-dependent','a05-gateway']:a03.wp(site,['plugin','activate',slug+'/entry.php'])
    a03.sql(db,"CREATE TABLE wp_a05_orphan (id INT PRIMARY KEY) ENGINE=InnoDB; INSERT INTO wp_a05_orphan VALUES (1),(2); CREATE TABLE wp_a05_stats_2015 (id INT) ENGINE=InnoDB; INSERT INTO wp_a05_stats_2015 VALUES (7); CREATE TABLE wp_a05_stats_2026 LIKE wp_a05_stats_2015; INSERT INTO wp_a05_stats_2026 VALUES (9); CREATE TABLE wp_a05_kept (id INT) ENGINE=InnoDB; INSERT INTO wp_a05_kept VALUES (8);")
    a03.wp(site,['eval',"add_option('a05_orphan_setting', 'Fiction option'); add_option('a05_uninstall_canary','must-survive-default-removal'); wp_schedule_single_event(time()+3600,'a05_orphan_hook',['fiction']);"])
    uploads=site/'wp-content/uploads/a05-debris';uploads.mkdir(parents=True);(uploads/'fiction.txt').write_text('fiction debris')
    kept_upload=site/'wp-content/uploads/a05-kept';kept_upload.mkdir();(kept_upload/'keep.txt').write_text('fiction preserved')
    (site/'.imagine-a04-bascule.lock').touch()
    sys.path.insert(0,'/subject/a05');import clean as subject
    inv=subject.inspect_site(site)
    owners={name:[] for name in inv['plugins']};owners.update({'theme:'+inv['theme']:[]});owners.update({'mu:'+n:[] for n in inv['mu_plugins']});owners['a05-keep/entry.php']=['wp_a05_kept']
    plan_doc={'schema':'imagine-a05-v1','site_status':'verified-staging','plugins':[{'plugin':'a05-remove/entry.php','action':'retirer','uninstall':False}],'tables':[{'match':'exact','name':'wp_a05_orphan','action':'supprimer'},{'match':'prefix','name':'wp_a05_stats_','action':'supprimer'}],'options':[{'match':'prefix','name':'a05_orphan_','action':'supprimer'}],'cron':[{'match':'exact','name':'a05_orphan_hook','action':'supprimer'}],'uploads':[{'path':'a05-debris','action':'supprimer'}],'table_owners':owners}
    plan=ROOT/(storage+'-plan.json');write(plan,plan_doc);shutil.copyfile(plan,OUT/(storage+'-plan.json'))
    backup_dir=ROOT/('backup-'+storage);backup_dir.mkdir();sql=backup_dir/'database.sql';sql.write_text(a03.cmd(['mariadb-dump','--socket=/scratch/mariadb.sock','-uroot','--single-transaction',db]).stdout)
    files=backup_dir/'files.tar'
    with tarfile.open(files,'w') as archive:archive.add(site,arcname='site')
    backup=ROOT/(storage+'-backup.json');backup_doc={'site':str(site),'created_at':int(time.time()),'database':{'path':str(sql),'sha256':a03.hashlib.sha256(sql.read_bytes()).hexdigest()},'files':{'path':str(files),'sha256':a03.hashlib.sha256(files.read_bytes()).hexdigest()}};write(backup,backup_doc)
    state=ROOT/(storage+'-state')
    denied=clean(site,plan,backup,state,['--dry-run']);check(storage+':maintenance_required',denied.returncode==1 and denied.stderr=='A04_MAINTENANCE\n',{'exit':denied.returncode,'code':denied.stderr[:120]})
    (site/'.maintenance').write_text('<?php $upgrading = '+str(int(time.time()))+';\n')
    before_db=a03.fingerprint(db,True);before_files=a03.filemap(site)
    stale=ROOT/(storage+'-stale-backup.json');write(stale,{**backup_doc,'created_at':int(time.time())-21601});r=clean(site,plan,stale,state,['--dry-run'])
    check(storage+':inherited_recent_backup_guard',r.returncode==1 and r.stderr=='A04_BACKUP_AGE\n' and before_db==a03.fingerprint(db,True) and before_files==a03.filemap(site))
    in_site=ROOT/(storage+'-inside-backup.json');write(in_site,{**backup_doc,'database':{'path':str(site/'wp-content/../wp-config.php'),'sha256':subject.a04.digest(site/'wp-config.php')}});r=clean(site,plan,in_site,state,['--dry-run'])
    check(storage+':inherited_canonical_backup_guard',r.returncode==1 and r.stderr=='A04_BACKUP_LOCATION\n')
    marker=site/'.imagine-staging-verified.json';marker_bytes=marker.read_bytes();marker.unlink();r=clean(site,plan,backup,state,['--dry-run']);marker.write_bytes(marker_bytes)
    check(storage+':inherited_verified_status_guard',r.returncode==1 and r.stderr=='A04_JSON\n')
    dry=clean(site,plan,backup,state,['--dry-run']);(OUT/(storage+'-dry-run.json')).write_text(dry.stdout)
    check(storage+':dry_run',dry.returncode==0,{'exit':dry.returncode,'code':dry.stderr[:200]})
    check(storage+':dry_database_files_exact',before_db==a03.fingerprint(db,True) and before_files==a03.filemap(site))
    report=json.loads(dry.stdout);check(storage+':dry_sizes',any(o['kind']=='table' and o['name']=='wp_a05_orphan' and o['rows']==2 and o['bytes']>0 for o in report['operations']) and any(o['kind']=='upload' and o['files']==1 and o['bytes']==14 for o in report['operations']))
    write(OUT/(storage+'-dry-fingerprints.json'),{'before_database':before_db,'after_database':a03.fingerprint(db,True),'before_files':before_files,'after_files':a03.filemap(site)})
    # Native A03 photographs with the fixture's SELECT-only account and rollback HTTP.
    (site/'.maintenance').unlink()
    readonly=config.replace("define('DB_USER', 'root')","define('DB_USER', 'a03_"+storage+"')")
    (site/'wp-config.php').write_text(readonly)
    log_path=json.loads(settings.read_text())['php_error_log']
    server=subprocess.Popen(['php','-d','log_errors=1','-d','display_errors=0','-d','date.timezone=UTC','-d','error_log='+log_path,'-S','127.0.0.1:18803','-t',str(site)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(.5)
    try:
        photo=a03.snapshot(site,settings,OUT/(storage+'-before'));check(storage+':a03_before',photo.returncode==0,photo.stderr[:120])
        (site/'wp-config.php').write_text(config);(site/'.maintenance').write_text('<?php $upgrading = '+str(int(time.time()))+';\n')
        # Whole-plan preflight must reject BEFORE any real deletion.
        cases=[('dependency',{'plugins':[{'plugin':'a05-base/entry.php','action':'retirer','uninstall':False}]},'A05_DEPENDENCY:a05-base/entry.php'),('commerce',{'plugins':[{'plugin':'woocommerce/woocommerce.php','action':'retirer','uninstall':False}]},'A05_PROTECTED_PLUGIN:woocommerce/woocommerce.php'),('subscriptions',{'plugins':[{'plugin':'woocommerce-subscriptions/woocommerce-subscriptions.php','action':'desactiver','uninstall':False}]},'A05_PROTECTED_PLUGIN:woocommerce-subscriptions/woocommerce-subscriptions.php'),('memberships',{'plugins':[{'plugin':'woocommerce-memberships/woocommerce-memberships.php','action':'retirer','uninstall':False}]},'A05_PROTECTED_PLUGIN:woocommerce-memberships/woocommerce-memberships.php'),('gateway',{'plugins':[{'plugin':'a05-gateway/entry.php','action':'retirer','uninstall':False}]},'A05_PROTECTED_PLUGIN:a05-gateway/entry.php'),('core-table',{'tables':[{'match':'exact','name':'wp_posts','action':'supprimer'}]},'A05_PROTECTED_TABLE:wp_posts'),('commerce-table',{'tables':[{'match':'prefix','name':'wp_wc_','action':'supprimer'}]},'A05_PROTECTED_TABLE:'),('kept-table',{'tables':[{'match':'exact','name':'wp_a05_kept','action':'supprimer'}]},'A05_KEPT_PLUGIN_TABLE:wp_a05_kept'),('outside-upload',{'uploads':[{'path':'../outside','action':'supprimer'}]},'A05_NAME:../outside'),('active-theme',{'plugins':[{'plugin':'../themes/a03-fiction/index.php','action':'retirer','uninstall':False}]},'A05_NAME:../themes/a03-fiction/index.php')]
        for label,delta,code in cases:
            bad=ROOT/(storage+'-'+label+'.json');write(bad,{**plan_doc,**delta});baseline_db=a03.fingerprint(db);baseline_files=a03.filemap(site)
            refused=clean(site,bad,backup,ROOT/(storage+'-refused-'+label));check(storage+':refusal_'+label,refused.returncode==1 and code in refused.stderr and baseline_db==a03.fingerprint(db) and baseline_files==a03.filemap(site),{'exit':refused.returncode,'code':refused.stderr[:180]})
        outside=ROOT/(storage+'-outside');outside.mkdir();(outside/'canary.txt').write_text('outside intact');link=site/'wp-content/uploads/a05-link';link.symlink_to(outside,target_is_directory=True)
        bad=ROOT/(storage+'-symlink.json');write(bad,{**plan_doc,'uploads':[{'path':'a05-link','action':'supprimer'}]});refused=clean(site,bad,backup,ROOT/(storage+'-refused-symlink'))
        check(storage+':resolved_upload_escape_refused',refused.returncode==1 and 'SYMLINK' in refused.stderr and (outside/'canary.txt').read_text()=='outside intact');link.unlink()
        frozen_before=subject.inspect_site(site);file_before=a03.filemap(site);db_before=a03.fingerprint(db,True);options_before=option_hashes(db)
        stopped=clean(site,plan,backup,state,['--stop-after=1']);check(storage+':actual_interruption',stopped.returncode==75,{'exit':stopped.returncode,'code':stopped.stderr[:160]})
        checkpoint=json.loads((state/'etat.json').read_text());check(storage+':checkpoint_fsynced',checkpoint['operations'][0]['phase']=='done' and checkpoint['complete'] is False)
        resumed=clean(site,plan,backup,state);check(storage+':actual_resume',resumed.returncode==0,{'exit':resumed.returncode,'code':resumed.stderr[:200]})
        after=subject.inspect_site(site);file_after=a03.filemap(site);db_after=a03.fingerprint(db,True)
        check(storage+':only_named_removed', 'a05-remove/entry.php' not in after['plugins'] and all(n in after['plugins'] for n in frozen_before['plugins'] if n!='a05-remove/entry.php') and not any(r['name'] in ['wp_a05_orphan','wp_a05_stats_2015','wp_a05_stats_2026'] for r in after['tables']) and not any(r['name'].startswith('a05_orphan_') for r in after['options']) and not any(r['name']=='a05_orphan_hook' for r in after['cron']) and not uploads.exists() and kept_upload.exists())
        check(storage+':default_uninstall_not_run',any(r['name']=='a05_uninstall_canary' for r in after['options']))
        options_after=option_hashes(db);option_changes=[n for n in set(options_before)|set(options_after) if options_before.get(n)!=options_after.get(n)]
        check(storage+':unlisted_option_values_intact',set(option_changes)=={'active_plugins','cron','a05_orphan_setting'},sorted(option_changes))
        write(OUT/(storage+'-options-fingerprints.json'),{'before':options_before,'after':options_after,'changed':sorted(option_changes)})
        changed_tables=[n for n in db_before['tables'] if n in db_after['tables'] and db_before['tables'][n]!=db_after['tables'][n]]
        check(storage+':unlisted_tables_intact',changed_tables==['wp_options'],changed_tables)
        changes=[n for n in set(file_before)|set(file_after) if file_before.get(n)!=file_after.get(n)]
        check(storage+':unlisted_files_intact',all(n.startswith(('wp-content/plugins/a05-remove/','wp-content/uploads/a05-debris/')) or n in ['wp-content/mu-plugins/001-imagine-a04-maintenance.php','.maintenance'] for n in changes),changes)
        repeat_db=a03.fingerprint(db,True);repeat_files=a03.filemap(site);repeat=clean(site,plan,backup,state)
        check(storage+':repeat_zero_effect',repeat.returncode==0 and repeat_db==a03.fingerprint(db,True) and repeat_files==a03.filemap(site))
        fresh=clean(site,plan,backup,ROOT/(storage+'-fresh-state'));check(storage+':fresh_second_pass_zero_effect',fresh.returncode==0 and repeat_db==a03.fingerprint(db,True) and repeat_files==a03.filemap(site),{'exit':fresh.returncode,'code':fresh.stderr[:160]})
        for f in ['etat.json','journal.json','journal.txt']:shutil.copyfile(state/f,OUT/(storage+'-'+f))
        write(OUT/(storage+'-inventory.json'),{'before':frozen_before,'after':after,'files_changed':changes,'surviving_tables_changed':changed_tables})
        (site/'.maintenance').unlink();(site/'wp-content/mu-plugins/001-imagine-a04-maintenance.php').unlink();(site/'wp-config.php').write_text(readonly)
        photo=a03.snapshot(site,settings,OUT/(storage+'-after'));check(storage+':a03_after',photo.returncode==0,photo.stderr[:120])
        compared=a03.cmd(['php','/subject/comparer',str(OUT/(storage+'-before/non-regression.json')),str(OUT/(storage+'-after/non-regression.json'))],check=False)
        comparison=json.loads(compared.stdout);write(OUT/(storage+'-comparison.json'),{'native_exit':compared.returncode,**comparison})
        check(storage+':native_a03_result_unmodified',compared.returncode==0 and comparison['anormal']==0 and comparison['changes']==[],{'native_exit':compared.returncode,**comparison})
        for label in ['before','after']:
            photo=json.loads((OUT/(storage+'-'+label+'/non-regression.json')).read_text());check(storage+':php_log_clean_'+label,photo['php_log']['checked'] and photo['php_log']['errors']==0)
        # Separate native API checks, after sealing the main before/after proof.
        (site/'wp-config.php').write_text(config);(site/'.maintenance').write_text('<?php $upgrading = '+str(int(time.time()))+';\n')
        extra_doc={**plan_doc,'plugins':[{'plugin':'a05-keep/entry.php','action':'desactiver','uninstall':False}],'tables':[],'options':[],'cron':[],'uploads':[]}
        extra=ROOT/(storage+'-deactivate.json');write(extra,extra_doc);r=clean(site,extra,backup,ROOT/(storage+'-deactivate-state'))
        check(storage+':native_deactivate_files_kept',r.returncode==0 and (site/'wp-content/plugins/a05-keep/entry.php').is_file() and 'a05-keep/entry.php' not in subject.inspect_site(site)['active'],{'exit':r.returncode,'code':r.stderr[:150]})
        uninstall=site/'wp-content/plugins/a05-explicit';uninstall.mkdir();(uninstall/'entry.php').write_text('<?php\n/*\nPlugin Name: Fiction explicit uninstall\nVersion: 1.0.0\n*/\n');(uninstall/'uninstall.php').write_text("<?php if (!defined('WP_UNINSTALL_PLUGIN')) exit; delete_option('a05_uninstall_canary');")
        explicit_doc={**extra_doc,'plugins':[{'plugin':'a05-explicit/entry.php','action':'retirer','uninstall':True}]};explicit=ROOT/(storage+'-explicit.json');write(explicit,explicit_doc)
        dry_explicit=clean(site,explicit,backup,ROOT/(storage+'-explicit-state'),['--dry-run']);check(storage+':explicit_uninstall_dry_does_not_run',dry_explicit.returncode==0 and any(r['name']=='a05_uninstall_canary' for r in subject.inspect_site(site)['options']))
        r=clean(site,explicit,backup,ROOT/(storage+'-explicit-state'))
        check(storage+':native_explicit_uninstall',r.returncode==0 and not uninstall.exists() and not any(r['name']=='a05_uninstall_canary' for r in subject.inspect_site(site)['options']),{'exit':r.returncode,'code':r.stderr[:150]})
        ambiguous=ROOT/(storage+'-ambiguous-state');ambiguous.mkdir();persistent=site/'wp-content/mu-plugins/001-imagine-a04-maintenance.php'
        checkpoint={'schema':'imagine-a05-state-v1','site':str(site),'plan_sha256':subject.a04.digest(explicit),'config_sha256':subject.a04.digest(site/'wp-config.php'),'operations':[{'kind':'uninstall','name':'a05-explicit/entry.php','phase':'started'}],'events':[],'complete':False};write(ambiguous/'etat.json',checkpoint)
        # This checkpoint double is additional fail-closed coverage, not the real interruption proof.
        r=clean(site,explicit,backup,ambiguous);check(storage+':ambiguous_uninstall_checkpoint_refused',r.returncode==1 and r.stderr=='A05_UNINSTALL_AMBIGUOUS:a05-explicit/entry.php\n',{'exit':r.returncode,'code':r.stderr[:150],'proof_kind':'checkpoint-double'})
    finally:server.terminate();server.wait(timeout=15)
def main():
    pathlib.Path('/scratch').mkdir();a03.cmd(['mariadb-install-db','--datadir=/scratch/mysql','--auth-root-authentication-method=normal','--skip-test-db','--user=root'])
    db=subprocess.Popen(['mariadbd','--user=root','--datadir=/scratch/mysql','--socket=/scratch/mariadb.sock','--skip-networking','--skip-log-bin','--pid-file=/scratch/mysql.pid','--log-error=/scratch/mysql.log'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:
        for _ in range(100):
            if a03.cmd(['mariadb-admin','--socket=/scratch/mariadb.sock','-uroot','ping'],check=False).returncode==0:break
            time.sleep(.2)
        for storage in ['classic','hpos']:
            try:run_storage(storage)
            except Exception as e:CHECKS.append({'check':storage+':exception','ok':False,'class':type(e).__name__,'code':str(e)[:500]});print(json.dumps(CHECKS[-1]),flush=True)
        check('network_none',[p.name for p in pathlib.Path('/sys/class/net').iterdir()]==['lo'])
        for p in ['/proc/net/tcp','/proc/net/tcp6']:check('no_listener:'+p,not any(l.split()[3]=='0A' for l in pathlib.Path(p).read_text().splitlines()[1:]))
    finally:
        db.terminate();db.wait(timeout=30);result={'suite':'A05-real-synthetic-classic-hpos','checks':CHECKS,'exit_code':int(any(not c['ok'] for c in CHECKS))};write(OUT/'result.json',result)
    return result['exit_code']
if __name__=='__main__':sys.exit(main())
