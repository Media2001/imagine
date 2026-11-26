"""A16 native fixture, same read-only A11 bootstrap in classic and HPOS."""
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
def inventory(site,out,audit,mapping='/subject/a16/correspondance.exemple.json',*extra):
    return b.cmd(['python3','/subject/a16/confine.py','--wp-path='+str(site),'--output='+str(out),'--audit='+str(audit),'--correspondance='+str(mapping),*extra],check=False)
def run_storage(storage):
    site,db,_=b.install(storage);(OUT/(storage+'-seed.json')).unlink()
    cfg=(site/'wp-config.php').read_text();writable=cfg.replace("define('DB_USER', 'a02_"+storage+"')","define('DB_USER', 'root')").split("\nfile_put_contents('/scratch/a02-bootstrap-trap'")[0]
    (site/'wp-config.php').write_text(writable)
    try:
        p=b.wp(site,['eval-file','/opt/a16/seed.php','--use-include']);oracle=json.loads(next(x[9:] for x in p.stdout.splitlines() if x.startswith('A16_JSON=')))
    finally:(site/'wp-config.php').write_text(cfg)
    (OUT/(storage+'-oracle.json')).write_text(json.dumps(oracle))
    mu=site/'wp-content/mu-plugins/a16-runtime.php';mu.write_text('''<?php
register_post_type('a16_numero', ['public'=>false]);
register_post_type('a16_article', ['public'=>false]);
register_taxonomy('a16_theme', 'a16_article');
register_taxonomy('a16_issue', 'a16_article');
if (getenv('A16_CONFINED') === '1') {
 global $wpdb; require_once ABSPATH.'wp-includes/pluggable.php';
 if ($wpdb->query('UPDATE wp_posts SET ID=ID WHERE 1=0') !== false
 || @mysqli_query($wpdb->dbh,'UPDATE wp_posts SET ID=ID WHERE 1=0') !== false
 || @file_put_contents(ABSPATH.'forbidden','NO') !== false
 || wp_mail('fictif@example.org','A16_PRIVATE_CANARY','A16_PRIVATE_CANARY') !== false
 || !is_wp_error(wp_remote_get('https://forbidden.invalid/'))
 || wp_schedule_single_event(time()+9999,'a16_forbidden') !== false
 || function_exists('mail') || function_exists('exec')) { throw new RuntimeException('A16_EARLY_GUARDS_FAILED'); }
 echo 'A16_BOOT_PRIVATE_CANARY';
}
''')
    audit=OUT/(storage+'-audit');b.check(storage+':a02_audit',b.audit(site,audit).returncode==0)
    before=b.fingerprint(db);files=b.files(site);(OUT/(storage+'-db-before.json')).write_text(json.dumps(before))
    dest=OUT/(storage+'-issues');p=inventory(site,dest,audit/'audit.json')
    b.check(storage+':cli_and_actual_readonly_guards',p.returncode==0,{'exit':p.returncode,'stderr':p.stderr[:180]})
    d=json.loads((dest/'numeros.json').read_text());rows=d['issues'];ids=oracle['issues']
    expected=[{'id':ids[2],'date_utc':'2026-03-01T12:00:00Z','articles':2,'published_articles':1,'unpublished_articles':1,'without_theme':1,'multiple_themes':1,'without_featured_image':1,'attached_media':2,'missing_media_files':1,'pdf':'oui','pdf_public':True},
    {'id':ids[1],'date_utc':'2026-02-01T12:00:00Z','articles':1,'published_articles':1,'unpublished_articles':0,'without_theme':0,'multiple_themes':0,'without_featured_image':1,'attached_media':0,'missing_media_files':0,'pdf':'declare_mais_fichier_absent','pdf_public':True},
    {'id':ids[0],'date_utc':'2026-01-01T12:00:00Z','articles':1,'published_articles':1,'unpublished_articles':0,'without_theme':0,'multiple_themes':0,'without_featured_image':1,'attached_media':0,'missing_media_files':0,'pdf':'non','pdf_public':None}]
    expected += [{'id':ids[i],'date_utc':'2025-12-01T12:00:00Z','articles':0,'published_articles':0,'unpublished_articles':0,'without_theme':0,'multiple_themes':0,'without_featured_image':0,'attached_media':0,'missing_media_files':0,'pdf':'non','pdf_public':None} for i in [4,3]]
    b.check(storage+':equal_dates_id_descending',[r['id'] for r in rows[-2:]]==[ids[4],ids[3]] and rows[-2]['date_utc']==rows[-1]['date_utc'])
    b.check(storage+':exact_all_issue_counts_dates_pdf_media_themes',rows==expected,rows)
    b.check(storage+':orphan_published_by_utc_year',d['orphan_published_by_year']==[{'year':2025,'articles':1}])
    payload=''.join(x.read_text() for x in dest.iterdir())+p.stdout+p.stderr
    b.check(storage+':no_titles_text_author_paths',not re.search(r'CANARY|@|/scratch|present\.|missing\.|post_title|post_content|post_author',payload))
    b.check(storage+':private_permissions',dest.stat().st_mode&0o777==0o700 and all(x.stat().st_mode&0o777==0o600 for x in dest.iterdir()))
    limited=OUT/(storage+'-limit');p=inventory(site,limited,audit/'audit.json','/subject/a16/correspondance.exemple.json','--limit=2')
    b.check(storage+':configurable_last_n_and_deterministic_order',p.returncode==0 and json.loads((limited/'numeros.json').read_text())['issues']==expected[:2])
    limited_report=json.loads((limited/'numeros.json').read_text())
    b.check(storage+':excluded_number_article_not_orphan',expected[2]['articles']==1 and expected[2]['id'] not in [r['id'] for r in limited_report['issues']] and limited_report['orphan_published_by_year']==[{'year':2025,'articles':1}])
    private_root=Path('/scratch/a16-private');private_before=b.files(private_root)
    private_map=json.loads(Path('/subject/a16/correspondance.exemple.json').read_text());private_map.update({'racine_privee':str(private_root),'pdf_cle':'_a16_private_pdf_id'})
    private_config=OUT/(storage+'-private.json');private_config.write_text(json.dumps(private_map))
    private_out=OUT/(storage+'-private');private_run=inventory(site,private_out,audit/'audit.json',private_config)
    b.check(storage+':private_root_inventory_succeeds',private_run.returncode==0,{'exit':private_run.returncode,'stderr':private_run.stderr})
    private_rows=json.loads((private_out/'numeros.json').read_text())['issues']
    b.check(storage+':private_pdf_present',private_rows[0]==dict(expected[0],pdf='oui',pdf_public=False))
    b.check(storage+':private_pdf_absent',private_rows[1]==dict(expected[1],pdf='declare_mais_fichier_absent',pdf_public=False))
    private_payload=private_run.stdout+private_run.stderr+''.join(x.read_text() for x in private_out.iterdir())
    b.check(storage+':private_root_paths_never_output',not re.search(r'CANARY|/scratch|a16-private',private_payload))
    b.check(storage+':private_files_unchanged',private_before==b.files(private_root))

    variants=[('parent',{'liaison':{'source':'post_parent','cle':'post_parent'}}),('taxonomy',{'numero_source':'taxonomy','numero_type':'a16_issue','date_cle':'_a16_date','liaison':{'source':'taxonomy','cle':'a16_issue'}})]
    for label,updates in variants:
        config=json.loads(Path('/subject/a16/correspondance.exemple.json').read_text());config.update(updates);f=OUT/(storage+'-'+label+'.json');f.write_text(json.dumps(config));vout=OUT/(storage+'-'+label)
        q=inventory(site,vout,audit/'audit.json',f);expected_variant=[dict(row) for row in expected]
        if label=='taxonomy':
            term_ids=dict(zip(ids,oracle['terms']))
            for row in expected_variant:row['id']=term_ids[row['id']]
        b.check(storage+':explicit_link_variant:'+label,q.returncode==0 and json.loads((vout/'numeros.json').read_text())['issues']==expected_variant,{'exit':q.returncode,'stderr':q.stderr[:180]})
    repeat=OUT/(storage+'-repeat');p=inventory(site,repeat,audit/'audit.json');b.check(storage+':replay_identical',p.returncode==0 and {x.name:x.read_bytes() for x in repeat.iterdir()}=={x.name:x.read_bytes() for x in dest.iterdir()})
    for label,path in [('exists',dest),('site',site/'forbidden'),('repo',Path('/subject/forbidden')),('ancestor',site.parent/'forbidden'),('root',Path('/forbidden'))]:
        bad=inventory(site,path,audit/'audit.json');b.check(storage+':guard:'+label,bad.returncode==1 and (path==dest or not path.exists()))
    raw=b.cmd(['php','/subject/a16/inventorier-numeros','--wp-path='+str(site),'--output=/report/'+storage+'-raw','--audit='+str(audit/'audit.json'),'--correspondance=/subject/a16/correspondance.exemple.json'],check=False)
    b.check(storage+':unconfined_refused',raw.returncode==1 and raw.stderr=='A16_CONFINEMENT_REQUIRED\n')
    dropin=site/'wp-content/object-cache.php';dropin.write_text('<?php throw new RuntimeException("NEVER_RUN");')
    try:
        bad=inventory(site,OUT/(storage+'-dropin'),audit/'audit.json');b.check(storage+':dropin_named_no_execution',bad.returncode==1 and bad.stderr=='A11_DROPIN_UNSUPPORTED {"file":"wp-content/object-cache.php"}\n')
    finally:dropin.unlink()
    after=b.fingerprint(db);(OUT/(storage+'-db-after.json')).write_text(json.dumps(after));b.check(storage+':all_tables_scheduler_identical',before==after);b.check(storage+':files_identical',files==b.files(site));b.check(storage+':config_not_executed',not Path('/scratch/a02-bootstrap-trap').exists())
    mapping=json.loads(Path('/subject/a16/correspondance.exemple.json').read_text());mapping['liaison']['cle']='absent_key';badmap=OUT/(storage+'-absent.json');badmap.write_text(json.dumps(mapping))
    bad=inventory(site,OUT/(storage+'-missing'),audit/'audit.json',badmap)
    b.check(storage+':absent_mapping_key_named',bad.returncode==1 and bad.stderr=='A16_MAPPING_KEY_ABSENT {"key":"absent_key"}\n')
    missing=b.cmd(['python3','/subject/a16/confine.py','--wp-path='+str(site),'--output=/report/'+storage+'-nomap','--audit='+str(audit/'audit.json')],check=False)
    b.check(storage+':mapping_required',missing.returncode==1 and missing.stderr=='A16_MAPPING_REQUIRED\n')
b.run_storage=run_storage
if __name__=='__main__':sys.exit(b.main())
