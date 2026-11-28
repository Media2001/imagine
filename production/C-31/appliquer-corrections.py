"""Déploiement borné aux trois classes C31, jamais au bootstrap partagé."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'wp/outils/demo'))
import c31 as o
import b13
import b06
name = sys.argv[1]
identity = o.guard()
old = b06.hashes(o.FILES)
known = json.loads((o.OUT / 'installation-V2.json').read_text(encoding='utf-8'))['readback']
local = {n: hashlib.sha256((ROOT / 'wp' / n).read_bytes()).hexdigest() for n in o.FILES}
assert all(old[n] in [known[n], local[n]] for n in o.FILES), 'Dérive distante C31'
boot = b06.hashes(['plugins/imagine-site/imagine-site.php'])
before = b13.c29.state()
private = b13.b11.private(name, {'files': o.wp('$out=[];foreach(' + o.php(o.FILES) + ' as $n){$out[$n]=file_get_contents(WP_CONTENT_DIR."/".$n);}echo wp_json_encode($out);')})
for n in o.FILES:
    b13.b11.upload(n, (ROOT / 'wp' / n).read_bytes())
actual = b06.hashes(o.FILES)
assert actual == local
assert b06.hashes(['plugins/imagine-site/imagine-site.php']) == boot
assert b13.c29.state() == before
b13.save(o, name, {'identity': identity, 'before': old, 'readback': actual, 'bootstrap_unchanged': boot, 'business_preserved': True, 'private_snapshot': private})
print(json.dumps({'readback': actual, 'bootstrap_unchanged': True, 'business_preserved': True}))
