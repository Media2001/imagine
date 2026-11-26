"""A17 fictitious accounts only, no login attempt, native classic and HPOS."""
import importlib.util,json,re,sys
from pathlib import Path
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('fixture','/opt/a02/inside.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
original=b.check
def check(name,ok,detail=None):
    if name.endswith(':commercial_fixture'):detail={k:detail[k] for k in ['versions','hpos','subscriptions','rules','restriction_real']}
    return original(name,ok,detail)
b.check=check
OUT=Path('/report')
def inventory(site,out,audit,env=None,*extra):
    return b.cmd(['python3','/subject/a17/confine.py','--wp-path='+str(site),'--output='+str(out),'--audit='+str(audit),'--as-of=2026-11-26T12:00:00Z',*extra],env=env,check=False)
def run_storage(storage):
    site,db,_=b.install(storage);(OUT/(storage+'-seed.json')).unlink();cfg=(site/'wp-config.php').read_text()
    config="\ndefine('DISALLOW_FILE_EDIT', false); define('DISALLOW_FILE_MODS', false);\n"
    cfg=cfg.replace("$table_prefix = 'wp_';",config+"$table_prefix = 'wp_';")
    writable=cfg.replace("define('DB_USER', 'a02_"+storage+"')","define('DB_USER', 'root')").split("\nfile_put_contents('/scratch/a02-bootstrap-trap'")[0]
    plugins={'two-factor/two-factor.php':'''<?php
/* Plugin Name: Two-Factor fixture
Version: 0.17.0 */
if (!getenv('A17_UNKNOWN_PROVIDER')) {
 class Two_Factor_Core {
 public static function is_user_using_two_factor($id) { return (bool) get_user_meta($id, '_a17_fixture_two_factor', true); }
 }
}
''','wp-last-login/wp-last-login.php':'''<?php
/* Plugin Name: WP Last Login fixture
Version: 1.3.0 */
''','limit-login-attempts-reloaded/limit-login-attempts-reloaded.php':'''<?php
/* Plugin Name: Limit Login Attempts Reloaded fixture
Version: 2.26.0 */
''','wordfence/wordfence.php':'''<?php
/* Plugin Name: Wordfence fixture inactive
Version: 8.0.0 */
throw new RuntimeException('NEVER_LOAD_INACTIVE');
'''}
    for relative,content in plugins.items():p=site/'wp-content/plugins'/relative;p.parent.mkdir();p.write_text(content)
    (site/'wp-config.php').write_text(writable)
    try:p=b.wp(site,['eval-file','/opt/a17/seed.php','--use-include']);b.check(storage+':seed_native_application_password','A17_SEED_OK' in p.stdout)
    finally:(site/'wp-config.php').write_text(cfg)
    mu=site/'wp-content/mu-plugins/a17-probe.php';mu.write_text('''<?php
if (getenv('A17_CONFINED') === '1') {
 global $wpdb; require_once ABSPATH.'wp-includes/pluggable.php';
 add_action('authenticate', function(){ throw new RuntimeException('A17_LOGIN_ATTEMPT_FORBIDDEN'); }, -99999);
 add_action('wp_login', function(){ throw new RuntimeException('A17_LOGIN_ATTEMPT_FORBIDDEN'); }, -99999);
 if ($wpdb->query('UPDATE wp_users SET ID=ID WHERE 1=0') !== false
 || @mysqli_query($wpdb->dbh,'UPDATE wp_users SET ID=ID WHERE 1=0') !== false
 || @file_put_contents(ABSPATH.'forbidden','NO') !== false
 || wp_mail('fictif@example.org','A17_PRIVATE_CANARY','A17_PRIVATE_CANARY') !== false
 || !is_wp_error(wp_remote_get('https://forbidden.invalid/'))
 || wp_schedule_single_event(time()+9999,'a17_forbidden') !== false
 || function_exists('mail') || function_exists('exec')) { throw new RuntimeException('A17_EARLY_GUARDS_FAILED'); }
 echo 'A17_BOOT_PRIVATE_CANARY';
}
''')
    audit=OUT/(storage+'-audit');b.check(storage+':a02_audit',b.audit(site,audit).returncode==0)
    before=b.fingerprint(db);files=b.files(site);(OUT/(storage+'-db-before.json')).write_text(json.dumps(before))
    dest=OUT/(storage+'-security');p=inventory(site,dest,audit/'audit.json');b.check(storage+':cli_and_actual_readonly_guards',p.returncode==0,{'exit':p.returncode,'stderr':p.stderr[:180]})
    d=json.loads((dest/'securite.json').read_text());rows={r['role']:r for r in d['roles']}
    expected={'administrator':2,'a17_gestion':1,'editor':3,'shop_manager':1,'a17_edit_users':1,'a17_update_plugins':1,'a17_switch_themes':1}
    b.check(storage+':exact_role_and_security_counts',{k:r['accounts'] for k,r in rows.items()}==expected and d['unique_management_accounts']==10 and rows['administrator']['application_password_accounts']==1 and rows['administrator']['last_login']=={'status':'observe','no_recent_record':1,'unknown_accounts':0} and all(rows[k]['last_login']['unknown_accounts']==1 for k in ['a17_gestion','shop_manager']))
    b.check(storage+':isolated_management_roles_included_content_excluded', all(rows['a17_'+cap]['accounts']==1 for cap in ['edit_users','update_plugins','switch_themes']) and 'a17_content_only' not in rows)
    b.check(storage+':exact_boundary_not_old_and_future_unknown',rows['editor']['last_login']=={'status':'observe','no_recent_record':0,'unknown_accounts':2})
    b.check(storage+':known_2fa_adapter',d['two_factor_adapter']=='Two_Factor_Core::is_user_using_two_factor' and rows['administrator']['two_factor_active']==1 and all(rows[k]['two_factor_active']==0 for k in ['a17_gestion','editor','shop_manager']))
    b.check(storage+':actual_configuration_not_runtime_forced_values',d['configuration']=={'public_registration':True,'default_role':'subscriber','admin_file_editing':True,'xmlrpc_authenticated_methods':True,'application_passwords_available':True})
    protections={r['name']:r for r in d['protections']};b.check(storage+':security_plugins_names_versions_active_inactive',protections['Wordfence fixture inactive']['active'] is False and protections['Two-Factor fixture']['version']=='0.17.0' and protections['Limit Login Attempts Reloaded fixture']['active'] is True)
    payload=''.join(x.read_text() for x in dest.iterdir())+p.stdout+p.stderr;b.check(storage+':no_identity_secret_in_outputs',not re.search(r'CANARY|@|/scratch|user_login|user_email|password_hash|user_pass|a02-admin|a17-fictif',payload))
    unknown=OUT/(storage+'-unknown');p=inventory(site,unknown,audit/'audit.json',{'A17_UNKNOWN_PROVIDER':'1'});u=json.loads((unknown/'securite.json').read_text());b.check(storage+':unknown_2fa_not_zero',p.returncode==0 and u['two_factor_adapter']=='inconnu' and all(r['two_factor_active'] is None for r in u['roles']))
    repeat=OUT/(storage+'-repeat');p=inventory(site,repeat,audit/'audit.json');b.check(storage+':replay_identical',p.returncode==0 and {x.name:x.read_bytes() for x in repeat.iterdir()}=={x.name:x.read_bytes() for x in dest.iterdir()})
    for label,path in [('exists',dest),('site',site/'forbidden'),('repo',Path('/subject/forbidden')),('ancestor',site.parent/'forbidden'),('root',Path('/forbidden'))]:
        p=inventory(site,path,audit/'audit.json');b.check(storage+':guard:'+label,p.returncode==1 and (path==dest or not path.exists()))
    raw=b.cmd(['php','/subject/a17/inventorier-securite','--wp-path='+str(site),'--output=/report/'+storage+'-raw','--audit='+str(audit/'audit.json')],check=False);b.check(storage+':unconfined_refused',raw.returncode==1 and raw.stderr=='A17_CONFINEMENT_REQUIRED\n')
    dropin=site/'wp-content/object-cache.php';dropin.write_text('<?php throw new RuntimeException("NEVER_RUN");')
    try:p=inventory(site,OUT/(storage+'-dropin'),audit/'audit.json');b.check(storage+':dropin_named_no_execution',p.returncode==1 and p.stderr=='A11_DROPIN_UNSUPPORTED {"file":"wp-content/object-cache.php"}\n')
    finally:dropin.unlink()
    after=b.fingerprint(db);(OUT/(storage+'-db-after.json')).write_text(json.dumps(after));b.check(storage+':all_tables_scheduler_identical',before==after);b.check(storage+':files_identical',files==b.files(site));b.check(storage+':config_not_executed',not Path('/scratch/a02-bootstrap-trap').exists())
    # A separate disposable copy crosses the unchanged real neutraliser and anonymiser.
    clone='a17_'+storage+'_test';b.sql('mysql','CREATE DATABASE '+clone)
    dump=b.cmd(['mariadb-dump','--socket='+b.SOCKET,'-uroot',db]).stdout
    b.cmd(['mariadb','--socket='+b.SOCKET,'-uroot',clone],data=dump)
    phase=b.cmd(['php','/opt/a17/neutralise.php'],env={'A17_DB':clone})
    provenance=json.loads(phase.stdout);(OUT/(storage+'-neutralisation.json')).write_text(json.dumps(provenance,indent=2)+'\n')
    b.check(storage+':real_neutralisation_erases_application_passwords',provenance=={'application_password_rows_before':1,'application_password_rows_after':0,'neutralisation_marker_count':1,'neutraliser_and_anonymiser_executed':True})
    b.sql('mysql',"GRANT SELECT ON "+clone+".* TO 'a02_"+storage+"'@'localhost'")
    original_cfg=(site/'wp-config.php').read_text();(site/'wp-config.php').write_text(original_cfg.replace("define('DB_NAME', '"+db+"')","define('DB_NAME', '"+clone+"')"))
    try:
        clone_before=b.fingerprint(clone);clone_files=b.files(site)
        neutral_audit=OUT/(storage+'-neutralised-audit');b.check(storage+':neutralised_audit',b.audit(site,neutral_audit).returncode==0)
        neutral=OUT/(storage+'-neutralised');p=inventory(site,neutral,neutral_audit/'audit.json')
        n=json.loads((neutral/'securite.json').read_text())
        b.check(storage+':neutralised_application_passwords_unknown_never_zero',p.returncode==0 and all(r['application_password_accounts']=='inconnu après neutralisation' for r in n['roles']))
        clone_after=b.fingerprint(clone)
        (OUT/(storage+'-neutralised-db-before.json')).write_text(json.dumps(clone_before));(OUT/(storage+'-neutralised-db-after.json')).write_text(json.dumps(clone_after))
        b.check(storage+':neutralised_all_tables_and_files_readonly',clone_before==clone_after and clone_files==b.files(site))
    finally:(site/'wp-config.php').write_text(original_cfg)
b.run_storage=run_storage
if __name__=='__main__':sys.exit(b.main())
