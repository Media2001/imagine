"""Read-only/current-source qualification on the owned real-export fixture."""
import hashlib
import io
import json
from pathlib import Path
import sys
import tarfile
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'wp/outils/staging-court'))
import publish


def main():
    out = Path(sys.argv[1])
    receipt = json.loads((out / 'prepare.json').read_bytes())
    assert receipt['status'] == 'PREPARED' and receipt['created'] is True
    name = receipt['name']
    assert name.startswith('imagine-test-a01-ai1wm-')
    result = {'status':'FAIL', 'synthetic_only':True, 'name':name, 'isolation_before':publish.offline_isolation(name)}
    attempt = __import__('uuid').uuid4().hex[:8]
    files = list((ROOT / 'wp/outils/staging-court').glob('*.py'))
    files += list((ROOT / 'wp/tests/a01-court').glob('test_*.py'))
    files += [ROOT / 'wp/tests/a01-court/ai1wm_verify_inside.py', ROOT / 'wp/outils/staging/schema.php', ROOT / 'wp/outils/staging/policy.php', ROOT / 'wp/outils/staging/lib.php', ROOT / 'wp/outils/staging-wp-integration/worker/worker.py']
    files += [ROOT / 'wp/tests/a01-court' / f for f in ('prepare_ai1wm.py','ai1wm_prepare_inside.py','ai1wm_export_fixture.php','exercise_ai1wm.py','test_native_file_policy.php','verify_ai1wm_final.py')]
    result['source_manifest'] = {}
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode='w') as tar:
        for source in files:
            raw = source.read_bytes(); rel = source.relative_to(ROOT).as_posix()
            result['source_manifest'][rel] = hashlib.sha256(raw).hexdigest()
            item = tarfile.TarInfo('checkout/' + rel); item.size = len(raw); tar.addfile(item, io.BytesIO(raw))
        raw = (ROOT / 'wp/outils/staging-wp-integration/worker/worker.py').read_bytes()
        item = tarfile.TarInfo('checkout/wp/outils/staging-court/legacy_importer.py'); item.size = len(raw); tar.addfile(item, io.BytesIO(raw))
    publish.call(['exec', '-i', name, 'tar', '-xf', '-', '-C', '/'], stream.getvalue())
    data, unused = publish.offline_runner.payload(True)
    result['source_manifest'].update(unused)
    publish.call(['exec', '-i', name, 'tar', '-xf', '-', '-C', '/'], data)
    result['units'] = []
    publish.call(['exec',name,'mkdir','-p','/scratch/native-data'])
    commands = [
        ('archive', ['python3','-m','unittest','discover','-s','/checkout/wp/tests/a01-court','-p','test_archive*.py','-v']),
        ('harness', ['python3','/opt/e2e/test_harness.py']),
        ('data', ['env','PHP_BIN=/usr/bin/php','IMAGINE_TEST_SCRATCH=/scratch/native-data',
                  'python3','/checkout/wp/tests/staging-data/verify.py','--output','/report/a01-native-data.json'])]
    for key, command in commands:
        p = publish.call(['exec','-e','PYTHONPATH=/checkout/wp/outils/staging-court','-e','TMPDIR=/scratch',name]+command,check=False)
        log = key+'-'+attempt+'.log'
        (out/log).write_bytes(p.stdout+p.stderr)
        result['units'].append({'key':key,'exit':p.returncode,'log':log})
        if key=='data' and p.returncode==0:
            result['units'][-1]['receipt']=publish.read_json(name,'/report/a01-native-data.json')
    p = publish.call(['exec','-i',name,'php'], (ROOT/'wp/tests/a01-court/test_native_file_policy.php').read_bytes(),check=False)
    (out/('native-files-'+attempt+'.log')).write_bytes(p.stdout+p.stderr)
    result['native_file_policy_exit'] = p.returncode
    execution = publish.call(['exec', '-e', 'PYTHONDONTWRITEBYTECODE=1', name, 'python3', '/checkout/wp/tests/a01-court/ai1wm_verify_inside.py'], check=False, timeout=1800)
    (out / ('qualification-'+attempt+'.log')).write_bytes(execution.stdout + execution.stderr)
    result['exit'] = execution.returncode
    subject = publish.call(['exec', name, 'cat', '/report/ai1wm-verification.json'], check=False)
    if subject.returncode == 0: result['subject'] = json.loads(subject.stdout)
    if execution.returncode == 0:
        import os
        import tempfile
        scratch = Path('C:/Users/Ced/AppData/Local/hermes/cache/scratch')
        with tempfile.TemporaryDirectory(prefix='a01-ai1wm-capacity-',dir=scratch) as temporary:
            source = Path(temporary)/'synthetic-small.wpress'
            destination = '/mnt/' + source.as_posix()[0].lower() + source.as_posix()[2:] if os.name=='nt' else str(source)
            publish.call(['cp',name+':/scratch/imagine-test-a01-ai1wm-synthetic/wp-content/ai1wm-backups/small.wpress',destination])
            with source.open('rb') as stream:
                digest=hashlib.file_digest(stream,'sha256').hexdigest()
            assert digest==next(row for row in result['subject']['cases'] if row['case']=='small')['archive_sha256']
            result['capacity_preflight']=publish.archive_capacity_on_engine(source,{})
        assert not Path(temporary).exists()
        result['capacity_test_synthetic_host_directory_removed']=True
        program = b"import pathlib,subprocess\np=pathlib.Path('/tmp/a01.sock')\nif p.is_symlink():\n assert p.readlink()==pathlib.Path('/scratch/mariadb.sock')\n p.unlink()\nassert not p.exists()\np.symlink_to('/scratch/mariadb.sock')\nsubprocess.run(['mariadb','--socket=/scratch/mariadb.sock','--user=root','-e','DROP DATABASE IF EXISTS wordpress; CREATE DATABASE wordpress'],check=True)\n"
        publish.call(['exec','-i',name,'python3','-'],program)
        publish.pipe_sanitized_database(name,name)
        program = b"import json,subprocess\nargs=['mariadb','--socket=/scratch/mariadb.sock','--user=root','--skip-column-names','-e']\na=subprocess.check_output(args+[\"SELECT COUNT(*),SUM(LENGTH(post_content)) FROM imagine_a01_staging.SERVMASK_PREFIX_posts\"])\nb=subprocess.check_output(args+[\"SELECT COUNT(*),SUM(LENGTH(post_content)) FROM wordpress.SERVMASK_PREFIX_posts\"])\nassert a==b\nprint(json.dumps({'exact_counts_and_content_bytes':True,'total_content_bytes':int(a.split()[1])}))\n"
        result['sanitized_dump_pipe'] = json.loads(publish.call(['exec','-i',name,'python3','-'],program).stdout)
    result['isolation_after'] = publish.offline_isolation(name)
    result['sources_unchanged'] = all(hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == digest for rel,digest in result['source_manifest'].items())
    result['status'] = 'PASS' if result['sources_unchanged'] and result['native_file_policy_exit']==0 and all(v['exit']==0 for v in result['units']) and execution.returncode == 0 and result.get('subject',{}).get('status') == 'PASS' else 'FAIL'
    if '--cleanup' in sys.argv[2:]:
        result['cleanup'] = publish.remove_owned(name)
        (out/'cleanup.json').write_text(json.dumps(result['cleanup'],indent=2))
    (out / ('qualification-' + attempt + '.json')).write_text(json.dumps(result,indent=2))
    print(json.dumps({'status':result['status'],'output':str(out),'exit':execution.returncode}))
    return 0 if result['status']=='PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
