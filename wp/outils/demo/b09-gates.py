"""Portes canoniques inchangées, reçus uniquement dans B09."""
import sys
sys.dont_write_bytecode=True
import hashlib
import json
import subprocess
import b09
kind,label=sys.argv[1:]
script={'prepare':'wp/tests/preparer-image.ps1','regression':'wp/tests/rejouer.ps1'}[kind]
path=b09.PROOF/(label+'.log')
assert not path.exists()
cmd=['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',script]
p=subprocess.run(cmd,cwd=b09.ROOT,capture_output=True,encoding='utf-8',errors='replace')
text=p.stdout+p.stderr
path.write_text(text,encoding='utf-8')
results=[json.loads(line[11:]) for line in text.splitlines() if line.startswith('T01_RESULT ')]
b09.save(label,{'command':cmd,'python':sys.version,'exit':p.returncode,'log':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'results':results})
print(text[-6500:])
assert p.returncode==0
