"""C27 lecture seule finale : fichiers distants, aucun résidu, profils/commandes/actions exacts."""
import sys
sys.dont_write_bytecode=True
import hashlib,json,os
from pathlib import Path
import importlib.util
import c27
spec=importlib.util.spec_from_file_location('native',c27.ROOT/'wp/outils/demo/c27-native.py');native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
label,recipe=sys.argv[1:]
identity=c27.guard()
receipt=json.loads((c27.PROOF/(recipe+'.json')).read_text(encoding='utf-8'))
raw=(Path(os.environ['TMPDIR'])/receipt['private_snapshot']['file']).read_bytes()
assert hashlib.sha256(raw).hexdigest()==receipt['private_snapshot']['sha256']
saved=json.loads(raw)['payload']['database'];current=c27.snapshot()
exact=native.compare(saved,current);preserved={k:v for k,v in exact.items() if k!='options_metier'}
assert all(preserved.values())
data=c27.wp('$files=["mu-plugins/c27-observer.php","imagine-demo-build/c27-runtime.php"];$out=["configuration"=>Imagine\\Site\\Acquisition::configuration(),"answers"=>Imagine\\Site\\AcquisitionConfidentialite::lignes(),"seen"=>Imagine\\Site\\AcquisitionConfidentialite::lignes(null,true),"temporary_files"=>[]];foreach($files as $n){$out["temporary_files"][$n]=file_exists(WP_CONTENT_DIR."/".$n);}echo wp_json_encode($out);')
assert data['answers']==data['seen']==[] and all(v is False for v in data['temporary_files'].values())
hashes=c27.b09.b08.c25.b06.hashes(c27.NAMES)
assert hashes=={n:hashlib.sha256((c27.ROOT/'wp'/n).read_bytes()).hexdigest() for n in c27.NAMES}
assert c27.wp('echo wp_json_encode(file_get_contents(WP_CONTENT_DIR."/plugins/imagine-site/imagine-site.php"));')==(c27.ROOT/'wp/plugins/imagine-site/imagine-site.php').read_text(encoding='utf-8')
c27.save(label,{'identity':identity,'remote_hashes':hashes,'preserved_rows':preserved,'baseline_receipt':recipe+'.json',**data})
print('Readback C27 : code exact, aucun résidu ; profils, commandes et quatre tables Action Scheduler identiques à la préimage.')
