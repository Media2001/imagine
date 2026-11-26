"""A14 actual classic/HPOS, no real contacts or sites."""
import csv
import importlib.util
import io
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
    return b.cmd(['python3','/checkout/wp/outils/bascule/rapprocher-contacts','--wp-path='+str(site),'--output='+str(out),'--audit='+str(audit),'--contacts=/opt/a14/contacts.csv','--correspondance=/checkout/wp/outils/bascule/a14/correspondance.exemple.json',*extra],check=False)

def storage_run(storage):
    site,db,_=b.install(storage);(OUT/(storage+'-seed.json')).unlink()
    cfg=(site/'wp-config.php').read_text()
    (site/'wp-config.php').write_text(cfg.replace("define('DB_USER', 'a02_"+storage+"')","define('DB_USER', 'root')").split("\nfile_put_contents('/scratch/a02-bootstrap-trap'")[0])
    try:
        p=b.wp(site,['eval-file','/opt/a14/seed.php','--use-include'])
        oracle=json.loads(next(x[9:] for x in p.stdout.splitlines() if x.startswith('A14_JSON=')))
    finally:(site/'wp-config.php').write_text(cfg)
    (OUT/(storage+'-oracle.json')).write_text(json.dumps(oracle,indent=2)+'\n')
    b.check(storage+':native_oracle',oracle=={'active':{'alice':True,'bob':False,'carol':False},'accounts':14,'hpos':storage=='hpos'})
    mu=site/'wp-content/mu-plugins/a14-guards.php'
    mu.write_text('''<?php
if (getenv('A14_CONFINED') === '1') {
    global $wpdb;
    require_once ABSPATH . 'wp-includes/pluggable.php';
    $checks = [
        !did_action('plugins_loaded'),
        $wpdb->query('UPDATE wp_posts SET ID=ID WHERE 1=0') === false,
        @mysqli_query($wpdb->dbh, 'UPDATE wp_posts SET ID=ID WHERE 1=0') === false,
        @file_put_contents(ABSPATH . 'forbidden', 'NO') === false,
        @file_put_contents(ABSPATH . 'index.php', 'NO') === false,
        wp_mail('a14-mail-canary@example.org', 'A14_PRIVATE_CANARY', 'A14_PRIVATE_CANARY') === false,
        is_wp_error(wp_remote_get('https://forbidden.invalid/')),
        wp_schedule_single_event(time()+9999, 'a14_forbidden') === false,
        !function_exists('mail'), !function_exists('exec'),
    ];
    if (in_array(false, $checks, true)) { throw new RuntimeException('A14_GUARDS_FAILED'); }
    echo 'A14_BOOT_PRIVATE_CANARY';
}
''')
    audit=OUT/(storage+'-audit');b.check(storage+':a02_audit',b.audit(site,audit).returncode==0)
    before=b.fingerprint(db);files=b.files(site)
    (OUT/(storage+'-db-before.json')).write_text(json.dumps(before,indent=2)+'\n')
    dest=OUT/(storage+'-contacts');p=inventory(site,dest,audit/'audit.json')
    b.check(storage+':cli_success_and_all_early_guards',p.returncode==0,{'exit':p.returncode,'stderr':p.stderr[:180]})
    data=json.loads((dest/'resume.json').read_text())
    expected={'contacts_total':30,'contacts_with_account':4,'contacts_without_account':23,'ambiguous_contact_lines':1,'accounts_without_contact':7,'accounts_unmatchable':1,'invalid_contact_lines':2,'duplicate_contact_lines':2,'unsubscribed_contacts':1,'blocked_contacts':1}
    b.check(storage+':exact_counts',data['counts']==expected, data['counts'])
    b.check(storage+':every_anomaly_correct_line',data['anomalies']==[
        {'line':2,'reason':'Doublon dans le fichier'},{'line':3,'reason':'Doublon dans le fichier'},
        {'line':7,'reason':'Adresse électronique invalide'},{'line':8,'reason':'Adresse électronique invalide'},
        {'line':11,'reason':'Plusieurs comptes pour cette adresse'}])
    rows=list(csv.DictReader(io.StringIO((dest/'rapproches.csv').read_text()),delimiter=';'))
    b.check(storage+':exact_rows_status_native_oracle_unknown_empty',rows==[
        {'ligne':'2','abonnement_actif':'oui','statut':'inscrit','cooperateur':'','tarif':''},
        {'ligne':'3','abonnement_actif':'oui','statut':'desinscrit','cooperateur':'','tarif':''},
        {'ligne':'4','abonnement_actif':'non','statut':'bloque','cooperateur':'','tarif':''},
        {'ligne':'5','abonnement_actif':'non','statut':'inscrit','cooperateur':'','tarif':''}])
    payload=''.join(x.read_text() for x in dest.iterdir())+p.stdout+p.stderr
    b.check(storage+':no_emails_names_ids_private_values',not re.search(r'@|Fictif|PRIVATE_CANARY|DB_PASSWORD|/scratch',payload))
    b.check(storage+':permissions',dest.stat().st_mode&0o777==0o700 and all(x.stat().st_mode&0o777==0o600 for x in dest.iterdir()))
    repeat=OUT/(storage+'-repeat');q=inventory(site,repeat,audit/'audit.json')
    b.check(storage+':replay_identical',q.returncode==0 and {x.name:x.read_bytes() for x in repeat.iterdir()}=={x.name:x.read_bytes() for x in dest.iterdir()})
    for label,path,extra in [('exists',dest,[]),('site',site/'forbidden',[]),('source',Path('/checkout/wp/outils/bascule/forbidden'),[]),('ancestor',site.parent/'forbidden',[]),('root',Path('/forbidden'),[]),('argument',OUT/(storage+'-arg'),['--unknown=yes'])]:
        bad=inventory(site,path,audit/'audit.json',*extra)
        b.check(storage+':guard:'+label,bad.returncode==1 and (path==dest or not path.exists()))
    bad=b.cmd(['php','/checkout/wp/outils/bascule/a14/command.php','--wp-path='+str(site),'--output=/report/'+storage+'-raw','--audit='+str(audit/'audit.json')],check=False)
    b.check(storage+':unconfined_refused',bad.returncode==1 and bad.stderr=='A14_CONFINEMENT_REQUIRED\n')
    dropin=site/'wp-content/object-cache.php';dropin.write_text('<?php throw new RuntimeException("NEVER_RUN");')
    try:
        bad=inventory(site,OUT/(storage+'-dropin'),audit/'audit.json')
        b.check(storage+':dropin_named_no_execution',bad.returncode==1 and bad.stderr=='A11_DROPIN_UNSUPPORTED {"file":"wp-content/object-cache.php"}\n')
    finally:dropin.unlink()
    after=b.fingerprint(db);(OUT/(storage+'-db-after.json')).write_text(json.dumps(after,indent=2)+'\n')
    b.check(storage+':all_tables_scheduler_identical',before==after,{'tables':len(before['tables']),'before':before['logical_sha256'],'after':after['logical_sha256']})
    b.check(storage+':files_identical',files==b.files(site),{'before':files,'after':b.files(site)})
    b.check(storage+':config_not_executed',not Path('/scratch/a02-bootstrap-trap').exists())

b.run_storage=storage_run
if __name__=='__main__':
    for p in [*Path('/checkout/wp/outils/bascule/a14').glob('*.php'),*Path('/opt/a14').glob('*.php')]:
        b.check('lint:'+p.name,b.cmd(['php','-l',str(p)],check=False).returncode==0)
    sys.exit(b.main())
