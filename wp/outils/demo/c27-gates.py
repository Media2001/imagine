"""Portes canoniques inchangées ; sorties et reçus C27 seulement."""
import sys
sys.dont_write_bytecode=True
import hashlib,json,subprocess
import c27
kind,label=sys.argv[1:]
script={'prepare':'wp/tests/preparer-image.ps1','regression':'wp/tests/rejouer.ps1'}[kind]
path=c27.PROOF/(label+'.log');assert not path.exists()
command=['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',script]
p=subprocess.run(command,cwd=c27.ROOT,capture_output=True,encoding='utf-8',errors='replace')
text=p.stdout+p.stderr;path.write_text(text,encoding='utf-8')
results=[json.loads(line[11:]) for line in text.splitlines() if line.startswith('T01_RESULT ')]
c27.save(label,{'command':command,'exit':p.returncode,'log':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'results':results})
print(text[-6500:]);print('EXIT',p.returncode)
if kind=='prepare':assert p.returncode==0
# Les quatre paquets annexes voie1 déjà rouges sont nommés, jamais ouverts ou réparés ici.
