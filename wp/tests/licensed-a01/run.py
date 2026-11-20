"""Execute only targeted licensed cases; preserve existing baseline/harness."""
import collections,datetime,hashlib,json,pathlib,sys,uuid
ROOT=pathlib.Path(__file__).resolve().parent
BASE=ROOT.parent/'staging-e2e'
sys.dont_write_bytecode=True
sys.path.insert(0,str(BASE))
from harness import Harness,validate_inspection,SUBJECT_FILES,LABEL
class Target(Harness):
    def __init__(self):
        self.use_wsl=True;self.docker=['wsl.exe','-d','Ubuntu','--','docker'];self.checks=[];self.run_id=uuid.uuid4().hex[:12];self.container=None;self.container_created=False
        self.evidence=ROOT/'evidence'/self.run_id;self.evidence.mkdir(parents=True)

def main():
    h=Target();status=1
    subject=ROOT.parent.parent/'outils/staging'
    manifest={n:hashlib.sha256((subject/n).read_bytes()).hexdigest()for n in SUBJECT_FILES}
    prior=json.loads((BASE/'evidence/f36c72f4d187/subject-source.json').read_text())
    assert manifest==prior,'Existing stabilized subject baseline drifted'
    (h.evidence/'subject-source.json').write_text(json.dumps(manifest,indent=2)+'\n')
    names=['run.py','inside-commercial.py','cases.php','diagnostic.php','prepare.py','compatible.lock.json']
    sources={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest()for n in names}
    for n in ['inside.py','worker-bridge.php','subject-adapter.json','harness.py']:
        sources['baseline:'+n]=hashlib.sha256((BASE/n).read_bytes()).hexdigest()
    (h.evidence/'driver-source.json').write_text(json.dumps(sources,indent=2)+'\n')
    lock=json.loads((ROOT/'compatible.lock.json').read_text());image=lock['image_id']
    info=json.loads(h.call(['image','inspect',image]).stdout)[0]
    assert info['Config']['Labels'].get(LABEL)=='true' and not info['Config'].get('Volumes') and not info['Config'].get('ExposedPorts')
    try:
        h.container='imagine-staging-e2e-'+h.run_id
        h.call(['create','--name',h.container,'--label',LABEL+'=true','--network','none','--no-healthcheck','--cap-drop','ALL','--security-opt','no-new-privileges','--pids-limit','256','--memory','1536m','--cpus','2','--log-driver','none','--pull','never',image,'sleep','infinity'])
        h.container_created=True
        def inspection(tag):
            v=json.loads(h.call(['inspect',h.container]).stdout)[0];validate_inspection(v)
            h.record(tag,'PASS',{'network':'none','ports':[],'mounts':[],'cap_drop':v['HostConfig']['CapDrop'],'no_new_privileges':True,'image_id':v['Image']})
        inspection('isolation_before_input')
        for name,path in [('inside.py',BASE/'inside.py'),('inside-commercial.py',ROOT/'inside-commercial.py'),('cases.php',ROOT/'cases.php'),('diagnostic.php',ROOT/'diagnostic.php'),('subject-adapter.json',BASE/'subject-adapter.json'),('worker-bridge.php',BASE/'worker-bridge.php')]:
            h.call(['cp',h.local_path(path),h.container+':/opt/e2e/'+name])
        for slug in ['woocommerce-memberships','woocommerce-subscriptions']:
            h.call(['cp','/home/ced/staging-wp/plugins/'+slug+'.zip',h.container+':/opt/e2e/'+slug+'.zip'])
        for n in SUBJECT_FILES:
            # Copy individual explicitly allowlisted subject files; no arbitrary tree.
            if '/' in n:h.call(['start',h.container]);h.call(['exec',h.container,'mkdir','-p','/subject/mu-plugins'])
            else:
                if n==SUBJECT_FILES[0]:h.call(['start',h.container]);h.call(['exec',h.container,'mkdir','-p','/subject'])
            h.call(['cp',h.local_path(subject/n),h.container+':/subject/'+n])
        assert {n:hashlib.sha256((subject/n).read_bytes()).hexdigest()for n in SUBJECT_FILES}==manifest
        p=h.call(['exec',h.container,'python3','/opt/e2e/inside-commercial.py'],check=False,timeout=1800)
        (h.evidence/'execution.log').write_text(p.stdout+p.stderr,encoding='utf8');print(p.stdout)
        h.call(['cp',h.container+':/report/commercial-result.json',h.local_path(h.evidence/'result.json')])
        h.call(['cp',h.container+':/opt/public/packages.tsv',h.local_path(h.evidence/'packages.tsv')])
        inspection('isolation_after_execution')
        result=json.loads((h.evidence/'result.json').read_text());assert result['exit_code']==p.returncode
        status=result['exit_code'];h.record('actual_result_readback','PASS',{'exit_code':status,'counts':dict(collections.Counter(c['status']for c in result['checks']))})
    finally:
        h.cleanup();h.write_journal()
        assert {n:hashlib.sha256((subject/n).read_bytes()).hexdigest()for n in SUBJECT_FILES}==manifest
        print('EVIDENCE='+str(h.evidence))
    return status
if __name__=='__main__':sys.exit(main())
