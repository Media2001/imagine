"""Mandatory real T01 image preparation receipt, no source changes."""
import datetime
import hashlib
import json
import pathlib
import subprocess
ROOT=pathlib.Path(__file__).resolve().parents[3]
OUT=ROOT/'production/A-10/preparation'
OUT.mkdir(parents=True,exist_ok=True)
command=['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'wp/tests/preparer-image.ps1')]
p=subprocess.run(command,capture_output=True,text=True,encoding='utf8',errors='replace',timeout=1800)
log=p.stdout+p.stderr
(OUT/'preparer-image.log').write_text(log,encoding='utf8')
receipt={'command':command,'exit_code':p.returncode,'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'script_sha256':hashlib.sha256((ROOT/'wp/tests/preparer-image.ps1').read_bytes()).hexdigest(),'log_sha256':hashlib.sha256((OUT/'preparer-image.log').read_bytes()).hexdigest()}
(OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
raise SystemExit(p.returncode)
