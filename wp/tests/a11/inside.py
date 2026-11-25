"""A11 native URLs and immutable all-table fingerprints on the A02 fixture."""
import csv
import importlib.util
import json
import pathlib
import re
import sys
sys.dont_write_bytecode = True
spec=importlib.util.spec_from_file_location('a02','/opt/a02/inside.py')
b=importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
OUT=pathlib.Path('/report')
original_check=b.check

def safe_check(name,ok,detail=None):
    if name.endswith(':commercial_fixture'):
        detail={k:detail[k] for k in ['versions','hpos','subscriptions','rules','restriction_real']}
    return original_check(name,ok,detail)
b.check=safe_check

PLUGIN='''<?php
/* Plugin Name: A11 synthetic native registrations */
add_action('init', static function () {
    register_post_type('a11_story', ['public'=>true, 'has_archive'=>'histoires', 'rewrite'=>['slug'=>'histoires'], 'supports'=>['title','author']]);
    register_taxonomy('a11_topic','a11_story',['public'=>true,'rewrite'=>['slug'=>'sujets']]);
});
add_filter('post_type_link', static function ($url,$post) { return $post->post_type === 'a11_story' ? add_query_arg('edition','a%2fb+z',$url) : $url; },10,2);
'''

def inventory(site,target,audit,*args):
    return b.cmd(['php','/subject/a11/inventorier-adresses','--wp-path='+str(site),'--output='+str(target),'--audit='+str(audit),*args],check=False)

