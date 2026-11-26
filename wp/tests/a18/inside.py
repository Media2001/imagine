"""A18 real WordPress/Woo native read-only receipt; fixtures only."""
import ctypes,importlib.util,json,os,re,sys
from pathlib import Path
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('fixture','/opt/a02/inside.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
original=b.check
def check(name,ok,detail=None):
    if name.endswith(':commercial_fixture'):detail={k:detail[k] for k in ['versions','hpos','subscriptions','rules','restriction_real']}
    return original(name,ok,detail)
b.check=check
OUT=Path('/report')
def inventory(site,out,audit):
    return b.cmd(['python3','/subject/a18/confine.py','--wp-path='+str(site),'--output='+str(out),'--audit='+str(audit)],check=False)
def run_storage(storage):
    site,db,_=b.install(storage);(OUT/(storage+'-seed.json')).unlink()
    cfg=(site/'wp-config.php').read_text();writable=cfg.replace("define('DB_USER', 'a02_"+storage+"')","define('DB_USER', 'root')").split("\nfile_put_contents('/scratch/a02-bootstrap-trap'")[0]
    (site/'wp-config.php').write_text(writable)
    try:
        p=b.wp(site,['eval-file','/opt/a18/seed.php','--use-include']);oracle=json.loads(next(x[9:] for x in p.stdout.splitlines() if x.startswith('A18_JSON=')))
    finally:(site/'wp-config.php').write_text(cfg)
    mu=site/'wp-content/mu-plugins/a18-runtime.php';mu.write_text('''<?php
if (getenv('A18_CONFINED') === '1' && ($forced = get_option('a18_forced_exception', '')) !== '') {
 throw new RuntimeException($forced);
}
if (getenv('A18_CONFINED') === '1') {
 global $wpdb; require_once ABSPATH.'wp-includes/pluggable.php';
 if ($wpdb->query('UPDATE wp_posts SET ID=ID WHERE 1=0') !== false
 || @mysqli_query($wpdb->dbh,'UPDATE wp_posts SET ID=ID WHERE 1=0') !== false
 || @file_put_contents(ABSPATH.'forbidden','NO') !== false
 || wp_mail('fictif@example.org','A18_PRIVATE_CANARY','A18_PRIVATE_CANARY') !== false
 || !is_wp_error(wp_remote_get('https://forbidden.invalid/'))
 || wp_schedule_single_event(time()+9999,'a18_forbidden') !== false
 || function_exists('mail') || function_exists('exec')) { throw new RuntimeException('A18_EARLY_GUARDS_FAILED'); }
 echo 'A18_BOOT_PRIVATE_CANARY';
}
''')
    audit=OUT/(storage+'-audit');b.check(storage+':a02_audit',b.audit(site,audit).returncode==0)
    before=b.fingerprint(db);files=b.files(site);(OUT/(storage+'-db-before.json')).write_text(json.dumps(before))
    # Kernel observations only around the subject; the oracle fingerprints are outside this interval.
    libc=ctypes.CDLL(None,use_errno=True);fd=libc.inotify_init1(os.O_NONBLOCK)
    assert fd>=0
    for f in Path(oracle['uploads']).rglob('*'):
        if f.is_file():assert libc.inotify_add_watch(fd,str(f).encode(),0x21)>=0 # IN_ACCESS|IN_OPEN
    dest=OUT/(storage+'-retention');p=inventory(site,dest,audit/'audit.json')
    try:events=os.read(fd,65536)
    except BlockingIOError:events=b''
    finally:os.close(fd)
    b.check(storage+':cli_and_actual_readonly_guards',p.returncode==0,{'exit':p.returncode,'stderr':p.stderr[:120]})
    b.check(storage+':media_contents_never_opened',events==b'')
    d=json.loads((dest/'conservation.json').read_text());groups=d['database']['groups']
    by={(r['scope'],r['key']):{k:r[k] for k in ['iban','card','national']} for r in groups}
    for scope,key,want in [('account','_a18_card',{'iban':0,'card':1,'national':0}),('account','_a18_rr',{'iban':0,'card':0,'national':1}),('order','_a18_bank',{'iban':1,'card':0,'national':0}),('subscription','_a18_bank',{'iban':1,'card':0,'national':0}),('option','a18_bank_setting',{'iban':1,'card':0,'national':0})]:
        b.check(storage+':exact_group:'+scope+':'+key,by.get((scope,key))==want)
    b.check(storage+':invalid_and_canary_values_not_counted',not any(k in {'a18_invalid_setting','_a18_canary'} for _,k in by))
    b.check(storage+':tokens_references_separate',d['payment_tokens']==[{'gateway':'a18_fixture','type':'CC','count':1}])
    b.check(storage+':known_and_other_folders_exact',d['media']==[
        {'folder':'autre','directories':2,'files':{'txt':1},'bytes':4,'server_rule_file_present':False,'reading_denied':None},
        {'folder':'exports','directories':1,'files':{'csv':2,'log':1},'bytes':12,'server_rule_file_present':False,'reading_denied':None},
        {'folder':'woocommerce_uploads','directories':1,'files':{'html':1,'regles':1},'bytes':13,'server_rule_file_present':True,'reading_denied':None}])
    payload=p.stdout+p.stderr+''.join(x.read_text() for x in dest.iterdir())
    b.check(storage+':no_values_names_ids_or_paths',not re.search(r'CANARY|4242|5390|850730|@|/scratch|DB_PASSWORD',payload))
    repeat=OUT/(storage+'-repeat');p=inventory(site,repeat,audit/'audit.json');b.check(storage+':replay_identical',p.returncode==0 and {x.name:x.read_bytes() for x in repeat.iterdir()}=={x.name:x.read_bytes() for x in dest.iterdir()})
    for label,path in [('exists',dest),('site',site/'forbidden'),('repo',Path('/subject/forbidden')),('ancestor',site.parent/'forbidden'),('root',Path('/forbidden'))]:
        bad=inventory(site,path,audit/'audit.json');b.check(storage+':guard:'+label,bad.returncode==1 and (path==dest or not path.exists()))
    raw=b.cmd(['php','/subject/a18/inventorier-conservation','--wp-path='+str(site),'--output=/report/'+storage+'-raw','--audit='+str(audit/'audit.json')],check=False)
    b.check(storage+':unconfined_refused',raw.returncode==1 and raw.stderr=='A18_CONFINEMENT_REQUIRED\n')
    for directory in [False,True]:
        link=site/('A18_PERSONAL_SYMLINK_CANARY'+str(directory));link.symlink_to(site/'wp-content' if directory else site/'wp-config.php',target_is_directory=directory)
        try:
            bad=inventory(site,OUT/(storage+'-symlink-'+str(directory)),audit/'audit.json')
            b.check(storage+':symlink_private_code_only:'+str(directory),bad.returncode==1 and bad.stdout=='' and bad.stderr=='A11_SYMLINK_UNSUPPORTED\n' and not (OUT/(storage+'-symlink-'+str(directory))).exists())
        finally:link.unlink()
    for index,name in enumerate(['wp-content/db.php','wp-content/object-cache.php','wp-content/advanced-cache.php','wp-content/sunrise.php','wordfence-waf.php','.user.ini']):
        f=site/name;f.write_text('<?php throw new RuntimeException("A18_PRIVATE_CANARY");')
        try:
            bad=inventory(site,OUT/(storage+'-dropin-'+str(index)),audit/'audit.json');b.check(storage+':closed_dropin:'+str(index),bad.returncode==1 and bad.stdout=='' and bad.stderr=='A11_DROPIN_UNSUPPORTED '+json.dumps({'file':name},separators=(',',':'))+'\n')
        finally:f.unlink()
    after=b.fingerprint(db);(OUT/(storage+'-db-after.json')).write_text(json.dumps(after));b.check(storage+':all_tables_scheduler_identical',before==after);b.check(storage+':files_identical',files==b.files(site));b.check(storage+':config_not_executed',not Path('/scratch/a02-bootstrap-trap').exists())
    # A synthetic variant carries only the existing importer provenance mark, never an invented historical count.
    b.sql(db,"INSERT INTO wp_options (option_name,option_value,autoload) VALUES ('imagine_staging_disabled_plugins','a:0:{}','no')")
    neutral_before=b.fingerprint(db);neutral_out=OUT/(storage+'-neutralised');p=inventory(site,neutral_out,audit/'audit.json');nd=json.loads((neutral_out/'conservation.json').read_text())
    b.check(storage+':neutralised_unknown_not_zero',p.returncode==0 and nd['database']=={'status':'inconnu après neutralisation','groups':None} and nd['payment_tokens']==d['payment_tokens'])
    b.check(storage+':neutralised_database_unchanged',neutral_before==b.fingerprint(db))
    # Rules presence must not be confused with effective server protection: contents remain unread.
    (Path(oracle['uploads'])/'exports/.htaccess').write_text('Require all denied\n')
    rule_before=b.files(site);rules_out=OUT/(storage+'-rules');p=inventory(site,rules_out,audit/'audit.json');rd=json.loads((rules_out/'conservation.json').read_text())
    b.check(storage+':rule_presence_not_false_assurance',p.returncode==0 and rd['media'][1]['server_rule_file_present'] is True and rd['media'][1]['reading_denied'] is None)
    b.check(storage+':rule_variant_files_unchanged',rule_before==b.files(site))
    b.check(storage+':all_produced_artifacts_canary_absent',not any(b'CANARY' in f.read_bytes() for f in OUT.rglob('*') if f.is_file()))
b.run_storage=run_storage
if __name__=='__main__':sys.exit(b.main())
