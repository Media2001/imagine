"""Native synthetic A20 acceptance; every child uses explicit UTF-8."""
import importlib.util,json,os,re,shlex,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('fixture','/opt/a02/inside.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
def cmd(args,check=True,env=None,data=None,timeout=240):
    p=subprocess.run(args,input=data,capture_output=True,text=True,encoding='utf-8',errors='strict',timeout=timeout,
        env={**os.environ,'PYTHONIOENCODING':'utf-8','PYTHONUTF8':'1','PYTHONDONTWRITEBYTECODE':'1',**(env or {})})
    if check and p.returncode:
        raise RuntimeError('A20_FIXTURE_COMMAND_FAILED')
    return p
b.cmd=cmd
original=b.check
def check(name,ok,detail=None):
    if name.endswith(':commercial_fixture'):detail={k:detail[k] for k in ['versions','hpos','subscriptions','rules','restriction_real']}
    return original(name,ok,detail)
b.check=check
OUT=Path('/report')
def inventory(site,out,audit,*extra):
    return b.cmd(['python3','/subject/a20/confine.py','--wp-path='+str(site),'--audit='+str(audit),'--output='+str(out),*extra],check=False)
def run_storage(storage):
    site,db,_=b.install(storage);(OUT/(storage+'-seed.json')).unlink()
    cfg=(site/'wp-config.php').read_text(encoding='utf-8')
    writable=cfg.replace("define('DB_USER', 'a02_"+storage+"')","define('DB_USER', 'root')").split("\nfile_put_contents('/scratch/a02-bootstrap-trap'")[0]
    (site/'wp-config.php').write_text(writable,encoding='utf-8')
    try:
        p=b.wp(site,['eval-file','/opt/a20/seed.php','--use-include'])
        oracle=json.loads(next(x[9:] for x in p.stdout.splitlines() if x.startswith('A20_JSON=')))
    finally:(site/'wp-config.php').write_text(cfg,encoding='utf-8')
    (OUT/(storage+'-oracle.json')).write_text(json.dumps(oracle),encoding='utf-8')
    b.check(storage+':native_fixture',oracle['native_count']==9 and [r[0] for r in oracle['observed']]==['active']*5+['pending','on-hold','pending-cancel','expired'] and oracle['observed'][5][1:]==['month',1,'9.17','FR',1] and oracle['observed'][7][-1]==3)
    mu=site/'wp-content/mu-plugins/a20-runtime.php';mu.write_text('''<?php
if (getenv('A20_CONFINED') === '1') {
 global $wpdb; require_once ABSPATH.'wp-includes/pluggable.php';
 if ($wpdb->query('UPDATE wp_posts SET ID=ID WHERE 1=0') !== false
 || @mysqli_query($wpdb->dbh,'UPDATE wp_posts SET ID=ID WHERE 1=0') !== false
 || @file_put_contents(ABSPATH.'forbidden','NO') !== false
 || wp_mail('fictif@example.org','A20_PRIVATE_CANARY','A20_PRIVATE_CANARY') !== false
 || !is_wp_error(wp_remote_get('https://forbidden.invalid/'))
 || wp_schedule_single_event(time()+9999,'a20_forbidden') !== false
 || function_exists('mail') || function_exists('exec')) { throw new RuntimeException('A20_EARLY_GUARDS_FAILED'); }
 if (get_option('a20_forced_exception') === 'yes') { throw new RuntimeException('A20_PLUGIN_PERSON_NAME_PRIVATE_CANARY'); }
 echo 'A20_BOOT_PRIVATE_CANARY';
}
''',encoding='utf-8')
    audit=OUT/(storage+'-audit');b.check(storage+':a02_audit',b.audit(site,audit).returncode==0)
    before=b.fingerprint(db);files=b.files(site);(OUT/(storage+'-db-before.json')).write_text(json.dumps(before),encoding='utf-8')
    dest=OUT/(storage+'-prices');p=inventory(site,dest,audit/'audit.json')
    b.check(storage+':native_confined_success',p.returncode==0,{'exit':p.returncode,'stderr':p.stderr[:120]})
    d=json.loads((dest/'tarifs.json').read_text(encoding='utf-8'));v=d['counts']
    expected={'live_subscriptions':8,'multiple_product_lines':1,'without_product_line':0,'with_fee_line':1,'with_shipping_line':2,'foreign_currency':1,'zero_recurring_total':1,
        'countries':[{'country':'BE','count':5,'with_shipping':0}],'other_countries':{'count':2,'with_shipping':2},'unknown_country':{'count':1,'with_shipping':0}}
    for key,want in expected.items():b.check(storage+':exact:'+key,v.get(key)==want,{'actual':v.get(key),'expected':want})
    p1={'product':oracle['product'],'variation':0,'count':7,'states':{'active':5,'pending':1,'on-hold':0,'pending-cancel':1},'schedules':[{'interval':1,'period':'month','count':1},{'interval':1,'period':'year','count':6}],'non_annual':1,'amounts':[{'currency':'EUR','amount':'100.00','count':5}],'other_amounts':2}
    p2={'product':oracle['parent'],'variation':oracle['variation'],'count':2,'states':{'active':0,'pending':0,'on-hold':1,'pending-cancel':1},'schedules':[{'interval':1,'period':'year','count':2}],'non_annual':0,'amounts':[],'other_amounts':2}
    b.check(storage+':exact_product_counts',v['products']==[p1,p2],{'actual':v['products'],'expected':[p1,p2]})
    b.check(storage+':all_counts_explained',all(key in v['definitions'] for key in [*expected,'products','states','schedules','non_annual','amounts','other_amounts']))
    payload=p.stdout+p.stderr+''.join(x.read_text(encoding='utf-8') for x in dest.iterdir())
    b.check(storage+':privacy_no_names_paths_ids_rare_amount_country',not re.search(r'CANARY|@|/scratch|DB_PASSWORD|"(?:user|customer|subscription_id|order_id|id)"|9\.17|80\.19|1234567\.89|"(?:FR|DE|US)"',payload))
    b.check(storage+':private_output_permissions',dest.stat().st_mode&0o777==0o700 and all(x.stat().st_mode&0o777==0o600 for x in dest.iterdir()))
    again=OUT/(storage+'-repeat');q=inventory(site,again,audit/'audit.json');b.check(storage+':replay_identical',q.returncode==0 and {x.name:x.read_bytes() for x in dest.iterdir()}=={x.name:x.read_bytes() for x in again.iterdir()})
    # Parse the published operator line, replacing path placeholders only; no extra argument.
    line=next(x for x in Path('/subject/a20/README.md').read_text(encoding='utf-8').splitlines() if x.startswith('python3 wp/outils/bascule/a20/confine.py '))
    command=shlex.split(line);destdoc=OUT/(storage+'-documented')
    replacements={'wp/outils/bascule/a20/confine.py':'/subject/a20/confine.py','--wp-path=/copie-verifiee':'--wp-path='+str(site),'--audit=/hors-web/audit-date/audit.json':'--audit='+str(audit/'audit.json'),'--output=/hors-web/tarifs-date':'--output='+str(destdoc)}
    command=[replacements.get(x,x) for x in command];q=b.cmd(command,check=False)
    b.check(storage+':documented_command_only_given_arguments',len(command)==5 and q.returncode==0 and q.stdout=='A20_OK tarifs.json tarifs.md\n' and q.stderr=='' and json.loads((destdoc/'tarifs.json').read_text())==d)
    for label,path in [('exists',dest),('site',site/'forbidden'),('repo',Path('/subject/forbidden')),('ancestor',site.parent/'forbidden'),('root',Path('/forbidden'))]:
        q=inventory(site,path,audit/'audit.json');b.check(storage+':guard:'+label,q.returncode==1 and q.stdout=='' and re.fullmatch(r'A(?:20|12)_[A-Z_]+\n',q.stderr) is not None and (path==dest or not path.exists()))
    raw=b.cmd(['php','/subject/a20/inventorier-tarifs','--wp-path='+str(site),'--audit='+str(audit/'audit.json'),'--output=/report/'+storage+'-raw'],check=False)
    b.check(storage+':unconfined_refused',raw.returncode==1 and raw.stdout=='' and raw.stderr=='A20_CONFINEMENT_REQUIRED\n')
    for directory in [False,True]:
        link=site/('A20_PERSON_SYMLINK_PRIVATE_CANARY'+str(directory));link.symlink_to(site/'wp-content' if directory else site/'wp-config.php',target_is_directory=directory)
        try:
            out=OUT/(storage+'-symlink-'+str(directory));q=inventory(site,out,audit/'audit.json');b.check(storage+':symlink_closed:'+str(directory),q.returncode==1 and q.stdout=='' and q.stderr=='A11_SYMLINK_UNSUPPORTED\n' and not out.exists())
        finally:link.unlink()
    for index,name in enumerate(['wp-content/db.php','wp-content/object-cache.php','wp-content/advanced-cache.php','wp-content/sunrise.php','wordfence-waf.php','.user.ini']):
        f=site/name;f.write_text('<?php throw new RuntimeException("A20_PRIVATE_CANARY");',encoding='utf-8')
        try:
            out=OUT/(storage+'-dropin-'+str(index));q=inventory(site,out,audit/'audit.json');b.check(storage+':closed_dropin:'+str(index),q.returncode==1 and q.stdout=='' and q.stderr=='A11_DROPIN_UNSUPPORTED '+json.dumps({'file':name},separators=(',',':'))+'\n' and not out.exists())
        finally:f.unlink()
    for label,statement in [('define',"define('A20_CONFIG_PRIVATE_CANARY', 'A20_VALUE_PRIVATE_CANARY');"),('const',"const A20_CONFIG_PRIVATE_CANARY = 'A20_VALUE_PRIVATE_CANARY';")]:
        (site/'wp-config.php').write_text(cfg+'\n'+statement+'\n',encoding='utf-8')
        try:
            out=OUT/(storage+'-config-'+label);q=inventory(site,out,audit/'audit.json');b.check(storage+':config_closed:'+label,q.returncode==1 and q.stdout=='' and q.stderr=='A11_CONFIG_OVERRIDE_UNSUPPORTED\n' and not out.exists())
        finally:(site/'wp-config.php').write_text(cfg,encoding='utf-8')
    rootcfg=cfg.replace("define('DB_USER', 'a02_"+storage+"')", "define('DB_USER', 'root')")
    (site/'wp-config.php').write_text(rootcfg,encoding='utf-8')
    try:
        rootout=OUT/(storage+'-root-readonly');q=inventory(site,rootout,audit/'audit.json')
        b.check(storage+':transaction_readonly_even_root',q.returncode==0 and q.stdout=='A20_OK tarifs.json tarifs.md\n' and q.stderr=='' and json.loads((rootout/'tarifs.json').read_text())==d and before==b.fingerprint(db))
    finally:(site/'wp-config.php').write_text(cfg,encoding='utf-8')
    bad_audit=OUT/(storage+'-invalid-audit');bad_audit.mkdir()
    for label,photo,want in [('schema',{'schema':'A20_PRIVATE_CANARY'},'A20_AUDIT_GUARD'),('storage',json.loads((audit/'audit.json').read_text()),'A20_AUDIT_STORAGE_MISMATCH')]:
        if label=='storage':photo['sections']['commerce']['order_storage']='classic' if storage=='hpos' else 'hpos'
        file=bad_audit/'audit.json';file.write_text(json.dumps(photo),encoding='utf-8')
        out=OUT/(storage+'-bad-audit-'+label);q=inventory(site,out,file)
        b.check(storage+':audit_guard:'+label,q.returncode==1 and q.stdout=='' and q.stderr==want+'\n' and not out.exists())
    # Invalid synthetic audit inputs are not retained as operator evidence.
    (bad_audit/'audit.json').unlink();bad_audit.rmdir()
    after=b.fingerprint(db);(OUT/(storage+'-db-after.json')).write_text(json.dumps(after),encoding='utf-8')
    b.check(storage+':all_tables_scheduler_identical',before==after)
    b.check(storage+':files_identical',files==b.files(site));b.check(storage+':config_not_executed',not Path('/scratch/a02-bootstrap-trap').exists())
    b.sql(db,"INSERT INTO wp_options (option_name,option_value,autoload) VALUES ('a20_forced_exception','yes','no')")
    variant=b.fingerprint(db);q=inventory(site,OUT/(storage+'-exception'),audit/'audit.json')
    b.check(storage+':plugin_exception_closed',q.returncode==1 and q.stdout=='' and q.stderr=='A20_INVENTORY_FAILED\n' and not (OUT/(storage+'-exception')).exists())
    b.check(storage+':exception_database_identical',variant==b.fingerprint(db))
    b.check(storage+':all_artifacts_canary_absent',not any(b'CANARY' in f.read_bytes() for f in OUT.rglob('*') if f.is_file()))
b.run_storage=run_storage
if __name__=='__main__':sys.exit(b.main())
