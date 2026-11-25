"""Reuse the A01 real-plugin fixture, small database-only qualification."""
import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile
import uuid
import zipfile
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'wp/outils/staging-court'))
import publish


def main():
    run = uuid.uuid4().hex[:12]
    out = ROOT/'production/A-01/archive-reelle-3'/run
    out.mkdir(parents=True)
    name = 'imagine-test-a01-db3-'+run
    result = {'status':'FAIL','name':name,'synthetic_only':True,'source_manifest':{}}
    created = False
    policy_only = '--policy-only' in sys.argv
    try:
        stream = io.BytesIO()
        pairs = [(p, 'checkout/'+p.relative_to(ROOT).as_posix()) for p in (ROOT/'wp/outils/staging-court').glob('*.py')]
        pairs += [(ROOT/'wp/outils/staging-court/politique-tables.json', 'checkout/wp/outils/staging-court/politique-tables.json')]
        pairs += [(ROOT/'wp/outils/staging/schema.php','checkout/wp/outils/staging/schema.php'),
                  (ROOT/'wp/outils/staging-wp-integration/worker/worker.py','checkout/wp/outils/staging-court/legacy_importer.py'),
                  (ROOT/'wp/tests/staging-data/fixtures.php','opt/fixtures.php')]
        for f,dest in [('database_fixture.php','opt/dbfixture.php'),('ai1wm_export_fixture.php','opt/fixture.php'),
                       ('database_verify_inside.py','opt/database_verify_inside.py'),('test_database_policy.php','opt/test_database_policy.php')]:
            pairs.append((ROOT/'wp/tests/a01-court'/f,dest))
        pairs += [(Path(__file__),'opt/exercise_database.py'),(ROOT/'wp/tests/a01-court/ai1wm_prepare_inside.py','opt/prepare-source.py')]
        with tarfile.open(fileobj=stream,mode='w') as tar:
            for source,dest in pairs:
                data=source.read_bytes(); result['source_manifest'][source.relative_to(ROOT).as_posix()]=hashlib.sha256(data).hexdigest()
                item=tarfile.TarInfo(dest); item.size=len(data); tar.addfile(item,io.BytesIO(data))
            if not policy_only:
                package=Path('C:/Users/Ced/AppData/Local/hermes/cache/scratch/a01-ai1wm-7.109.zip')
                if not package.exists():
                    from core_source import download
                    raw = download('https://downloads.wordpress.org/plugin/all-in-one-wp-migration.7.109.zip')
                    assert hashlib.sha256(raw).hexdigest() == 'cc592ad8e929d6ddb14b46a70dc840a0571f8bd6addda36a9bbf007d0bb3b72f'
                    package.write_bytes(raw)
                result['plugin_sha256']=hashlib.sha256(package.read_bytes()).hexdigest()
                assert result['plugin_sha256']=='cc592ad8e929d6ddb14b46a70dc840a0571f8bd6addda36a9bbf007d0bb3b72f'
                with zipfile.ZipFile(package) as z:
                    for info in z.infolist():
                        if info.is_dir(): continue
                        assert info.filename.startswith('all-in-one-wp-migration/') and '..' not in info.filename.split('/')
                        data=z.read(info); item=tarfile.TarInfo('opt/public/'+info.filename); item.size=len(data); tar.addfile(item,io.BytesIO(data))
        image=json.loads(publish.call(['image','inspect',publish.IMAGE]).stdout)[0]
        assert not image['Config'].get('Volumes') and not image['Config'].get('ExposedPorts')
        result['image_id']=image['Id']
        publish.call(['create','--pull','never','--name',name,'--label',publish.LABEL+'=true','--network','none','--cap-drop','ALL','--security-opt','no-new-privileges','--memory','1g','--cpus','2','--pids-limit','256','--log-driver','none','--entrypoint','sleep',image['Id'],'infinity'])
        created=True
        result['isolation_before']=publish.offline_isolation(name)
        publish.call(['start',name]); publish.call(['exec','-i',name,'tar','-xf','-','-C','/'],stream.getvalue())
        payload, manifest=publish.offline_runner.payload(True)
        result['source_manifest'].update(manifest)
        publish.call(['exec','-i',name,'tar','-xf','-','-C','/'],payload)
        p=publish.call(['exec',name,'php','/opt/test_database_policy.php'],check=False)
        (out/'native-policy.log').write_bytes(p.stdout+p.stderr)
        result['native_policy_exit']=p.returncode
        if p.returncode: raise RuntimeError('NATIVE_POLICY_FAILED')
        if not policy_only:
            program=(ROOT/'wp/tests/a01-court/ai1wm_prepare_inside.py').read_text()
            program=program.split("wp(['eval-file', '/opt/fixture.php', 'grow'")[0]
            needle="wp(['eval-file', '/opt/fixture.php', 'small', '--use-include'])"
            assert program.count(needle)==1
            program=program.replace(needle,"wp(['eval-file', '/opt/dbfixture.php', '--use-include'])\n"+needle)
            result['bounded_prepare_program_sha256']=hashlib.sha256(program.encode()).hexdigest()
            p=publish.call(['exec','-i',name,'python3','-'],program.encode(),check=False,timeout=1800)
            (out/'prepare.log').write_bytes(p.stdout+p.stderr)
            result['prepare_exit']=p.returncode
            if p.returncode: raise RuntimeError('REAL_EXPORT_FAILED')
            result['real_export']=publish.read_json(name,'/report/export-small.json')
            result['fixture']=publish.read_json(name,'/report/database-fixture.json')
            p=publish.call(['exec',name,'python3','/opt/database_verify_inside.py'],check=False,timeout=1800)
            (out/'verify.log').write_bytes(p.stdout+p.stderr)
            result['verify_exit']=p.returncode
            result['verification']=publish.read_json(name,'/report/database-verification.json')
            if p.returncode or result['verification']['status']!='PASS': raise RuntimeError('DATABASE_VERIFICATION_FAILED')
        result['isolation_after']=publish.offline_isolation(name)
        result['sources_unchanged']=all(hashlib.sha256((ROOT/r).read_bytes()).hexdigest()==h for r,h in result['source_manifest'].items())
        assert result['sources_unchanged']
        result['status']='PASS'
    except Exception as exc:
        result['error']=type(exc).__name__+':'+str(exc)
    finally:
        if created: result['cleanup']=publish.remove_owned(name)
        (out/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({'status':result['status'],'report':str(out/'result.json')}))
    return 0 if result['status']=='PASS' else 1


if __name__=='__main__': raise SystemExit(main())
