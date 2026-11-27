"""B11 : lancer les commandes parentes inchangées et conserver leurs vrais codes."""
import sys
sys.dont_write_bytecode=True
import json
import subprocess
from pathlib import Path
import b11

def run(action,label):
    scripts={'image':'preparer-image.ps1','replay':'rejouer.ps1'}
    assert action in scripts
    log=b11.OUT/(label+'.log')
    assert not log.exists()
    cmd=['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(b11.ROOT/'wp/tests'/scripts[action])]
    with log.open('xb') as stream:
        p=subprocess.run(cmd,cwd=b11.ROOT,stdout=stream,stderr=subprocess.STDOUT)
    b11.save(label,{'action':action,'command':cmd,'exit':p.returncode,'log':log.name,'sources':b11.sources()})
    text=log.read_bytes().decode('utf-8','replace')
    print('\n'.join(text.splitlines()[-12:]))
    return p.returncode

if __name__=='__main__':raise SystemExit(run(*sys.argv[1:]))
