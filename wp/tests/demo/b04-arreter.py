"""Arrêt B04 bloqué : retirer uniquement le tracer-bullet, préimages contrôlées."""
from pathlib import Path
from datetime import datetime, timezone
import importlib.util
import base64
import json
import hashlib
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('b04_work_stop', HERE / 'b04-work.py')
work = importlib.util.module_from_spec(spec)
spec.loader.exec_module(work)
work.guard()
proof = work.PROOF
receipt = json.loads((proof / 'deploy-status.json').read_text())
before = json.loads((proof / 'theme-before-status.json').read_text())
observed = work.readback(list(receipt['expected']))
original_functions = hashlib.sha256(base64.b64decode(before['themes/imagine/functions.php'])).hexdigest()
assert all(observed[k] == v or (k == 'themes/imagine/functions.php' and observed[k] == original_functions) for k, v in receipt['expected'].items()), 'Dérive du thème : arrêt sans restauration'
key = 'themes/imagine/functions.php'
original = base64.b64decode(before[key])
assert (work.ROOT / 'wp' / key).read_bytes() == original
candidate = work.ROOT / 'wp/themes/imagine/inc/catalogue.php'
assert candidate.read_bytes() == (proof / 'catalogue-candidat.php').read_bytes()
work.c08.b00.upload(key, original)
assert work.readback([key])[key] == hashlib.sha256(original).hexdigest()
key2 = 'themes/imagine/inc/catalogue.php'
assert before[key2] is None
# wp-cli ne peut pas supprimer le fichier du volume ; même cible hôte que l'upload B00.
import subprocess
remote_code = ('from pathlib import Path;import hashlib;'
    'p=Path("/app/sites/imagine-test-demo/wp-content/themes/imagine/inc/catalogue.php");'
    'assert hashlib.sha256(p.read_bytes()).hexdigest()==' + repr(receipt['expected'][key2]) + ';p.unlink();assert not p.exists();print("B04_CANDIDATE_REMOVED")')
removed = subprocess.run(['wsl.exe','docker','exec','staging-wp-dashboard','python','-c',remote_code], capture_output=True,text=True,timeout=60)
assert removed.returncode == 0 and removed.stdout.strip() == 'B04_CANDIDATE_REMOVED'
candidate.unlink()
actual = work.readback(list(before))
expected = {k:hashlib.sha256(base64.b64decode(v)).hexdigest() if v is not None else None for k,v in before.items()}
assert actual == expected
result = {'at':datetime.now(timezone.utc).isoformat(),'scope':'imagine-test-demo','status':'BLOCKED_ROLLED_BACK','theme_restored_exact':True,'actual':actual,'expected':expected,'candidate_retained':str(proof/'catalogue-candidat.php'),'catalogue_blocker':'Aucun produit publié ; produit simple 271 privé, lié au numéro 11. Aucun objet ou droit fabriqué.'}
(proof / 'arret-verifie.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'status':result['status'],'theme_restored_exact':True}))
