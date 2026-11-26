"""A19 real native stores and explicit-link oracle; synthetic and disconnected."""
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
def inventory(site,out,audit,*extra):
    return b.cmd(['python3','/subject/a19/confine.py','--wp-path='+str(site),'--output='+str(out),'--audit='+str(audit),'--as-of=2026-11-26T00:00:00Z',*extra],check=False)
def run_storage(storage):
    site,db,_=b.install(storage);(OUT/(storage+'-seed.json')).unlink()
    cfg=(site/'wp-config.php').read_text();writable=cfg.replace("define('DB_USER', 'a02_"+storage+"')","define('DB_USER', 'root')").split("\nfile_put_contents('/scratch/a02-bootstrap-trap'")[0]
    (site/'wp-config.php').write_text(writable)
    try:
        p=b.wp(site,['eval-file','/opt/a19/seed.php','--use-include']);oracle=json.loads(next(x[9:] for x in p.stdout.splitlines() if x.startswith('A19_JSON=')))
    finally:(site/'wp-config.php').write_text(cfg)
    (OUT/(storage+'-oracle.json')).write_text(json.dumps(oracle))
    b.check(storage+':native_fixture_relationships',oracle['subscriptions_native']==4 and all(oracle[k] for k in ['past_next_native','coherent_link_native','stale_native_absent','paid_parent_native','paid_renewal_native','renewal_native_link']))
    mu=site/'wp-content/mu-plugins/a19-runtime.php';mu.write_text('''<?php
add_filter('woocommerce_subscription_payment_meta', static function ($meta, $sub) {
 if (get_option('a19_fixture_schema_enabled') === 'yes') {
  $meta['a19_fixture'] = ['post_meta'=>['_a19_payment_reference'=>['value'=>$sub->get_meta('_a19_payment_reference'),'label'=>'Reference']]];
 }
 return $meta;
}, 10, 2);
if (getenv('A19_CONFINED') === '1' && ($forced = get_option('a19_forced_exception', '')) !== '') {
 throw new RuntimeException($forced);
}
if (getenv('A19_CONFINED') === '1') {
 global $wpdb; require_once ABSPATH.'wp-includes/pluggable.php';
 if ($wpdb->query('UPDATE wp_posts SET ID=ID WHERE 1=0') !== false
 || @mysqli_query($wpdb->dbh,'UPDATE wp_posts SET ID=ID WHERE 1=0') !== false
 || @file_put_contents(ABSPATH.'forbidden','NO') !== false
 || wp_mail('fictif@example.org','A19_PRIVATE_CANARY','A19_PRIVATE_CANARY') !== false
 || !is_wp_error(wp_remote_get('https://forbidden.invalid/'))
 || wp_schedule_single_event(time()+9999,'a19_forbidden') !== false
 || function_exists('mail') || function_exists('exec')) { throw new RuntimeException('A19_EARLY_GUARDS_FAILED'); }
 echo 'A19_BOOT_PRIVATE_CANARY';
}
''')
    audit=OUT/(storage+'-audit');b.check(storage+':a02_audit',b.audit(site,audit).returncode==0)
    before=b.fingerprint(db);files=b.files(site);(OUT/(storage+'-db-before.json')).write_text(json.dumps(before))
    dest=OUT/(storage+'-coherence');p=inventory(site,dest,audit/'audit.json')
    b.check(storage+':cli_and_actual_readonly_guards',p.returncode==0,{'exit':p.returncode,'stderr':p.stderr[:120]})
    d=json.loads((dest/'coherence.json').read_text());v=d['counts'];plan=oracle['plan']
    expected={
        'cross':[{'plan':plan,'subscription_status':'active','membership_status':'active','count':1}],
        'subscriptions_without_membership':[{'status':'active','count':2},{'status':'on-hold','count':1}],
        'memberships_without_subscription':[{'plan':plan,'status':'active','count':2}],
        'memberships_missing_subscription':[{'plan':plan,'status':'active','count':1}],
        'multiple_active_subscription_accounts':1,'multiple_active_membership_accounts':1,
        'multiple_active_membership_accounts_by_plan':[{'plan':plan,'count':1}],
        'automatic_without_saved_payment':[{'gateway':'a19_fixture','count':1}],
        'automatic_payment_reference_unknown':[], 'active_past_next_payment':1,'active_without_paid_order':1,
        'manual_by_gateway':[{'gateway':'bacs','count':1},{'gateway':'cheque','count':1}]}
    for key,want in expected.items():b.check(storage+':exact_count:'+key,v.get(key)==want,{'actual':v.get(key),'expected':want})
    b.check(storage+':all_counts_explained',set(v['definitions'])==set(expected) and all(isinstance(x,str) and x for x in v['definitions'].values()))
    payload=p.stdout+p.stderr+''.join(x.read_text() for x in dest.iterdir())
    b.check(storage+':no_account_subscription_order_identifiers_names_paths',not re.search(r'CANARY|@|/scratch|DB_PASSWORD|"(?:user|customer|subscription_id|order_id|id)"',payload))
    b.check(storage+':private_output_permissions',dest.stat().st_mode&0o777==0o700 and all(x.stat().st_mode&0o777==0o600 for x in dest.iterdir()))
    repeat=OUT/(storage+'-repeat');p=inventory(site,repeat,audit/'audit.json');b.check(storage+':replay_identical',p.returncode==0 and {x.name:x.read_bytes() for x in repeat.iterdir()}=={x.name:x.read_bytes() for x in dest.iterdir()})
    for label,path in [('exists',dest),('site',site/'forbidden'),('repo',Path('/subject/forbidden')),('ancestor',site.parent/'forbidden'),('root',Path('/forbidden'))]:
        bad=inventory(site,path,audit/'audit.json');b.check(storage+':guard:'+label,bad.returncode==1 and (path==dest or not path.exists()))
    raw=b.cmd(['php','/subject/a19/inventorier-coherence','--wp-path='+str(site),'--output=/report/'+storage+'-raw','--audit='+str(audit/'audit.json')],check=False)
    b.check(storage+':unconfined_refused',raw.returncode==1 and raw.stderr=='A19_CONFINEMENT_REQUIRED\n')
    for directory in [False,True]:
        link=site/('A19_PERSONAL_SYMLINK_CANARY'+str(directory));link.symlink_to(site/'wp-content' if directory else site/'wp-config.php',target_is_directory=directory)
        try:
            out=OUT/(storage+'-symlink-'+str(directory));bad=inventory(site,out,audit/'audit.json')
            b.check(storage+':symlink_private_code_only:'+str(directory),bad.returncode==1 and bad.stdout=='' and bad.stderr=='A11_SYMLINK_UNSUPPORTED\n' and not out.exists())
        finally:link.unlink()
    for index,name in enumerate(['wp-content/db.php','wp-content/object-cache.php','wp-content/advanced-cache.php','wp-content/sunrise.php','wordfence-waf.php','.user.ini']):
        f=site/name;f.write_text('<?php throw new RuntimeException("A19_PRIVATE_CANARY");')
        try:
            out=OUT/(storage+'-dropin-'+str(index));bad=inventory(site,out,audit/'audit.json')
            b.check(storage+':closed_dropin:'+str(index),bad.returncode==1 and bad.stdout=='' and bad.stderr=='A11_DROPIN_UNSUPPORTED '+json.dumps({'file':name},separators=(',',':'))+'\n' and not out.exists())
        finally:f.unlink()
    for label,statement in [('define',"define('A19_CONFIG_PRIVATE_CANARY', 'A19_VALUE_PRIVATE_CANARY');"),('const',"const A19_CONFIG_PRIVATE_CANARY = 'A19_VALUE_PRIVATE_CANARY';")]:
        (site/'wp-config.php').write_text(cfg+'\n'+statement+'\n')
        try:
            out=OUT/(storage+'-config-'+label);bad=inventory(site,out,audit/'audit.json')
            b.check(storage+':config_private_code_only:'+label,bad.returncode==1 and bad.stdout=='' and bad.stderr=='A11_CONFIG_OVERRIDE_UNSUPPORTED\n' and not out.exists())
        finally:(site/'wp-config.php').write_text(cfg)
    clockout=OUT/(storage+'-clock')
    bad=b.cmd(['python3','/subject/a19/confine.py','--wp-path='+str(site),'--output='+str(clockout),'--audit='+str(audit/'audit.json'),'--as-of=2026-02-30T00:00:00Z'],check=False)
    b.check(storage+':invalid_clock_code_only',bad.returncode==1 and bad.stdout=='' and bad.stderr=='A19_CLOCK_INVALID\n' and not clockout.exists())
    after=b.fingerprint(db);(OUT/(storage+'-db-after.json')).write_text(json.dumps(after));b.check(storage+':all_tables_scheduler_identical',before==after);b.check(storage+':files_identical',files==b.files(site));b.check(storage+':config_not_executed',not Path('/scratch/a02-bootstrap-trap').exists())
    b.sql(db,"UPDATE wp_options SET option_value='no' WHERE option_name='a19_fixture_schema_enabled'")
    variant_before=b.fingerprint(db);variant_out=OUT/(storage+'-unknown');p=inventory(site,variant_out,audit/'audit.json');vd=json.loads((variant_out/'coherence.json').read_text())
    b.check(storage+':unknown_reference_not_counted_absent',p.returncode==0 and vd['counts']['automatic_without_saved_payment']==[] and vd['counts']['automatic_payment_reference_unknown']==[{'gateway':'a19_fixture','count':1}])
    b.check(storage+':unknown_variant_database_unchanged',variant_before==b.fingerprint(db))
    b.sql(db,"INSERT INTO wp_options (option_name,option_value,autoload) VALUES ('a19_forced_exception','A19_PLUGIN_PRIVATE_CANARY','no')")
    refusal_before=b.fingerprint(db);refusal_out=OUT/(storage+'-plugin-exception');bad=inventory(site,refusal_out,audit/'audit.json')
    b.check(storage+':plugin_exception_code_closed',bad.returncode==1 and bad.stdout=='' and bad.stderr=='A19_INVENTORY_FAILED\n' and not refusal_out.exists())
    b.check(storage+':plugin_exception_variant_database_unchanged',refusal_before==b.fingerprint(db))
    b.check(storage+':all_produced_artifacts_canary_absent',not any(b'CANARY' in f.read_bytes() for f in OUT.rglob('*') if f.is_file()))
b.run_storage=run_storage
if __name__=='__main__':sys.exit(b.main())
