"""Portes C24 : préparation officielle et rejeu canonique, reçus immuables."""
import sys
sys.dont_write_bytecode=True
import subprocess,json,hashlib,re
import c24

def run(kind,label):
    scripts={'prepare':'wp/tests/preparer-image.ps1','regression':'wp/tests/rejouer.ps1'}
    script=scripts[kind];log=c24.PROOF/(label+'.log')
    assert label.endswith('-V2') and not log.exists() and not (c24.PROOF/(label+'.json')).exists()
    command=['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',script]
    p=subprocess.run(command,cwd=c24.ROOT,capture_output=True,encoding='utf-8',errors='replace')
    text=p.stdout+p.stderr
    log.write_text(text,encoding='utf-8')
    checks={'exit_zero':p.returncode==0}
    if kind=='prepare':checks['image_verifiee']='PREPARATION T01 : image verifiee sha256:' in text
    else:
        rows=[json.loads(s[len('T01_RESULT '):]) for s in text.splitlines() if s.startswith('T01_RESULT ')]
        checks['unique_bilan']=len(rows)==1
        if len(rows)==1:
            r=rows[0];checks['suite_verte']=r['pass'] is True and r['tests']>0 and all(r[k]==0 for k in ['failures','errors','skipped']) and r['tools']['failures']==0
        else:r=None
    data={'kind':kind,'command':command,'exit':p.returncode,'checks':checks,'failures':[k for k,v in checks.items() if not v],'log':log.name,'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256((c24.ROOT/script).read_bytes()).hexdigest()}
    if kind=='regression':data['result']=r
    c24.save(label,data)
    print(json.dumps(data,ensure_ascii=False));print(text[-1800:])
    assert not data['failures']

if __name__=='__main__':run(*sys.argv[1:])
