"""Real AI1WM archive -> actual operator implementation -> independent DB reads."""
import hashlib
import json
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import traceback
sys.dont_write_bytecode=True
TOOLS=Path('/checkout/wp/outils/staging-court')
sys.path.insert(0,str(TOOLS))
import archive
import diagnosis
import legacy_importer
from sql_stream import validate_file
import inside

result={'status':'FAIL','cases':[]}
def sql(query, db=inside.DB):
    return subprocess.check_output(['mariadb','--socket=/scratch/mariadb.sock','--user=root','--skip-column-names',db,'-e',query])
try:
    source=Path('/scratch/imagine-test-a01-ai1wm-synthetic/wp-content/ai1wm-backups/small.wpress')
    fixture=json.loads(Path('/report/database-fixture.json').read_bytes())
    result['archive_sha256']=hashlib.file_digest(source.open('rb'),'sha256').hexdigest()
    cli=[sys.executable,str(TOOLS/'publish.py'),'--diagnose','--operator-ced','--archive',str(source),'--expected-core-version','7.0.9']
    p=subprocess.run(cli+['--detail'],capture_output=True,timeout=180)
    result['diagnostic_exit']=p.returncode
    result['diagnostic']=json.loads(p.stdout)
    assert p.returncode==0 and not result['diagnostic']['blockers']
    p=subprocess.run(cli,capture_output=True,timeout=180)
    result['summary']=p.stdout.decode(); assert p.returncode==0
    assert 'matomo_* 3 videe' in result['summary'] and 'Disque:' in result['summary']
    target=Path('/scratch/raw-restore'); raw=Path('/scratch/raw-database.sql')
    with source.open('rb') as stream: archive.restore(stream,target,sql_path=raw)
    result['real_export_blob_literal_forms']={
        'binary_introducer':b'_binary' in raw.read_bytes(),
        'hexadecimal':b'0x' in raw.read_bytes(),
        'escaped_octets':b'\\0' in raw.read_bytes()}
    normalized=Path('/scratch/default-normalized.sql')
    plan=validate_file(raw,legacy_importer,normalized)
    assert b'FICTION_PRIVATE_SENTINEL' not in normalized.read_bytes()
    assert plan['skipped_inserts'] >= 11
    result['default_skipped_inserts']=plan['skipped_inserts']
    prefix='SERVMASK_PREFIX_'
    tables=['fiction_blob','fiction_kept_blob','fiction_email','matomo_archive_blob_2024_01','matomo_archive_blob_2024_07','matomo_archive_blob_2024_08','ahm_emails','fsmpt_email_logs','wfls_role_counts','pmxi_posts','pmxe_exports']
    for case,decisions,kept in [
        ('default',{},[]),
        ('explicit',{
            prefix+'fiction_kept_blob':{'action':'garder'},
            prefix+'matomo_archive_blob_2024_01':{'action':'garder'},
            prefix+'fiction_email':{'action':'anonymiser','columns':['email']}},
            ['fiction_kept_blob','matomo_archive_blob_2024_01','fiction_email'])]:
        if case == 'explicit':
            decision_path = Path('/scratch/explicit-table-decisions.json')
            decision_path.write_text(json.dumps(decisions))
            probe = subprocess.run(cli + ['--detail','--table-decisions',str(decision_path)],capture_output=True,timeout=180)
            detail = json.loads(probe.stdout)
            assert probe.returncode == 0 and not detail['blockers']
            assert any(r['family']=='matomo_*' and r['action']=='gardee' and r['count']==1 for r in detail['table_families'])
            result['actual_table_decisions_cli'] = {'exit':probe.returncode,'family_override_readback':True}
        if inside.SITE.exists(): shutil.rmtree(inside.SITE)
        sql('DROP DATABASE IF EXISTS '+inside.DB, 'mysql')
        for f in ('a01-source.sql','a01-validated.sql'):
            Path('/scratch',f).unlink(missing_ok=True)
        restored=inside.execute_offline_request(str(source),{'target_url':'https://imagine-test-a01-restored.invalid',
            'production_url':'https://source.synthetic.invalid','password':secrets.token_urlsafe(32),
            'expected_core_version':'7.0.9','decisions':decisions},False)
        row={'case':case,'data_verified':restored.get('data_verified'),'native':{k:v for k,v in restored.items() if k not in ('restored_files_before_cleanup','files_after_cleanup')},'tables':{}}
        result['cases'].append(row)
        assert restored.get('data_verified') is True, restored
        for name in tables:
            count=int(sql('SELECT COUNT(*) FROM `'+prefix+name+'`'))
            assert count==(1 if name in kept else 0),(name,count)
            row['tables'][name]=count
            if name in kept:
                digest=sql('SELECT SHA2(payload,256) FROM `'+prefix+name+'`').decode().strip()
                assert digest==fixture['blob_sha256'],name
        if kept:
            assert sql('SELECT email FROM `'+prefix+'fiction_email`').strip()==b'abonne-1@example.org'
        assert int(sql('SELECT COUNT(*) FROM `'+prefix+'actionscheduler_logs`'))==0
        assert sql('SELECT status,args,COALESCE(extended_args,\'NULL\') FROM `'+prefix+'actionscheduler_actions`').strip()==b'canceled\t[]\tNULL'
        assert sql('SELECT COUNT(*) FROM `'+prefix+'comments` WHERE comment_author_IP<>\'\' OR comment_author<>\'\' OR comment_author_email NOT LIKE \'%@example.org\'').strip()==b'0'
        for folder in ('memberships_profile_fields','download-manager-files'):
            assert not (inside.SITE/'wp-content/uploads'/folder).exists()
        # Independent PDO full-table scan + complete restored file-byte scan.
        program=r'''<?php
        $pdo=new PDO('mysql:unix_socket=/scratch/mariadb.sock;dbname=imagine_a01_staging','root','');
        $markers=['FICTION_PRIVATE_SENTINEL','FICTION_AS_SENTINEL','FICTION_EXTENDED','FICTION_DONE','FICTION_LOG_SENTINEL','FICTION_COMMENT_SENTINEL','FICTION_AUTHOR_SENTINEL','192.0.2.44','FICTION_ADMIN_SENTINEL','FICTION_OPTION_SECRET','sk_live_FICTION_ONLY','pk_live_FICTION_ONLY','whsec_FICTION_ONLY','FICTION_EXCLUDED_SENTINEL'];
        $cells=0; $files=0;
        foreach($pdo->query('SHOW TABLES')->fetchAll(PDO::FETCH_COLUMN) as $table){
          foreach($pdo->query('SELECT * FROM `'.$table.'`') as $row){foreach($row as $value){
            if(!is_string($value))continue; ++$cells;
            foreach($markers as $marker){if(str_contains($value,$marker))throw new RuntimeException('DB_SENTINEL_RESIDUE');}
          }}
        }
        foreach(new RecursiveIteratorIterator(new RecursiveDirectoryIterator('/scratch/a01-site',FilesystemIterator::SKIP_DOTS)) as $file){
          if(!$file->isFile())continue; ++$files; $value=file_get_contents($file->getPathname());
          foreach($markers as $marker){if(str_contains($value,$marker))throw new RuntimeException('FILE_SENTINEL_RESIDUE');}
        }
        echo json_encode(['cells_scanned'=>$cells,'files_scanned'=>$files,'sentinel_residue'=>false]);
        '''
        p=subprocess.run(['php'],input=program.encode(),capture_output=True)
        assert p.returncode==0,p.stderr.decode()
        row['independent_residue_scan']=json.loads(p.stdout)
        row['status']='PASS'
    # Literal forms beyond what this pinned plugin happens to emit: actual DB roundtrip.
    extra=raw.read_bytes()+b"INSERT INTO `SERVMASK_PREFIX_fiction_kept_blob` VALUES (2,_binary'\\0\\n\\r\\t\\b\\Z\\\\\\\'\";'),(3,0x00ff27),(4,X'00FF27');"
    extra_path=Path('/scratch/literal-probe.sql'); extra_path.write_bytes(extra)
    dest=Path('/scratch/literal-probe-normalized.sql')
    plan=validate_file(extra_path,legacy_importer,dest,decisions={prefix+'fiction_kept_blob':{'action':'garder'}})
    sql('CREATE DATABASE literal_probe','mysql')
    with dest.open('rb') as stream:
        p=subprocess.run(['mariadb','--socket=/scratch/mariadb.sock','--user=root','literal_probe'],stdin=stream,capture_output=True)
    assert p.returncode==0
    rows=sql('SELECT id,HEX(payload) FROM `SERVMASK_PREFIX_fiction_kept_blob` WHERE id>1 ORDER BY id','literal_probe').decode().splitlines()
    assert rows==['2\t000A0D09081A5C27223B','3\t00FF27','4\t00FF27'],rows
    result['extra_literal_roundtrip']={'status':'PASS','rows':rows,'separate_from_real_extension_export':True}
    result['status']='PASS'
except Exception as exc:
    result['error']=type(exc).__name__+':'+str(exc)
    result['frames']=traceback.format_exc()
finally:
    Path('/report/database-verification.json').write_text(json.dumps(result,indent=2))
print(json.dumps({'status':result['status'],'cases':len(result['cases'])}))
raise SystemExit(0 if result['status']=='PASS' else 1)
