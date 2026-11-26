"""Operator base-only rehearsal. Seek over EVERY non-SQL archive payload."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import threading
import time
import uuid
import zlib
from archive import Refusal, header_fields, eof_block, archive_path, DEFAULT_MAX_BYTES, DEFAULT_MAX_ENTRIES, DEFAULT_MAX_SQL_BYTES
from diagnostics import CommandFailure


def locate_database(stream, max_bytes=DEFAULT_MAX_BYTES, max_entries=DEFAULT_MAX_ENTRIES, max_sql_bytes=DEFAULT_MAX_SQL_BYTES):
    start = stream.tell()
    stream.seek(0, 2); end = stream.tell(); stream.seek(start)
    total = entries = 0
    found = None
    while entries <= max_entries:
        offset = stream.tell()-start
        header = stream.read(4377)
        if len(header)!=4377: raise Refusal('ARCHIVE_TRUNCATED')
        if eof_block(header):
            if stream.tell()!=end: raise Refusal('ARCHIVE_TRAILING_DATA')
            if header!=bytes(4377) and int(header[255:269].rstrip(b'\0'))!=offset: raise Refusal('ARCHIVE_EOF_SIZE')
            if found is None: raise Refusal('ARCHIVE_DATABASE_MISSING')
            return dict(found, entries=entries, non_database_payloads_read=False)
        (name,size,stamp,prefix),crc=header_fields(header)
        if not re.fullmatch(r'[0-9]{1,14}',size) or not re.fullmatch(r'[0-9]{1,12}',stamp): raise Refusal('ARCHIVE_HEADER')
        length=int(size); entries+=1; total+=length
        if entries>max_entries or total>max_bytes: raise Refusal('ARCHIVE_LIMIT')
        if stream.tell()+length>end-4377: raise Refusal('ARCHIVE_TRUNCATED')
        if archive_path(prefix,name)=='database.sql':
            if found is not None: raise Refusal('ARCHIVE_PATH_DUPLICATE')
            if length>max_sql_bytes: raise Refusal('ARCHIVE_LIMIT')
            found={'offset':stream.tell(),'length':length,'crc':crc.decode().lower() if crc else None}
        stream.seek(length,1)
    raise Refusal('ARCHIVE_LIMIT')


def database_chunks(stream, where):
    stream.seek(where['offset']); remaining=where['length']; checksum=0
    while remaining:
        data=stream.read(min(1048576,remaining))
        if not data: raise Refusal('ARCHIVE_TRUNCATED')
        remaining-=len(data); checksum=zlib.crc32(data,checksum)
        yield data
    if where['crc'] and f'{checksum:08x}'!=where['crc']: raise Refusal('ARCHIVE_CRC_MISMATCH')


def inside_database(request):
    import inside
    import legacy_importer
    from sql_stream import validate_file
    started=time.monotonic()
    try:
        inside.isolation()
        source=Path('/scratch/a01-source.sql'); normalized=Path('/scratch/a01-validated.sql')
        plan=validate_file(source,legacy_importer,normalized,decisions=request.get('decisions',{}))
        inside.database_start()
        imported=inside.import_database(normalized)
        rows=inside.command(['mariadb','--socket='+inside.SOCKET,'--user=root','--skip-column-names','-e',
             "SELECT TABLE_NAME,ENGINE FROM information_schema.TABLES WHERE TABLE_SCHEMA='"+inside.DB+"'"],stage='database_engine_readback').stdout.decode().splitlines()
        engines={row.split('\t')[0]:row.split('\t')[1].upper() for row in rows}
        if engines!=plan['table_engines']: raise Refusal('TABLE_ENGINE_READBACK_REFUSED')
        return {'status':'DATABASE_IMPORTED_NATIVE_DEFERRED','data_verified':False,'full_staging_ready':False,
                'database_import':imported,'sql_policy':plan,'table_engines':engines,
                'native_phases':{'executed':False,'code':'FILES_REQUIRED_NATIVE_PHASES',
                                 'reason':'Native verification requires the exact archived plugins/core/settings; no surrogate bootstrap is used.'},
                'elapsed_seconds':round(time.monotonic()-started,3)}
    except Exception as error:
        return inside.failure_receipt(error)


def diagnose_database_path(path, limits, decisions_path=None):
    import publish
    run=uuid.uuid4().hex[:12]
    name='imagine-a01-db-only-'+run
    out=publish.ROOT/'production/A-01/archive-reelle-4'/('database-'+run)
    result={'status':'REFUSED','mode':'diagnose-database','created_sites':[],'downloads':0,
            'extracted_wp_content_files':0,'data_verified':False,'full_staging_ready':False}
    created=False
    source=None
    try:
        p=Path(path)
        if p.is_symlink() or not p.is_file() or p.suffix.lower()!='.wpress': raise Refusal('ARCHIVE_SOURCE_REFUSED')
        source=p.open('rb')
        initial=os.fstat(source.fileno())
        where=locate_database(source,**limits)
        # No archive is copied. Check engine space for ONLY SQL + normalization + DB.
        root=publish.call(['info','--format','{{.DockerRootDir}}']).stdout.decode().strip()
        if not root.startswith('/') or any(c in root for c in '\r\n\0'): raise Refusal('CAPACITY_PREFLIGHT_REFUSED')
        free=publish.wsl_python('import json,sys,shutil\nv=json.load(sys.stdin)\nprint(json.dumps({"free":shutil.disk_usage(v["root"]).free}))',json.dumps({'root':root}).encode())['free']
        needed=where['length']*5+512*1024**2
        if free<needed: raise Refusal('DISK_SPACE_INSUFFICIENT')
        result['capacity']={'required_bytes':needed,'free_bytes':free,'before_any_creation':True}
        out.mkdir(parents=True,exist_ok=False)
        # Set ownership as soon as create returns, so failed source copy still cleans.
        image=json.loads(publish.call(['image','inspect',publish.IMAGE]).stdout)[0]
        if image['Config'].get('Volumes') or image['Config'].get('ExposedPorts'): raise Refusal('RUNNER_IMAGE_REFUSED')
        publish.call(['create','--pull','never','--name',name,'--label',publish.LABEL+'=true','--network','none',
                      '--cap-drop','ALL','--security-opt','no-new-privileges','--memory','2g','--cpus','2','--pids-limit','256',
                      '--log-driver','none','--entrypoint','sleep',publish.IMAGE,'infinity'])
        created=True
        result['isolation_before']=publish.offline_isolation(name)
        publish.call(['start',name])
        tar,manifest=publish.offline_runner.payload(False)
        publish.call(['exec','-i',name,'tar','-xf','-','-C','/'],tar)
        result['source_manifest']=manifest
        publish.call(['exec',name,'mkdir','-p','/scratch','/report'])
        child=subprocess.Popen(publish.DOCKER+['exec','-i',name,'tee','/scratch/a01-source.sql'],stdin=subprocess.PIPE,
                               stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        expired=threading.Event()
        def expire():
            expired.set(); child.kill()
        timer=threading.Timer(1800,expire); timer.start()
        try:
            for block in database_chunks(source,where): child.stdin.write(block)
            child.stdin.close()
            child.stderr.read(); child.wait(timeout=30)
            if expired.is_set(): raise CommandFailure('COMMAND_TIMEOUT','database_transport',timeout_seconds=1800)
            if child.returncode: raise CommandFailure('EXTERNAL_COMMAND_REFUSED','database_transport',exit=child.returncode)
        finally:
            timer.cancel()
            if child.poll() is None: child.kill(); child.wait(timeout=30)
        current=os.fstat(source.fileno())
        if (initial.st_size,initial.st_mtime_ns)!=(current.st_size,current.st_mtime_ns): raise Refusal('ARCHIVE_CHANGED')
        decisions=json.loads(Path(decisions_path).read_text(encoding='utf-8')) if decisions_path else {}
        program="import json,sys\nsys.path.insert(0,'/opt/court')\nfrom database_only import inside_database\nr=inside_database("+repr({'decisions':decisions})+")\nfrom pathlib import Path\nPath('/report/database-only.json').write_text(json.dumps(r))\n"
        publish.call(['exec','-i',name,'python3','-'],program.encode(),timeout=5400)
        result.update(publish.read_json(name,'/report/database-only.json'))
        result['database_bytes']=where['length']
        result['non_database_payloads_read']=False
        result['isolation_after']=publish.offline_isolation(name)
        result['sources_unchanged']=all(hashlib.sha256((publish.ROOT/r).read_bytes()).hexdigest()==h for r,h in manifest.items())
        if not result['sources_unchanged']: raise Refusal('SOURCE_CHANGED')
    except Exception as error:
        result['status']='REFUSED'
        result['failure']=error.failure if isinstance(error,CommandFailure) else {'stage':'database_preflight',
            'code':str(error) if isinstance(error,Refusal) else 'DATABASE_DIAGNOSIS_REFUSED', 'class':type(error).__name__}
    finally:
        if source: source.close()
        if created:
            try: result['cleanup']=publish.remove_owned(name)
            except Exception as error: result['cleanup_failure']={'stage':'runner_removal','code':'REMOVAL_NOT_PROVEN','class':type(error).__name__}
        result['recorded_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
        if out.exists():
            result['report']=str(out/'result.json')
            (out/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result
