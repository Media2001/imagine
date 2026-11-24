"""Real-extension archive assertions; no generated positive wire format."""
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import struct
import subprocess
import sys
import traceback
sys.dont_write_bytecode = True
TOOLS = Path('/checkout/wp/outils/staging-court')
sys.path.insert(0, str(TOOLS))
import archive
import diagnosis
import legacy_importer
from sql_stream import validate_file

result = {'status':'FAIL','cases':[], 'real_extension':'7.109', 'handcrafted_positive_archives':False}
try:
    site = Path('/scratch/imagine-test-a01-ai1wm-synthetic')
    for case in ('small','large'):
        source = site / ('wp-content/ai1wm-backups/' + case + '.wpress')
        record = {'case':case, 'archive_bytes':source.stat().st_size}
        result['cases'].append(record)
        with source.open('rb') as stream:
            header = stream.read(4377)
            record['root_prefix'] = header[281:4369].split(b'\0')[0].decode()
            stream.seek(-4377,2)
            record['eof_v2'] = bool(archive.eof_block(stream.read(4377)))
        with source.open('rb') as stream:
            record['archive_sha256'] = hashlib.file_digest(stream,'sha256').hexdigest()
        # Real CLI under a 256 MiB address-space limit: diagnosis is read-only.
        def bound(): resource.setrlimit(resource.RLIMIT_AS,(256*1024**2,256*1024**2))
        cli = [sys.executable,str(TOOLS/'publish.py'),'--diagnose','--operator-ced','--archive',str(source),'--expected-core-version','7.0.9']
        p = subprocess.run(cli + ['--detail'],capture_output=True,preexec_fn=bound,timeout=1200)
        record['diagnostic_exit'] = p.returncode
        if p.returncode:
            Path('/report/' + case + '-failed-detail.json').write_bytes(p.stdout)
            sys.stderr.buffer.write(p.stderr[-3000:])
        report = json.loads(p.stdout)
        record['diagnostic'] = report
        assert p.returncode == 0, report['blockers']
        assert report['complete'] and not report['blockers']
        assert report['database_bytes'] > (128*1024**2 if case == 'large' else 0)
        assert report['entries'] > (30000 if case == 'large' else 10)
        assert report['inventory']['plugins'] == ['akismet']  # exporter omits itself
        assert next(r for r in report['rules'] if r['code']=='SECRET_OU_IDENTIFIANT')['blocking'] is False
        p = subprocess.run(cli,capture_output=True,preexec_fn=bound,timeout=1200)
        assert p.returncode == 0
        record['summary_lines'] = len(p.stdout.splitlines())
        record['summary'] = p.stdout.decode()
        assert record['summary_lines'] <= 25
        if case == 'large':
            assert sum(row['bytes'] for row in report['inventory']['uploads'] if row['directory']=='2026') > 1024**3
        target = Path('/scratch/restored-' + case)
        sql_path = Path('/scratch/restored-' + case + '.sql')
        if target.exists(): shutil.rmtree(target)
        if sql_path.exists(): sql_path.unlink()
        # Instrument read intervals; excluded payloads cannot reach any observer.
        class NoExcludedRead:
            def __init__(self, stream): self.stream=stream; self.protected=[]
            def tell(self): return self.stream.tell()
            def seekable(self): return True
            def seek(self,*args): return self.stream.seek(*args)
            def read(self,n=-1):
                pos=self.tell()
                assert n >= 0
                assert not any(pos < end and pos+n > begin for begin,end in self.protected), 'EXCLUDED_BYTES_READ'
                data=self.stream.read(n)
                if n==4377 and len(data)==4377 and not archive.eof_block(data):
                    fields,crc=archive.header_fields(data)
                    name,size,stamp,prefix=fields
                    if archive.excluded(archive.archive_path(prefix,name)):
                        self.protected.append((pos+4377,pos+4377+int(size)))
                return data
        with source.open('rb') as stream:
            guarded=NoExcludedRead(stream)
            restore_report={}
            sql,package,count=archive.restore(guarded,target,sql_path=sql_path,report=restore_report)
            record['excluded_read_guard_intervals']=len(guarded.protected)
        assert isinstance(sql,Path)
        for path in ('uploads/wpallexport/fiction.csv','uploads/wc-logs/order.log','uploads/woocommerce_uploads/private.csv',
                     'uploads/simple-file-list/private.html','themes/fiction-backup.zip'):
            assert not (target/path).exists()
        for path in ('uploads/woocommerce_uploads/issue.pdf','uploads/simple-file-list/issue.jpg','uploads/2026/11/fixture.jpg'):
            assert (target/path).read_bytes()==(site/'wp-content'/path).read_bytes()
        normalized = Path('/scratch/validated-' + case + '.sql')
        if normalized.exists(): normalized.unlink()
        plan = validate_file(sql,legacy_importer,normalized)
        record['sql_plan'] = plan
        database='a01_restored_' + case
        subprocess.run(['mariadb','--socket=/scratch/mariadb.sock','--user=root','-e','DROP DATABASE IF EXISTS '+database+'; CREATE DATABASE '+database],check=True,capture_output=True)
        with normalized.open('rb') as src:
            imported=subprocess.run(['mariadb','--socket=/scratch/mariadb.sock','--user=root',database],stdin=src,capture_output=True)
        assert imported.returncode==0, imported.stderr[-200:]
        prefix=plan['prefix']
        query='SELECT COUNT(*) FROM `'+prefix+'posts` WHERE post_title LIKE \'FICTION GENERATED %\''
        count=int(subprocess.run(['mariadb','--socket=/scratch/mariadb.sock','--user=root','--skip-column-names',database,'-e',query],check=True,capture_output=True).stdout)
        assert count == (1500 if case=='large' else 0)
        record.update(restored_generated_posts=count,restoration_exclusions=restore_report['excluded'],retained_files=sum(1 for p in target.rglob('*') if p.is_file()),payload_never_read=True,streamed_sql_import=True)
        if case=='large': assert record['retained_files']>32000
        # Exact offline operator implementation, including all three native phases.
        from inside import execute_offline_request, SITE, DB
        import secrets
        if SITE.exists(): shutil.rmtree(SITE)
        subprocess.run(['mariadb','--socket=/scratch/mariadb.sock','--user=root','-e','DROP DATABASE IF EXISTS '+DB],check=True,capture_output=True)
        for name in ('a01-source.sql', 'a01-validated.sql'):
            stale=Path('/scratch')/name
            if stale.exists(): stale.unlink()
        offline=execute_offline_request(str(source), {'target_url':'https://imagine-test-a01-restored.invalid',
            'production_url':'https://source.synthetic.invalid', 'password':secrets.token_urlsafe(32),
            'expected_core_version':'7.0.9','decisions':{}}, False)
        record['native_offline']={k:v for k,v in offline.items() if k not in ('restored_files_before_cleanup','files_after_cleanup')}
        assert offline.get('data_verified') is True, record['native_offline']
        assert offline['restored_files_before_cleanup']['uploads/woocommerce_uploads/issue.pdf']==offline['files_after_cleanup']['uploads/woocommerce_uploads/issue.pdf']
        record['native_three_phases_pass']=True
        record['status']='PASS'
    result['peak_child_rss_kib']=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    result['status']='PASS'
except Exception as exc:
    result['error']=type(exc).__name__+':'+str(exc)
    result['frames']=traceback.format_exc()
finally:
    Path('/report/ai1wm-verification.json').write_text(json.dumps(result,indent=2))
print(json.dumps({'status':result['status'],'cases':[{k:v for k,v in c.items() if k in ('case','status','diagnostic_exit','archive_bytes')} for c in result['cases']]}))
raise SystemExit(0 if result['status']=='PASS' else 1)
