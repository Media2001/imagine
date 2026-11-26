"""Offline runtime checks on the fresh real-extension synthetic export."""
import json
from pathlib import Path
import secrets
import subprocess
import sys
import time
sys.dont_write_bytecode=True
sys.path.insert(0,'/checkout/wp/outils/staging-court')
import inside
import legacy_importer
from database_only import locate_database,database_chunks
from diagnostics import execute,CommandFailure
from sql_stream import validate_file

result={'status':'FAIL','checks':{}}
def sql(text):
    return inside.command(['mariadb','--socket='+inside.SOCKET,'--user=root','--skip-column-names',inside.DB],data=text.encode()).stdout.decode().strip()
def drop():
    inside.command(['mariadb','--socket='+inside.SOCKET,'--user=root','-e','DROP DATABASE IF EXISTS '+inside.DB])
try:
    archive=Path('/scratch/imagine-test-a01-ai1wm-synthetic/wp-content/ai1wm-backups/small.wpress')
    raw=Path('/scratch/fourth-source.sql')
    with archive.open('rb') as source,raw.open('xb') as sink:
        where=locate_database(source)
        for block in database_chunks(source,where): sink.write(block)
    result['database_bytes']=raw.stat().st_size
    assert result['database_bytes']>474*1024**2
    prefix='SERVMASK_PREFIX_'
    decisions={prefix+'fiction_'+suffix:{'action':'garder'} for suffix in ('volume','compat','myisam','memory')}
    normalized=Path('/scratch/fourth-validated.sql')
    started=time.monotonic(); plan=validate_file(raw,legacy_importer,normalized,decisions=decisions)
    result['validation_seconds']=round(time.monotonic()-started,3)
    result['plan']=plan
    imported=inside.import_database(normalized)
    result['checks']['retained_large_database_import']=imported
    assert sql('SELECT COUNT(*),SUM(OCTET_LENGTH(payload)),MAX(OCTET_LENGTH(payload)) FROM '+prefix+'fiction_volume')=='481\t522190848\t18874368'
    result['checks']['wide_rows_readback']=True
    assert sql('SELECT doubled,JSON_VALID(payload),stamp FROM '+prefix+'fiction_compat')=='8\t1\t0000-00-00 00:00:00'
    result['checks']['json_generated_zero_dates']=True
    engines=sql("SELECT ENGINE FROM information_schema.TABLES WHERE TABLE_SCHEMA='"+inside.DB+"' AND TABLE_NAME IN ('"+prefix+"fiction_myisam','"+prefix+"fiction_memory') ORDER BY TABLE_NAME").splitlines()
    assert engines==['MEMORY','MyISAM'],engines
    result['checks']['myisam_memory_engines']=engines
    drop()
    # MySQL8 syntax cannot be emitted by this MariaDB source. Derive a separate
    # explicit fixture from its exact real exporter DDL, never claim MySQL8 ran.
    adapted=Path('/scratch/fourth-mysql8.sql')
    from sql_stream import Framer
    with raw.open('rb') as source,adapted.open('xb') as sink:
        sink.write(b"/*!40101 SET SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;\n")
        def emit(payload):
            if payload.lstrip().upper().startswith(b'CREATE TABLE'):
                payload=payload.replace(b'utf8mb4_unicode_520_ci',b'utf8mb4_0900_ai_ci').replace(b'utf8mb4_unicode_ci',b'utf8mb4_0900_ai_ci')
            sink.write(payload)
        framer=Framer(emit)
        while block:=source.read(1048576): framer.feed(block)
        framer.finish()
    compat=Path('/scratch/fourth-mysql8-normalized.sql')
    cp=validate_file(adapted,legacy_importer,compat)
    assert cp['compatibility']
    inside.import_database(compat)
    result['checks']['mysql8_collation_emulation']={'mapping':cp['compatibility'],'native_mysql8_server':False}
    drop()
    # Real duplicate-key diagnostic. The imported file is the bounded source of
    # line/type/table coordinates, not the potentially personal error message.
    with compat.open('ab') as sink:
        sink.write(("INSERT INTO `"+prefix+"options` (`option_name`,`option_value`,`autoload`) VALUES ('home','FICTION_PRIVATE@example.org','on');\n").encode())
    try:
        inside.import_database(compat)
        raise AssertionError('DUPLICATE_NOT_REFUSED')
    except CommandFailure as error:
        failure=error.failure
        assert failure['stage']=='database_import' and failure['database']['errno']==1062
        assert failure['database']['sqlstate']=='23000' and failure['database']['table']==prefix+'options'
        assert failure['database']['statement']=='INSERT' and failure['database']['line']>0
        assert 'FICTION_PRIVATE' not in json.dumps(failure) and 'Duplicate' not in json.dumps(failure)
        result['checks']['duplicate_key_failure']=failure
    drop()
    # True elapsed timeout, not a patched boundary.
    try:
        execute(['python3','-c','import time; time.sleep(5)'],stage='timeout_canary',timeout=.1,capture_output=True)
        raise AssertionError('TIMEOUT_NOT_REFUSED')
    except CommandFailure as error:
        assert error.failure['timeout_seconds']==.1
        result['checks']['actual_timeout']=error.failure
    plugin=Path('/scratch/fatal/wp-content/plugins/fiction/fatal.php'); plugin.parent.mkdir(parents=True)
    plugin.write_text("<?php throw new LogicException('FICTION_PRIVATE@example.org');")
    try:
        execute(['php',str(plugin)],stage='native_verifier',php=True,capture_output=True)
        raise AssertionError('PHP_NOT_REFUSED')
    except CommandFailure as error:
        assert error.failure['php']['class']=='LogicException'
        assert error.failure['php']['file']=='plugins/fiction/fatal.php'
        assert error.failure['php']['line']==1 and 'FICTION_PRIVATE' not in json.dumps(error.failure)
        result['checks']['actual_php_exception']=error.failure
    native=inside.execute_offline_request(str(archive),{'target_url':'https://imagine-test-fourth.invalid',
        'production_url':'https://synthetic.invalid','password':secrets.token_urlsafe(32),'expected_core_version':'7.0.9','decisions':{}},False)
    result['native']={k:v for k,v in native.items() if k not in ('restored_files_before_cleanup','files_after_cleanup')}
    assert native.get('data_verified') is True,'NATIVE_PHASES_FAILED'
    result['checks']['three_native_phases']=True
    result['status']='PASS'
except Exception as error:
    result['error']={'class':type(error).__name__,'code':str(error) if isinstance(error,AssertionError) else 'FOURTH_VERIFICATION_FAILED'}
    result['failure']=inside.failure_receipt(error).get('failure')
    import traceback
    result['frames']=[{'file':Path(f.filename).name,'line':f.lineno,'function':f.name} for f in traceback.extract_tb(error.__traceback__)]
finally:
    Path('/report/fourth-verification.json').write_text(json.dumps(result,indent=2))
print(json.dumps({'status':result['status'],'checks':len(result['checks'])}))
raise SystemExit(0 if result['status']=='PASS' else 1)
