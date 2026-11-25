"""Real A08 chain on the existing synthetic A04/A05 bench, no tool doubles."""
import hashlib
import importlib.util
import json
import pathlib
import shutil
import subprocess
import sys
import tarfile
import time
import zipfile
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('a03','/opt/a03/inside.py')
a03=importlib.util.module_from_spec(spec);spec.loader.exec_module(a03)
spec=importlib.util.spec_from_file_location('fixture_a04','/opt/a04/inside.py')
a04=importlib.util.module_from_spec(spec);spec.loader.exec_module(a04)
ROOT=pathlib.Path('/opt/a08');OUT=pathlib.Path('/report');CHECKS=[]


def write(path,value):
    path.write_text(json.dumps(value,indent=2)+'\n')


def check(name,ok,detail=None):
    CHECKS.append({'check':name,'ok':bool(ok),'detail':detail})
    print(json.dumps(CHECKS[-1]),flush=True)
    if not ok:raise AssertionError(name)


def sha(path):
    with open(path,'rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def run_storage(storage):
    baseline=ROOT/'baseline'
    if not baseline.exists():
        baseline.mkdir()
        for file in ['wordpress-7.0.zip','woocommerce-11.0.1.zip']:
            with zipfile.ZipFile('/opt/a04/'+file) as archive:archive.extractall(baseline)
    original=shutil.copytree
    def copy(source,target,*args,**kw):
        selected=baseline/'wordpress' if str(source)=='/opt/wordpress/wordpress' else baseline/'woocommerce' if str(source)=='/opt/woocommerce/woocommerce' else source
        return original(selected,target,*args,**kw)
    shutil.copytree=copy
    try:site,db,seed,config,settings=a03.install(storage)
    finally:shutil.copytree=original
    a03.wp(site,['eval',"require_once WC_ABSPATH . 'includes/admin/wc-admin-functions.php'; wc_memberships()->get_lifecycle_handler()->init(); WC_Subscriptions_Upgrader::upgrade();"])
    orphan=site/'wp-content/plugins/a08-orphan';orphan.mkdir()
    (orphan/'entry.php').write_text('<?php\n/*\nPlugin Name: Fiction A08 orphan\nVersion: 1.0.0\n*/\n')
    a03.wp(site,['plugin','activate','a08-orphan/entry.php'])
    debris=site/'wp-content/uploads/a08-debris';debris.mkdir(parents=True);(debris/'fiction.txt').write_text('A08 fictional obsolete file')
    a03.sql(db,'CREATE TABLE wp_a08_orphan (id INT PRIMARY KEY) ENGINE=InnoDB; INSERT INTO wp_a08_orphan VALUES (1)')
    a03.wp(site,['eval',"add_option('a08_orphan_setting','Fiction'); $cron=_get_cron_array(); $cron[time()+3600]['a08_orphan_hook'][md5(serialize(['fiction']))]=['schedule'=>false,'args'=>['fiction']]; _set_cron_array($cron);"])
    (site/'.imagine-a04-bascule.lock').touch()
    sys.path.insert(0,'/subject/a05');import clean as cleaner
    inventory=cleaner.inspect_site(site)
    owners={name:[] for name in inventory['plugins']}
    owners.update({'theme:'+inventory['theme']:[]})
    owners.update({'mu:'+name:[] for name in inventory['mu_plugins']})
    cleanup={'schema':'imagine-a05-v1','site_status':'verified-staging',
        'plugins':[{'plugin':'a08-orphan/entry.php','action':'retirer','uninstall':False}],
        'tables':[{'match':'exact','name':'wp_a08_orphan','action':'supprimer'}],
        'options':[{'match':'exact','name':'a08_orphan_setting','action':'supprimer'}],
        'cron':[{'match':'exact','name':'a08_orphan_hook','action':'supprimer'}],
        'uploads':[{'path':'a08-debris','action':'supprimer'}],'table_owners':owners}
    plan_clean=ROOT/(storage+'-cleanup.json');write(plan_clean,cleanup)
    keys=['core','woocommerce','woocommerce-subscriptions','woocommerce-memberships']
    versions=seed['versions']
    before=[versions['wordpress'],versions['woocommerce'],versions['subscriptions'],versions['memberships']]
    archives=['/opt/compatible-public/wordpress.zip','/opt/compatible-public/woocommerce.zip','/opt/a03/woocommerce-subscriptions.zip','/opt/a03/woocommerce-memberships.zip']
    after=[a04.package_version(archives[0],'wordpress/wp-includes/version.php',True),a04.package_version(archives[1],'woocommerce/woocommerce.php'),before[2],before[3]]
    steps=[{'component':key,'main_file':None if key=='core' else key+'.php','before':old,'after':new,'archive':archive,'sha256':sha(archive),'adapter':key,'hooks':[]} for key,old,new,archive in zip(keys,before,after,archives)]
    plan_update=ROOT/(storage+'-update.json');write(plan_update,{'schema':'imagine-a04-v1','site_status':'verified-staging','steps':steps})
    backup_dir=ROOT/(storage+'-backups');backup_dir.mkdir()
    sql=backup_dir/'db.sql';sql.write_text(a03.cmd(['mariadb-dump','--socket=/scratch/mariadb.sock','-uroot','--single-transaction',db]).stdout)
    files=backup_dir/'files.tar'
    with tarfile.open(files,'w') as tar:tar.add(site,arcname='site')
    backup=ROOT/(storage+'-backup.json')
    write(backup,{'site':str(site),'created_at':int(time.time()),'database':{'path':str(sql),'sha256':sha(sql)},'files':{'path':str(files),'sha256':sha(files)}})
    shutil.copyfile(plan_clean,OUT/(storage+'-cleanup-plan.json'));shutil.copyfile(plan_update,OUT/(storage+'-update-plan.json'))
    state=OUT/(storage+'-sequence')
    args=['python3','-B','/subject/repeter','--wp-path='+str(site),'--state='+str(state),'--update-plan='+str(plan_update),'--clean-plan='+str(plan_clean),'--config='+str(settings),'--backup='+str(backup)]
    readonly=config.replace("define('DB_USER', 'root')","define('DB_USER', 'a03_"+storage+"')")
    saved_maintenance=[None]
    def read_mode():
        # Operator fixture boundary, never A08: retain external network isolation and safety MU.
        persistent=site/'wp-content/mu-plugins/001-imagine-a04-maintenance.php'
        if persistent.exists():saved_maintenance[0]=persistent.read_bytes()
        for path in [site/'.maintenance',persistent]:
            if path.exists():path.unlink()
        (site/'wp-config.php').write_text(readonly)
    def write_mode():
        (site/'wp-config.php').write_text(config)
        (site/'.maintenance').write_text('<?php $upgrading = '+str(int(time.time()))+';\n')
        if saved_maintenance[0] is not None:
            (site/'wp-content/mu-plugins/001-imagine-a04-maintenance.php').write_bytes(saved_maintenance[0])
    def invoke(label,extra=None):
        # Same explicit fixture-only AUTO_INCREMENT repair as accepted A03.snapshot.
        sequence_query="SELECT AUTO_INCREMENT FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='wp_options'"
        reading=label in ['before','after','second-before','second-after']
        sequence=int(a03.sql(db,sequence_query).stdout.splitlines()[-1]) if reading else None
        started=time.monotonic()
        result=a03.cmd(args+(extra or []),check=False,timeout=700)
        if reading:
            a03.sql(db,'ALTER TABLE wp_options AUTO_INCREMENT='+str(sequence))
            assert int(a03.sql(db,sequence_query).stdout.splitlines()[-1])==sequence
        write(OUT/(storage+'-'+label+'-call.json'),{'command':args+(extra or []),'exit':result.returncode,'stderr':result.stderr,'stdout':result.stdout,'duration_seconds':time.monotonic()-started})
        return result
    def checkpoint():return json.loads((state/'etat.json').read_text())
    def fp():return {'database':a03.fingerprint(db,True),'files':a03.filemap(site)}
    log_path=json.loads(settings.read_text())['php_error_log']
    server=subprocess.Popen(['php','-d','log_errors=1','-d','display_errors=0','-d','date.timezone=UTC','-d','error_log='+log_path,'-S','127.0.0.1:18803','-t',str(site)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    time.sleep(.5)
    try:
        read_mode()
        first=invoke('before')
        check(storage+':audit_before_native',first.returncode==75 and list(checkpoint()['done'])==['audit','avant'],first.stderr)
        check(storage+':no_mutations_before_gate',orphan.is_dir() and debris.is_dir() and not (state/'a04').exists() and not (state/'a05').exists())
        native_before=checkpoint()['done']['avant']
        # Deliberately OMIT required maintenance: real A04 refuses in the middle.
        (site/'wp-config.php').write_text(config)
        prior=fp()
        refused=invoke('refusal',['--mutations-ready'])
        cp=checkpoint()
        write(OUT/(storage+'-refused-checkpoint.json'),cp)
        check(storage+':real_middle_refusal',refused.returncode==1 and cp['attempts'][-1]['step']=='mise-a-jour' and (state/'mise-a-jour-1-stderr.log').read_text()=='A04_MAINTENANCE\n')
        check(storage+':refusal_no_later_step',list(cp['done'])==['audit','avant'] and len(cp['attempts'])==3 and not (state/'a05').exists() and not (state/'apres-1').exists())
        check(storage+':refusal_database_files_exact',prior==fp())
        write_mode()
        resumed=invoke('resumed',['--mutations-ready'])
        cp=checkpoint()
        check(storage+':resume_update_cleanup_native',resumed.returncode==75 and list(cp['done'])==['audit','avant','mise-a-jour','nettoyage'],resumed.stderr)
        check(storage+':before_not_replayed',cp['done']['avant']==native_before and len([r for r in cp['attempts'] if r['step']=='avant'])==1)
        inventory_after=cleaner.inspect_site(site)
        check(storage+':cleanup_effects_real','a08-orphan/entry.php' not in inventory_after['plugins'] and not orphan.exists() and not debris.exists() and not any(r['name']=='wp_a08_orphan' for r in inventory_after['tables']) and not any(r['name']=='a08_orphan_setting' for r in inventory_after['options']) and not any(r['name']=='a08_orphan_hook' for r in inventory_after['cron']))
        check(storage+':native_maintenance_preserved', (site/'.maintenance').is_file() and (site/'wp-content/mu-plugins/001-imagine-a04-maintenance.php').is_file())
        read_mode()
        reception=invoke('after',['--reception-ready'])
        cp=checkpoint();write(OUT/(storage+'-first-complete.json'),cp)
        comparison=json.loads((state/'comparaison-1-stdout.log').read_text())
        check(storage+':complete_native_expected_only',reception.returncode==0 and len(cp['done'])==6 and cp['comparison']['anormal']==0 and (state/'comparaison-1-receipt.json').is_file() and json.loads((state/'comparaison-1-receipt.json').read_text())['exit']==3 and all(r['class']=='attendu' for r in comparison['changes']),cp['comparison'])
        # Full second pass: all six tools really run, same native mutation checkpoints.
        second_before=fp()
        started=invoke('second-before',['--new-pass'])
        check(storage+':second_pass_restarts_audit_before',started.returncode==75 and list(checkpoint()['done'])==['audit','avant'])
        check(storage+':second_readonly_before_exact',second_before==fp())
        write_mode();mutation_before=fp()
        second=invoke('second-mutations',['--mutations-ready'])
        check(storage+':second_native_mutations_no_effect',second.returncode==75 and mutation_before==fp(),second.stderr)
        read_mode();reception_before=fp()
        final=invoke('second-after',['--reception-ready'])
        cp=checkpoint()
        check(storage+':second_comparison_identical',final.returncode==0 and len(cp['done'])==6 and len(cp['passes'])==1 and cp['comparison']=={'attendu':0,'anormal':0} and json.loads((state/'comparaison-2-stdout.log').read_text())['changes']==[])
        check(storage+':second_readonly_after_exact',reception_before==fp())
        check(storage+':second_all_six_tools_really_run',len(cp['attempts'])==13 and all(len([r for r in cp['attempts'] if r['step']==name])==(3 if name=='mise-a-jour' else 2) for name in ['audit','avant','mise-a-jour','nettoyage','apres','comparaison']))
        for name in ['avant-1','apres-1','avant-2','apres-2']:
            photo=json.loads((state/name/'non-regression.json').read_text())
            check(storage+':photo_'+name+'_native_storage_and_clean_log',photo['storage']==storage and photo['php_log']['checked'] is True and photo['php_log']['errors']==0)
        text=(state/'rapport.md').read_text()
        check(storage+':single_report_six_rows_private',len(list(state.glob('rapport*.md')))==1 and all('| '+name+' |' in text for name in ['audit','avant','mise-a-jour','nettoyage','apres','comparaison']) and not any(token in text for token in ['@example.org','Fiction','a08_orphan_setting']))
        write(OUT/(storage+'-inventory.json'),{'before':inventory,'after':inventory_after})
        # Root safety MU is byte-identical throughout both boundary preparations.
        check(storage+':staging_guard_bytes_unchanged',sha(site/'wp-content/mu-plugins/000-imagine-staging-safety.php')==sha('/subject/000-imagine-staging-safety.php'))
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
            except Exception as error:
                CHECKS.append({'check':storage+':exception','ok':False,'class':type(error).__name__,'code':str(error)[:1000]})
                print(json.dumps(CHECKS[-1]),flush=True)
        check('network_none',[p.name for p in pathlib.Path('/sys/class/net').iterdir()]==['lo'])
        for path in ['/proc/net/tcp','/proc/net/tcp6']:
            check('no_listener:'+path,not any(line.split()[3]=='0A' for line in pathlib.Path(path).read_text().splitlines()[1:]))
    finally:
        db.terminate();db.wait(timeout=30)
        result={'suite':'A08-real-synthetic-classic-hpos','checks':CHECKS,'exit_code':int(any(not row['ok'] for row in CHECKS))}
        write(OUT/'result.json',result)
    return result['exit_code']


if __name__=='__main__':sys.exit(main())
