"""Fourth-pass acceptance on an unmodified real AI1WM synthetic export."""
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tarfile
import time
import uuid
import zipfile
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'wp/outils/staging-court'))
import publish
from core_source import download
from database_only import diagnose_database_path


def main():
    run=uuid.uuid4().hex[:12]; name='imagine-test-a01-fourth-'+run
    out=ROOT/'production/A-01/archive-reelle-4'/run; out.mkdir(parents=True)
    scratch=Path('C:/Users/Ced/AppData/Local/hermes/cache/scratch')/('a01-fourth-'+run)
    scratch.mkdir()
    result={'status':'FAIL','synthetic_only':True,'name':name,'checks':{}}
    created=False
    try:
        manifest=publish.fresh_runner(name); created=True
        result['isolation_before']=publish.offline_isolation(name)
        pairs=[(p,'checkout/'+p.relative_to(ROOT).as_posix()) for p in (ROOT/'wp/outils/staging-court').glob('*.py')]
        pairs += [(ROOT/'wp/outils/staging-court/politique-tables.json','checkout/wp/outils/staging-court/politique-tables.json'),
                  (ROOT/'wp/outils/staging/schema.php','checkout/wp/outils/staging/schema.php'),
                  (ROOT/'wp/outils/staging-wp-integration/worker/worker.py','checkout/wp/outils/staging-court/legacy_importer.py')]
        for source,dest in [('database_fixture.php','dbfixture-original.php'),('fourth_fixture.php','dbfixture.php'),
                            ('ai1wm_export_fixture.php','fixture.php'),('test_diagnostics.php','test_diagnostics.php'),
                            ('fourth_verify.py','fourth_verify.py')]:
            pairs.append((ROOT/'wp/tests/a01-court'/source,'opt/'+dest))
        stream=io.BytesIO()
        package=scratch/'ai1wm.zip'
        raw=download('https://downloads.wordpress.org/plugin/all-in-one-wp-migration.7.109.zip')
        result['plugin_sha256']=hashlib.sha256(raw).hexdigest()
        assert result['plugin_sha256']=='cc592ad8e929d6ddb14b46a70dc840a0571f8bd6addda36a9bbf007d0bb3b72f'
        with tarfile.open(fileobj=stream,mode='w') as tar:
            for path,dest in pairs:
                data=path.read_bytes(); manifest[path.relative_to(ROOT).as_posix()]=hashlib.sha256(data).hexdigest()
                item=tarfile.TarInfo(dest); item.size=len(data); tar.addfile(item,io.BytesIO(data))
            with zipfile.ZipFile(io.BytesIO(raw)) as z:
                for info in z.infolist():
                    if info.is_dir(): continue
                    assert info.filename.startswith('all-in-one-wp-migration/') and '..' not in info.filename.split('/')
                    data=z.read(info); item=tarfile.TarInfo('opt/public/'+info.filename); item.size=len(data); tar.addfile(item,io.BytesIO(data))
        result['source_manifest']=manifest
        publish.call(['exec','-i',name,'tar','-xf','-','-C','/'],stream.getvalue())
        program=(ROOT/'wp/tests/a01-court/ai1wm_prepare_inside.py').read_text()
        program=program.split("wp(['eval-file', '/opt/fixture.php', 'grow'")[0]
        program=program.replace("wp(['eval-file', '/opt/fixture.php', 'small', '--use-include'])", "wp(['eval-file', '/opt/dbfixture.php', '--use-include'])\nwp(['eval-file', '/opt/fixture.php', 'small', '--use-include'])")
        started=time.monotonic()
        p=publish.call(['exec','-i',name,'python3','-'],program.encode(),check=False,timeout=1800)
        (out/'prepare.log').write_bytes(p.stdout+p.stderr)
        result['prepare_exit']=p.returncode
        assert p.returncode==0,'REAL_EXPORT_FAILED'
        result['export_elapsed_seconds']=round(time.monotonic()-started,3)
        result['real_export']=publish.read_json(name,'/report/export-small.json')
        result['fixture']=publish.read_json(name,'/report/fourth-fixture.json')
        p=publish.call(['exec',name,'php','/opt/test_diagnostics.php'],check=False)
        (out/'php-diagnostics.log').write_bytes(p.stdout+p.stderr)
        result['checks']['php_diagnostics']={'exit':p.returncode}
        assert p.returncode==0,'PHP_DIAGNOSTICS_FAILED'
        p=publish.call(['exec',name,'python3','/opt/fourth_verify.py'],check=False,timeout=1800)
        (out/'verification.log').write_bytes(p.stdout+p.stderr)
        result['inside']=publish.read_json(name,'/report/fourth-verification.json')
        assert p.returncode==0 and result['inside']['status']=='PASS','INSIDE_ACCEPTANCE_FAILED'
        source='/scratch/imagine-test-a01-ai1wm-synthetic/wp-content/ai1wm-backups/small.wpress'
        archive=scratch/'synthetic.wpress'
        linux='/mnt/c/'+str(archive)[3:].replace('\\','/') if os.name=='nt' else str(archive)
        publish.call(['cp',name+':'+source,linux],timeout=600)
        # Actual operator CLI on a generated fake archive, never Imagine input.
        p=publish.execute([sys.executable,str(ROOT/'wp/outils/staging-court/publish.py'),'--diagnose-database','--operator-ced',
                          '--archive',str(archive)],capture_output=True,timeout=1800,stage='synthetic_database_cli',check=False)
        (out/'database-cli.json').write_bytes(p.stdout)
        result['database_cli_exit']=p.returncode
        result['database_cli']=json.loads(p.stdout)
        assert p.returncode==0 and result['database_cli']['cleanup']['absent'],'DATABASE_CLI_FAILED'
        assert not result['database_cli']['created_sites'] and not result['database_cli']['non_database_payloads_read']
        result['isolation_after']=publish.offline_isolation(name)
        result['sources_unchanged']=all(hashlib.sha256((ROOT/r).read_bytes()).hexdigest()==h for r,h in manifest.items())
        assert result['sources_unchanged']
        result['status']='PASS'
    except Exception as error:
        result['error']={'class':type(error).__name__,'code':str(error) if isinstance(error,AssertionError) else 'FOURTH_ACCEPTANCE_FAILED'}
        import traceback
        result['frames']=[{'file':Path(f.filename).name,'line':f.lineno,'function':f.name} for f in traceback.extract_tb(error.__traceback__)]
    finally:
        if created: result['cleanup']=publish.remove_owned(name)
        shutil.rmtree(scratch)
        result['scratch_removed']=not scratch.exists()
        (out/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({'status':result['status'],'report':str(out/'result.json')}))
    return 0 if result['status']=='PASS' else 1


if __name__=='__main__': raise SystemExit(main())
