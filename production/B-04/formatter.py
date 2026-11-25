from pathlib import Path
import base64
import difflib
import importlib.util
import json
import subprocess
import sys
import uuid
sys.dont_write_bytecode=True
root=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('bench',root/'wp/outils/demo/c11-unit.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
docker=b.docker
files=['wp/plugins/imagine-site/Paywall.php','wp/plugins/imagine-site/Decouverte.php','wp/themes/imagine/inc/catalogue.php']
name='imagine-b04-format-'+uuid.uuid4().hex
try:
    docker('create','--name',name,'--network','none','--read-only','--tmpfs','/tmp:rw,nosuid,nodev,size=64m,mode=1777',
        '--user','65534:65534','--cap-drop','ALL','--security-opt','no-new-privileges',
        '--mount','type=bind,src=/mnt/c/Users/Ced/imagine,dst=/repo,readonly',
        '--entrypoint','sleep','imagine-tests-t01:1','120')
    docker('start',name)
    for f in files: docker('exec',name,'cp','/repo/'+f,'/tmp/'+Path(f).name)
    result=docker('exec',name,'php','/opt/t01/imagine-site/vendor/bin/phpcbf','--standard=PSR12','-n',*[('/tmp/'+Path(f).name) for f in files],check=False)
    print(result.stdout)
    php='<?php $o=[];foreach('+str([Path(f).name for f in files]).replace("'",'"')+' as $f){$o[$f]=base64_encode(file_get_contents("/tmp/".$f));}echo json_encode($o);'
    r=subprocess.run(['wsl.exe','docker','exec','-i',name,'php'],input=php,capture_output=True,text=True,check=True)
    data=json.loads(r.stdout)
    out={}
    for f in files:
        old=(root/f).read_text(encoding='utf-8')
        new=base64.b64decode(data[Path(f).name]).decode()
        assert ''.join(old.split())==''.join(new.split()), 'Formatter must only change whitespace'
        out[f]=new
        print(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=f,tofile=f)))
    (root/'production/B-04/formatting-proposal.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
finally:
    docker('rm','-f',name)
    absent=docker('inspect',name,check=False)
    assert absent.returncode and 'no such' in (absent.stdout+absent.stderr).lower()