def run_storage(storage):
    site,db,_=b.install(storage)
    (OUT/(storage+'-seed.json')).unlink()
    config=(site/'wp-config.php').read_text()
    writable=config.replace("define('DB_USER', 'a02_"+storage+"')", "define('DB_USER', 'root')").split("\nfile_put_contents('/scratch/a02-bootstrap-trap'")[0]
    (site/'wp-content/mu-plugins/a11-fixture.php').write_text(PLUGIN)
    (site/'wp-config.php').write_text(writable)
    seed=b.wp(site,['eval-file','/opt/a11/seed.php','--use-include'],env={'A11_VARIANT':'seed'},check=False)
    if seed.returncode:
        (OUT/(storage+'-seed-error.log')).write_text(seed.stdout+seed.stderr)
        raise RuntimeError('NATIVE_SEED_FAILED')
    (site/'wp-config.php').write_text(config)
    b.check(storage+':command_exists',pathlib.Path('/subject/a11/inventorier-adresses').is_file())
    for variant in ['pretty','plain','subdir','attachments-disabled']:
        key=storage+':'+variant
        (site/'wp-config.php').write_text(writable)
        try:
            b.wp(site,['eval-file','/opt/a11/seed.php','--use-include'],env={'A11_VARIANT':variant})
            oracle=b.wp(site,['eval-file','/opt/a11/oracle.php','--use-include'])
            data=json.loads(next(x[9:] for x in oracle.stdout.splitlines() if x.startswith('A11_JSON=')))
        finally:
            (site/'wp-config.php').write_text(config)
        stem=storage+'-'+variant
        (OUT/(stem+'-oracle.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
        auditdir=OUT/(stem+'-audit')
        photo=b.audit(site,auditdir)
        b.check(key+':audit',photo.returncode==0)
        before=b.fingerprint(db); fb=b.files(site)
        (OUT/(stem+'-before.json')).write_text(json.dumps(before,indent=2)+'\n')
        target=OUT/(stem+'-addresses')
        p=inventory(site,target,auditdir/'audit.json')
        (OUT/(stem+'-command.log')).write_text(p.stdout+p.stderr)
        b.check(key+':cli',p.returncode==0,{'exit_code':p.returncode})
        report=json.loads((target/'adresses.json').read_text())
        actual={row['ancienne']:[[c['nature'],c['type_contenu']] for c in row['contextes']] for row in report['adresses']}
        b.check(key+':exact_native_urls_and_natures',actual==data['expected'],{'expected':len(data['expected']),'actual':len(actual)})
        b.check(key+':excluded_exact',report['exclus']==data['excluded'],report['exclus'])
        b.check(key+':author_slug_only',sum(any(c['nature']=="archive d'auteur" for c in row['contextes']) for row in report['adresses'])==1)
        with open(target/'adresses.csv',encoding='utf-8-sig',newline='') as f:
            rows=list(csv.DictReader(f,delimiter=';'))
        b.check(key+':spreadsheet_exact',len(rows)==len(actual) and {r['ancienne'] for r in rows}==set(actual))
        b.check(key+':unique_sorted',list(actual)==sorted(actual) and report['total']==len(actual))
        b.check(key+':publication_and_dates',all(r['etat_publication'] in ['publish','inherit','public'] and (r['derniere_modification_utc'] is None or re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ',r['derniere_modification_utc'])) for r in report['adresses']))
        body=''.join(f.read_text() for f in target.iterdir())+p.stdout+p.stderr
        b.check(key+':no_private_fields',not re.search(r'PRIVATE_|@|user_email|display_name|billing_|customer_id|post_content|post_title|post_password',body))
        b.check(key+':output_permissions',target.stat().st_mode&0o777==0o700 and all(f.stat().st_mode&0o777==0o600 for f in target.iterdir()))
        b.check(key+':no_http_mail_scheduling',report['native_guards']['http']==0 and report['native_guards']['mail']==0 and report['native_guards']['scheduled']==0,report['native_guards'])
        again=OUT/(stem+'-repeat')
        repeat=inventory(site,again,auditdir/'audit.json')
        b.check(key+':repeat',repeat.returncode==0 and json.loads((again/'adresses.json').read_text())==report)
        for suffix,dest,extra in [('web',site/'forbidden',[]),('source',pathlib.Path('/subject/forbidden'),[]),('exists',target,[]),('unknown',OUT/(stem+'-unknown'),['--oops=yes'])]:
            bad=inventory(site,dest,auditdir/'audit.json',*extra)
            b.check(key+':refuse:'+suffix,bad.returncode==1 and (dest==target or not dest.exists()))
        link=OUT/(stem+'-web-link'); link.symlink_to(site,target_is_directory=True)
        bad=inventory(site,link/'forbidden',auditdir/'audit.json')
        b.check(key+':symlink_web',bad.returncode==1 and not (site/'forbidden').exists()); link.unlink()
        # The subject's DB fence is also enforced with privileged synthetic credentials.
        (site/'wp-config.php').write_text(config.replace("define('DB_USER', 'a02_"+storage+"')", "define('DB_USER', 'root')"))
        try:
            probe=b.cmd(['php','/opt/a11/readonly-probe.php'],env={'A11_SITE':str(site)},check=False)
            (OUT/(stem+'-readonly.json')).write_text(probe.stdout)
            b.check(key+':root_write_denied',probe.returncode==0 and all(json.loads(probe.stdout).values()))
        finally: (site/'wp-config.php').write_text(config)
        after=b.fingerprint(db)
        (OUT/(stem+'-after.json')).write_text(json.dumps(after,indent=2)+'\n')
        b.check(key+':all_tables_unchanged',before==after,{'before':before['logical_sha256'],'after':after['logical_sha256'],'tables':len(before['tables'])})
        b.check(key+':files_unchanged',fb==b.files(site),{'sha256':fb})
        b.check(key+':config_never_executed',not pathlib.Path('/scratch/a02-bootstrap-trap').exists())

b.run_storage=run_storage
if __name__=='__main__':
    for p in sorted(pathlib.Path('/subject/a11').glob('*'))+sorted(pathlib.Path('/opt/a11').glob('*.php')):
        if p.suffix=='.php' or p.name=='inventorier-adresses':
            lint=b.cmd(['php','-l',str(p)],check=False)
            b.check('lint:'+p.name,lint.returncode==0)
    result=b.main()
    payload=json.loads((OUT/'result.json').read_text()); payload['suite']='A11-native-public-addresses-on-A02'
    (OUT/'result.json').write_text(json.dumps(payload,indent=2)+'\n')
    sys.exit(result)
