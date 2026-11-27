"""Préparation prescrite et suite imagine-site entière, sans rejouer/resceller les paquets."""
import sys
sys.dont_write_bytecode = True
import subprocess
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PROOF = ROOT/'production/B-07'


def run(kind):
    assert kind in ['prepare', 'suite']
    path=PROOF/('antislash-'+kind+'.log')
    receipt=path.with_suffix('.json')
    assert not path.exists() and not receipt.exists()
    if kind=='prepare':
        cmd=['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File','wp/tests/preparer-image.ps1']
    else:
        code='''define('STDOUT',fopen('php://stdout','w'));define('STDERR',fopen('php://stderr','w'));define('T01_FUNCTIONS_ONLY',true);require '/repo/wp/tests/t01/executer.php';
foreach(discoverT01Packages('/repo/wp')['packages'] as $p){$dest='/tmp/t01/'.$p['relative'];copyTree('/repo/wp/'.$p['relative'],$dest);copyTree('/opt/t01/'.$p['cacheKey'].'/vendor',$dest.'/vendor');}
$dest='/tmp/t01/plugins/imagine-site';verifyCoverage($dest);
$cmd=['php','vendor/bin/phpunit','--configuration','phpunit.xml','--do-not-cache-result','--fail-on-warning','--fail-on-risky','--fail-on-deprecation','--fail-on-skipped','--fail-on-incomplete','--log-junit','/tmp/b07-suite.xml'];
$p=proc_open($cmd,[0=>['file','/dev/null','r'],1=>STDOUT,2=>STDERR],$pipes,$dest);$exit=proc_close($p);echo "B07 JUNIT BEGIN\\n",file_get_contents('/tmp/b07-suite.xml'),"B07 JUNIT END\\n";exit($exit);'''
        cmd=['wsl.exe','-d','Ubuntu','--','docker','run','-i','--rm','--pull','never','--network','none','--read-only','--user','65534:65534','--cap-drop','ALL','--security-opt','no-new-privileges','--mount','type=bind,source=/mnt/c/Users/Ced/imagine/wp,target=/repo/wp,readonly','--tmpfs','/tmp:rw,nosuid,nodev,size=512m,mode=1777','--entrypoint','php','imagine-tests-t01:1']
    stdin = '<?php\n' + code if kind == 'suite' else None
    result=subprocess.run(cmd,input=stdin,capture_output=True,encoding='utf-8',errors='replace',timeout=300)
    path.write_text(result.stdout+result.stderr,encoding='utf-8')
    files=['wp/plugins/imagine-site/Agenda.php','wp/plugins/imagine-site/tests/AgendaAdapterTest.php','wp/plugins/imagine-site/tests/AgendaWPStubs.php','wp/outils/demo/b07-antislash-gates.py']
    receipt.write_text(json.dumps({'command':cmd,'stdin':stdin,'exit':result.returncode,'log':path.name,'log_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'sources':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files}},ensure_ascii=False,indent=2),encoding='utf-8')
    print(result.stdout[:2000] if kind=='suite' else result.stdout[-1800:])
    print('exit',result.returncode)
    return result.returncode


if __name__=='__main__':
    raise SystemExit(run(sys.argv[1]))
