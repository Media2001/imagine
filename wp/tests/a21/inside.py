"""A21 synthetic native fixture, two stores; reuse unchanged A02 engine."""
import datetime
import importlib.util
import json
import re
import shlex
import sys
from pathlib import Path
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('fixture','/opt/a02/inside.py')
b=importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
original=b.check
def check(name,ok,detail=None):
    if name.endswith(':commercial_fixture'):
        detail={k:detail[k] for k in ['versions','hpos','subscriptions','rules','restriction_real']}
    return original(name,ok,detail)
b.check=check
OUT=Path('/report')
def invoke(site,out,audit,*extra):
    return b.cmd(['python3','/subject/a21/confine.py','--wp-path='+str(site),'--audit='+str(audit),'--output='+str(out),*extra],check=False)
def run_storage(storage):
    site,db,_=b.install(storage)
    (OUT/(storage+'-seed.json')).unlink()
    cfg=(site/'wp-config.php').read_text()
    writable=cfg.replace("define('DB_USER', 'a02_"+storage+"')","define('DB_USER', 'root')").split("\nfile_put_contents('/scratch/a02-bootstrap-trap'")[0]
    (site/'wp-config.php').write_text(writable)
    try:
        p=b.wp(site,['eval-file','/opt/a21/seed.php','--use-include'])
        oracle=json.loads(next(x[9:] for x in p.stdout.splitlines() if x.startswith('A21_JSON=')))
    finally:
        (site/'wp-config.php').write_text(cfg)
    (OUT/(storage+'-oracle.json')).write_text(json.dumps(oracle))
    b.check(storage+':fixture_native_readback',oracle=={'keys':2,'webhooks':4,'store_connected_native':True})
    mu=site/'wp-content/mu-plugins/a21-probe.php'
    mu.write_text('''<?php
if (getenv('A21_CONFINED') === '1') {
    $forced = get_option('a21_forced_exception', '');
    if ($forced !== '') { throw new RuntimeException($forced); }
    add_action('woocommerce_webhook_delivery', static function () { throw new RuntimeException('A21_DELIVERY_ATTEMPT_CANARY'); });
    if (get_option('a21_probe_guards') === 'yes') {
        global $wpdb; require_once ABSPATH.'wp-includes/pluggable.php';
        if ($wpdb->query('UPDATE wp_posts SET ID=ID WHERE 1=0') !== false
            || @mysqli_query($wpdb->dbh,'UPDATE wp_posts SET ID=ID WHERE 1=0') !== false
            || @file_put_contents(ABSPATH.'forbidden','NO') !== false
            || wp_mail('fictif@example.org','CANARY','CANARY') !== false
            || !is_wp_error(wp_remote_get('https://forbidden.invalid/'))
            || wp_schedule_single_event(time()+9999,'a21_forbidden') !== false
            || function_exists('mail') || function_exists('exec')) { throw new RuntimeException('A21_GUARDS_FAILED'); }
    }
}
''')
    audit=OUT/(storage+'-audit')
    b.check(storage+':a02_audit',b.audit(site,audit).returncode==0)
    before=b.fingerprint(db)
    files=b.files(site)
    (OUT/(storage+'-db-before.json')).write_text(json.dumps(before))
    dest=OUT/(storage+'-portes')
    # Literal documented command, only placeholder paths substituted; no added date argument.
    line=next(x for x in Path('/subject/a21/README.md').read_text().splitlines() if x.startswith('python3 /chemin/du/depot/'))
    cmd=line.replace('/chemin/du/depot/wp/outils/bascule','/subject').replace('/copie-verifiee',str(site)).replace('/hors-web/audit-date/audit.json',str(audit/'audit.json')).replace('/hors-web/portes-date',str(dest))
    start=datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
    p=b.cmd(shlex.split(cmd),check=False)
    end=datetime.datetime.now(datetime.timezone.utc)
    b.check(storage+':documented_three_argument_command',p.returncode==0 and p.stdout=='A21_OK portes.json portes.md\n' and p.stderr=='',{'exit_code':p.returncode,'stderr':p.stderr[:120]})
    d=json.loads((dest/'portes.json').read_text())
    instant=datetime.datetime.strptime(d['as_of_utc'],'%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=datetime.timezone.utc)
    b.check(storage+':default_clock_actual_utc',start<=instant<=end)
    b.check(storage+':keys_exact',d['api_keys']=={'status':'connu','counts':{'total':2,'by_permission':{'read':1,'write':0,'read_write':1,'unknown':0},'never_used':1,'unused_twelve_months':1,'last_access_unknown':0}})
    b.check(storage+':webhooks_exact',d['webhooks']=={'status':'connu','counts':{'total':4,'by_status':{'active':2,'paused':1,'disabled':1,'unknown':0},'by_topic':{'order.created':1,'order.updated':1,'product.updated':1,'unknown':1},'active_destination':{'same_domain':1,'external_domain':1,'unknown':0}}})
    b.check(storage+':store_connection_native_boolean',d['extension_store']=={'status':'connu','connected':True})
    b.check(storage+':zero_outbound_attempts',d['outbound_attempts']=={'http':0,'mail':0,'scheduled':0})
    payload=p.stdout+p.stderr+''.join(x.read_text() for x in dest.iterdir())
    b.check(storage+':no_secrets_fragments_addresses_names_paths',not re.search(r'CANARY|@|example\.org|synthetic\.test|/scratch|987654|consumer_key|consumer_secret|description|delivery_url|truncated_key',payload))
    b.check(storage+':private_permissions',dest.stat().st_mode&0o777==0o700 and all(x.stat().st_mode&0o777==0o600 for x in dest.iterdir()))
    repeat=OUT/(storage+'-repeat')
    rp=invoke(site,repeat,audit/'audit.json','--as-of='+d['as_of_utc'])
    b.check(storage+':frozen_replay_identical',rp.returncode==0 and {f.name:f.read_bytes() for f in dest.iterdir()}=={f.name:f.read_bytes() for f in repeat.iterdir()})
    for label,path in [('exists',dest),('site',site/'forbidden'),('repo',Path('/subject/forbidden')),('ancestor',site.parent/'forbidden'),('root',Path('/forbidden'))]:
        bad=invoke(site,path,audit/'audit.json')
        b.check(storage+':output_guard:'+label,bad.returncode==1 and bad.stdout=='' and (path==dest or not path.exists()) and 'CANARY' not in bad.stderr)
    raw=b.cmd(['php','/subject/a21/inventorier-portes','--wp-path='+str(site),'--output=/report/'+storage+'-raw','--audit='+str(audit/'audit.json')],check=False)
    b.check(storage+':unconfined_refused',raw.returncode==1 and raw.stdout=='' and raw.stderr=='A21_CONFINEMENT_REQUIRED\n')
    for directory in [False,True]:
        link=site/('A21_PERSONAL_SYMLINK_CANARY'+str(directory))
        link.symlink_to(site/'wp-content' if directory else site/'wp-config.php',target_is_directory=directory)
        try:
            out=OUT/(storage+'-symlink-'+str(directory));bad=invoke(site,out,audit/'audit.json')
            b.check(storage+':closed_symlink:'+str(directory),bad.returncode==1 and bad.stdout=='' and bad.stderr=='A11_SYMLINK_UNSUPPORTED\n' and not out.exists())
        finally:
            link.unlink()
    for index,name in enumerate(['wp-content/db.php','wp-content/object-cache.php','wp-content/advanced-cache.php','wp-content/sunrise.php','wordfence-waf.php','.user.ini']):
        f=site/name;f.write_text('<?php throw new RuntimeException("CANARY");')
        try:
            out=OUT/(storage+'-dropin-'+str(index));bad=invoke(site,out,audit/'audit.json')
            b.check(storage+':closed_dropin:'+str(index),bad.returncode==1 and bad.stdout=='' and bad.stderr=='A11_DROPIN_UNSUPPORTED '+json.dumps({'file':name},separators=(',',':'))+'\n' and not out.exists())
        finally:
            f.unlink()
    for label,statement in [('define',"define('A21_CONFIG_CANARY','CANARY');"),('const',"const A21_CONFIG_CANARY='CANARY';")]:
        (site/'wp-config.php').write_text(cfg+'\n'+statement+'\n')
        try:
            out=OUT/(storage+'-config-'+label);bad=invoke(site,out,audit/'audit.json')
            b.check(storage+':closed_config:'+label,bad.returncode==1 and bad.stdout=='' and bad.stderr=='A11_CONFIG_OVERRIDE_UNSUPPORTED\n' and not out.exists())
        finally:
            (site/'wp-config.php').write_text(cfg)
    out=OUT/(storage+'-bad-clock');bad=invoke(site,out,audit/'audit.json','--as-of=2026-02-30T00:00:00Z')
    b.check(storage+':closed_invalid_clock',bad.returncode==1 and bad.stdout=='' and bad.stderr=='A21_CLOCK_INVALID\n' and not out.exists())
    after=b.fingerprint(db)
    (OUT/(storage+'-db-after.json')).write_text(json.dumps(after))
    b.check(storage+':all_tables_scheduler_identical',before==after)
    b.check(storage+':all_files_identical',files==b.files(site))
    b.check(storage+':config_never_executed',not Path('/scratch/a02-bootstrap-trap').exists())
    b.sql(db,"INSERT INTO wp_options (option_name,option_value,autoload) VALUES ('a21_probe_guards','yes','no')")
    guard_before=b.fingerprint(db)
    guard=OUT/(storage+'-guards');gp=invoke(site,guard,audit/'audit.json')
    b.check(storage+':real_kernel_sql_mail_http_cron_guards',gp.returncode==0 and json.loads((guard/'portes.json').read_text())['outbound_attempts']=={'http':1,'mail':1,'scheduled':1})
    b.check(storage+':guard_probe_database_unchanged',guard_before==b.fingerprint(db))
    b.sql(db,"DELETE FROM wp_options WHERE option_name='a21_probe_guards'")
    for index,exception in enumerate(['A21_SITE_DERIVED_CANARY','A21_PRIVATE_CANARY_PATH','A21_USAGE CANARY']):
        b.sql(db,"INSERT INTO wp_options (option_name,option_value,autoload) VALUES ('a21_forced_exception','"+exception+"','no')")
        refusal_before=b.fingerprint(db);out=OUT/(storage+'-exception-'+str(index));bad=invoke(site,out,audit/'audit.json')
        b.check(storage+':closed_site_exception:'+str(index),bad.returncode==1 and bad.stdout=='' and bad.stderr=='A21_INVENTORY_FAILED\n' and not out.exists())
        b.check(storage+':exception_database_unchanged:'+str(index),refusal_before==b.fingerprint(db))
        b.sql(db,"DELETE FROM wp_options WHERE option_name='a21_forced_exception'")
    # Untrusted bootstrap output must never escape the PHP subprocess supervisor.
    hostile=site/'wp-content/mu-plugins/a21-hostile.php'
    fixtures={
        'stdout': "fwrite(STDOUT, __FILE__.' A21_FLOW_CANARY');",
        'stderr': "fwrite(STDERR, __FILE__.' A21_FLOW_CANARY');",
        'early_exit': "exit('A21_FLOW_CANARY');",
        'empty_exit': "exit(0);",
        'forged_success': 'fwrite(STDOUT, "A21_OK portes.json portes.md\\n"); exit(0);',
        'shutdown_stdout': "register_shutdown_function(static function () { fwrite(STDOUT, __FILE__.' A21_FLOW_CANARY'); });",
        'shutdown_stderr': "register_shutdown_function(static function () { fwrite(STDERR, __FILE__.' A21_FLOW_CANARY'); });",
    }
    for label,body in fixtures.items():
        hostile.write_text("<?php if (getenv('A21_CONFINED') === '1') { "+body+' }')
        snapshot=b.fingerprint(db);fixture_files=b.files(site)
        out=OUT/(storage+'-hostile-'+label)
        try:
            bad=invoke(site,out,audit/'audit.json')
            expected='A21_SUCCESS_INCOMPLETE\n' if label=='forged_success' else 'A21_UNEXPECTED_OUTPUT\n'
            b.check(storage+':supervised_bootstrap:'+label,bad.returncode==1 and bad.stdout=='' and bad.stderr==expected)
            b.check(storage+':hostile_artifacts_absent:'+label,not out.exists() and not any(b'A21_FLOW_CANARY' in f.read_bytes() for f in OUT.rglob('*') if f.is_file()))
            b.check(storage+':hostile_confinement_unchanged:'+label,snapshot==b.fingerprint(db) and fixture_files==b.files(site))
        finally:
            hostile.unlink()
    # Actual unmodified neutraliser, on a cloned synthetic database only.
    clone='a21_'+storage+'_test'
    b.sql('mysql','CREATE DATABASE '+clone)
    for table in before['tables']:
        b.sql('mysql',f'CREATE TABLE {clone}.{table} LIKE {db}.{table}; INSERT INTO {clone}.{table} SELECT * FROM {db}.{table}')
    b.sql('mysql',"GRANT SELECT ON "+clone+".* TO 'a02_"+storage+"'@'localhost'")
    p=b.cmd(['php','/opt/a21/neutralise.php'],env={'A21_DB':clone})
    neutral=json.loads(p.stdout)
    b.check(storage+':real_neutraliser_observed',neutral=={'mark':True,'keys':0,'disabled_webhooks':4,'empty_destinations':4,'store_token_empty':True})
    (OUT/(storage+'-neutraliser.json')).write_text(json.dumps(neutral))
    (site/'wp-config.php').write_text(cfg.replace("define('DB_NAME', '"+db+"')","define('DB_NAME', '"+clone+"')"))
    neutral_before=b.fingerprint(clone);neutral_files=b.files(site)
    neutral_out=OUT/(storage+'-neutralised');np=invoke(site,neutral_out,audit/'audit.json')
    nd=json.loads((neutral_out/'portes.json').read_text())
    b.check(storage+':neutralised_unknown_not_zero',np.returncode==0 and nd['api_keys']=={'status':'inconnu après neutralisation','counts':None} and nd['webhooks']=={'status':'inconnu après neutralisation','counts':None} and nd['extension_store']=={'status':'inconnu après neutralisation','connected':None})
    b.check(storage+':neutralised_database_unchanged',neutral_before==b.fingerprint(clone))
    b.check(storage+':neutralised_files_unchanged',neutral_files==b.files(site))
    b.check(storage+':all_produced_artifacts_canary_absent',not any(b'CANARY' in f.read_bytes() for f in OUT.rglob('*') if f.is_file()))
b.run_storage=run_storage
if __name__=='__main__':
    sys.exit(b.main())
