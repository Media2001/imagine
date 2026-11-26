"""Actual native WC_Emails/WCS/Memberships; classic and HPOS."""
import importlib.util
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('fixture','/opt/a02/inside.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
original=b.check

def check(name,ok,detail=None):
    if name.endswith(':commercial_fixture'):detail={k:detail[k] for k in ['versions','hpos','subscriptions','rules','restriction_real']}
    return original(name,ok,detail)
b.check=check
OUT=Path('/report')

def inventory(site,out,audit,*extra):
    return b.cmd(['python3','/subject/a15/confine.py','--wp-path='+str(site),'--output='+str(out),'--audit='+str(audit),*extra],check=False)

def run_storage(storage):
    site,db,_=b.install(storage);(OUT/(storage+'-seed.json')).unlink()
    cfg=(site/'wp-config.php').read_text()
    writable=cfg.replace("define('DB_USER', 'a02_"+storage+"')","define('DB_USER', 'root')").split("\nfile_put_contents('/scratch/a02-bootstrap-trap'")[0]
    active=site/'wp-content/plugins/a15-smtp';active.mkdir()
    (active/'a15-smtp.php').write_text('''<?php
/* Plugin Name: A15 SMTP fictif
Version: 1.2.3 */
add_action('phpmailer_init', function ($mailer) { throw new RuntimeException('A15_MAIL_ESCAPED_GUARD'); });
''')
    inactive=site/'wp-content/plugins/a15-smtp-inactive';inactive.mkdir()
    (inactive/'a15-smtp-inactive.php').write_text('''<?php
/* Plugin Name: A15 SMTP inactif fictif
Version: 4.5.6 */
throw new RuntimeException('A15_NEVER_LOAD_INACTIVE');
''')
    theme=site/'wp-content/themes/a02-child/woocommerce/emails';theme.mkdir()
    (theme/'customer-on-hold-order.php').write_text("<?php throw new RuntimeException('A15_NEVER_RENDER_PRIVATE_CANARY');")
    (site/'wp-config.php').write_text(writable)
    try:
        p=b.wp(site,['eval-file','/opt/a15/seed.php','--use-include']);b.check(storage+':fixture_seed', 'A15_SEED_OK' in p.stdout)
        p=b.wp(site,['eval-file','/opt/a15/oracle.php','--use-include'])
        oracle=json.loads(next(x[9:] for x in p.stdout.splitlines() if x.startswith('A15_JSON=')))
    finally:(site/'wp-config.php').write_text(cfg)
    (OUT/(storage+'-oracle.json')).write_text(json.dumps(oracle,indent=2)+'\n')
    b.check(storage+':oracle_commercial_registry_and_storage',set(oracle['summary'])=={'plugin:woocommerce','plugin:woocommerce-subscriptions','plugin:woocommerce-memberships'} and oracle['hpos']==(storage=='hpos'))
    mu=site/'wp-content/mu-plugins/a15-probes.php'
    mu.write_text('''<?php
if (getenv('A15_CONFINED') === '1') {
    global $wpdb;
    require_once ABSPATH . 'wp-includes/pluggable.php';
    $checks = [
        !did_action('plugins_loaded'),
        $wpdb->query('UPDATE wp_posts SET ID=ID WHERE 1=0') === false,
        @mysqli_query($wpdb->dbh, 'UPDATE wp_posts SET ID=ID WHERE 1=0') === false,
        @file_put_contents(ABSPATH . 'forbidden', 'NO') === false,
        @file_put_contents(ABSPATH . 'index.php', 'NO') === false,
        wp_mail('a15-mail-canary@example.org', 'A15_PRIVATE_CANARY', 'A15_PRIVATE_CANARY') === false,
        is_wp_error(wp_remote_get('https://forbidden.invalid/')),
        wp_schedule_single_event(time()+9999, 'a15_forbidden') === false,
        !function_exists('mail'), !function_exists('exec'),
    ];
    if (in_array(false, $checks, true)) { throw new RuntimeException('A15_EARLY_GUARDS_FAILED'); }
    add_action('wp_loaded', function () {
        $emails = WC()->mailer()->get_emails();
        $email = reset($emails);
        if ($email->send('a15-woo-send-canary@example.org', 'A15_SEND_PRIVATE_CANARY', 'A15_SEND_PRIVATE_CANARY', '', []) !== false) {
            throw new RuntimeException('A15_WOO_SEND_NOT_BLOCKED');
        }
        echo 'A15_BOOT_PRIVATE_CANARY';
    }, PHP_INT_MAX);
}
''')
    audit=OUT/(storage+'-audit');b.check(storage+':a02_audit',b.audit(site,audit).returncode==0)
    before=b.fingerprint(db);files=b.files(site);(OUT/(storage+'-db-before.json')).write_text(json.dumps(before,indent=2)+'\n')
    dest=OUT/(storage+'-emails');p=inventory(site,dest,audit/'audit.json')
    b.check(storage+':cli_and_actual_mail_sql_file_http_cron_guards',p.returncode==0,{'exit':p.returncode,'stderr':p.stderr[:180]})
    data=json.loads((dest/'emails.json').read_text());rows={r['id']:r for r in data['emails']}
    b.check(storage+':exact_native_registry',data['registry']=={'native_loaded':True,'email_count':oracle['count']} and [{k:r[k] for k in ['id','extension','enabled']} for r in data['emails']]==oracle['emails'])
    b.check(storage+':exact_active_counts_by_extension',data['summary']['active_by_extension']==oracle['summary'])
    row=rows['customer_on_hold_order']
    b.check(storage+':disabled_subject_body_client',row['enabled'] is False and row['subject_customised'] is True and row['content_customised'] is True and row['recipient_nature']=='client')
    b.check(storage+':exact_theme_override',row['template_overrides']==['wp-content/themes/a02-child/woocommerce/emails/customer-on-hold-order.php'] and row['template_overridden'] is True and data['summary']['overridden_template_files']==1)
    b.check(storage+':internal_custom_recipient_without_address',rows['new_order']['recipient_nature']=='administration' and rows['new_order']['recipient_customised'] is True)
    senders={r['name']:r for r in data['transport_plugins']}
    b.check(storage+':present_active_and_inactive_transport_versions',senders['A15 SMTP fictif']=={'name':'A15 SMTP fictif','version':'1.2.3','active':True,'runtime_mail_hook':True} and senders['A15 SMTP inactif fictif']=={'name':'A15 SMTP inactif fictif','version':'4.5.6','active':False,'runtime_mail_hook':False})
    b.check(storage+':memberships_plan_body_customisation',rows['WC_Memberships_User_Membership_Activated_Email']['content_customised'] is True)
    b.check(storage+':native_formatter_not_transport','WooCommerce' not in senders)
    payload=''.join(x.read_text() for x in dest.iterdir())+p.stdout+p.stderr
    b.check(storage+':no_address_subject_body_canary_secret_path',not re.search(r'@|PRIVATE_CANARY|DB_PASSWORD|/scratch|a15-recipient-canary',payload))
    b.check(storage+':output_only_allowlisted_schema',set(data)=={'schema','read_only','storage','registry','emails','transport_plugins','summary','audit_sha256'} and all(set(r)=={'id','title','extension','enabled','recipient_nature','recipient_customised','subject_customised','content_customised','template_overrides','template_overridden'} for r in rows.values()))
    b.check(storage+':permissions',dest.stat().st_mode&0o777==0o700 and all(x.stat().st_mode&0o777==0o600 for x in dest.iterdir()))
    repeat=OUT/(storage+'-repeat');q=inventory(site,repeat,audit/'audit.json')
    b.check(storage+':replay_identical',q.returncode==0 and {x.name:x.read_bytes() for x in repeat.iterdir()}=={x.name:x.read_bytes() for x in dest.iterdir()})
    (site/'wp-config.php').write_text(cfg.replace("define('DB_USER', 'a02_"+storage+"')","define('DB_USER', 'root')"))
    try:
        root_out=OUT/(storage+'-root-credential')
        root_run=inventory(site,root_out,audit/'audit.json')
        b.check(storage+':transaction_blocks_even_privileged_root',root_run.returncode==0 and json.loads((root_out/'emails.json').read_text())==data)
    finally:(site/'wp-config.php').write_text(cfg)
    import shutil
    canonical=Path('/checkout/wp/outils/bascule')
    if not canonical.exists():canonical.parent.mkdir(parents=True);shutil.copytree('/subject',canonical)
    bad=b.cmd(['python3',str(canonical/'a15/confine.py'),'--wp-path='+str(site),'--output=/checkout/forbidden','--audit='+str(audit/'audit.json')],check=False)
    b.check(storage+':canonical_repository_output_refused',bad.returncode==1 and bad.stderr=='A15_OUTPUT_UNSAFE\n' and not Path('/checkout/forbidden').exists())
    for label,path,extra in [('exists',dest,[]),('site',site/'forbidden',[]),('source',Path('/subject/forbidden'),[]),('ancestor',site.parent/'forbidden',[]),('root',Path('/forbidden'),[]),('argument',OUT/(storage+'-arg'),['--unknown=yes'])]:
        bad=inventory(site,path,audit/'audit.json',*extra);b.check(storage+':guard:'+label,bad.returncode==1 and (path==dest or not path.exists()))
    raw=b.cmd(['php','/subject/a15/inventorier-emails','--wp-path='+str(site),'--output=/report/'+storage+'-raw','--audit='+str(audit/'audit.json')],check=False)
    b.check(storage+':unconfined_refused',raw.returncode==1 and raw.stderr=='A15_CONFINEMENT_REQUIRED\n')
    wrong=OUT/(storage+'-wrong-audit');wrong.mkdir();photo=json.loads((audit/'audit.json').read_text());photo['sections']['commerce']['order_storage']='hpos' if storage=='classic' else 'classic';(wrong/'audit.json').write_text(json.dumps(photo))
    bad=inventory(site,OUT/(storage+'-badstorage'),wrong/'audit.json');b.check(storage+':storage_mismatch_refused',bad.returncode==1 and bad.stderr=='A15_AUDIT_STORAGE_MISMATCH\n')
    dropin=site/'wp-content/object-cache.php';dropin.write_text('<?php throw new RuntimeException("NEVER_RUN");')
    try:
        bad=inventory(site,OUT/(storage+'-dropin'),audit/'audit.json');b.check(storage+':dropin_named_no_execution',bad.returncode==1 and bad.stderr=='A11_DROPIN_UNSUPPORTED {"file":"wp-content/object-cache.php"}\n')
    finally:dropin.unlink()
    after=b.fingerprint(db);(OUT/(storage+'-db-after.json')).write_text(json.dumps(after,indent=2)+'\n')
    b.check(storage+':all_tables_scheduler_identical',before==after,{'tables':len(before['tables']),'before':before['logical_sha256'],'after':after['logical_sha256']})
    b.check(storage+':files_identical',files==b.files(site),{'before':files,'after':b.files(site)})
    b.check(storage+':config_not_executed',not Path('/scratch/a02-bootstrap-trap').exists())

b.run_storage=run_storage
if __name__=='__main__':
    for p in [*Path('/subject/a15').glob('*.php'),*Path('/opt/a15').glob('*.php'),Path('/subject/a15/inventorier-emails')]:b.check('a15_lint:'+p.name,b.cmd(['php','-l',str(p)],check=False).returncode==0)
    sys.exit(b.main())
