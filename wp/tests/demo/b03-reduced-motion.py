"""Amendement B03 de 19h30 : un seul CSS, préimage et relecture exactes."""
from pathlib import Path
from datetime import datetime, timezone
import importlib.util
import json
import hashlib
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('b03_work_amendment', HERE / 'b03-work.py')
work = importlib.util.module_from_spec(spec)
spec.loader.exec_module(work)
work.guard()
key = 'themes/imagine/assets/reading.css'
proof = work.PROOF
before = work.wp('$p=WP_CONTENT_DIR . "/' + key + '";echo wp_json_encode(["sha256"=>hash_file("sha256",$p),"base64"=>base64_encode(file_get_contents($p))]);')
previous = json.loads((proof / 'deploy-corrections.json').read_text())['expected'][key]
assert before['sha256'] == previous, 'CSS distant modifié depuis les corrections'
(proof / 'theme-before-reduced-motion.json').write_text(json.dumps(before, indent=2), encoding='utf-8')
data = (work.ROOT / 'wp' / key).read_bytes()
assert b'prefers-reduced-motion' not in data
work.c08.b00.upload(key, data)
expected = {key: hashlib.sha256(data).hexdigest()}
actual = work.readback([key])
assert actual == expected
receipt = {'at': datetime.now(timezone.utc).isoformat(), 'scope':'imagine-test-demo', 'before':{key:before['sha256']},'expected':expected,'actual':actual,'exact':actual == expected,'files':1}
(proof / 'deploy-reduced-motion.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
print(json.dumps(receipt))
