"""C22 PSR12 bloquant et lint PHP ; conteneur jetable sans réseau, sources RO."""
from pathlib import Path
import json, subprocess, sys
ROOT=Path(__file__).resolve().parents[3]
PROOF=ROOT/'production/C-22'
FILES=['Newsletters.php','NewslettersRegles.php','NewslettersReglages.php','tests/NewslettersReglesTest.php']

def run(label):
    path=PROOF/(label+'.json')
    assert not path.exists()
    args=['wsl.exe','-d','Ubuntu','--','docker','run','--rm','--network','none','--read-only','--user','65534:65534','--cap-drop','ALL','--security-opt','no-new-privileges','--tmpfs','/tmp:rw,nosuid,nodev,size=64m,mode=1777','--mount','type=bind,source=/mnt/c/Users/Ced/imagine/wp,target=/repo/wp,readonly','--entrypoint','php','imagine-tests-t01:1','/opt/t01/imagine-site/vendor/bin/phpcs','--standard=PSR12','--report=json','-n']
    args+=['/repo/wp/plugins/imagine-site/'+n for n in FILES]
    p=subprocess.run(args,capture_output=True,text=True,encoding='utf-8')
    data={'exit':p.returncode,'stderr':p.stderr,'report':json.loads(p.stdout),'command':args,'soft_line_length_warnings_excluded':True}
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(data['report']['totals']))
    assert p.returncode==0 and data['report']['totals']['errors']==0

if __name__=='__main__':run(sys.argv[1])
