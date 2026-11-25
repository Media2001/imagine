"""C17 real HTTP acceptance on imagine-test-demo only."""
from pathlib import Path
import importlib.util
import sys
import json
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'outils/demo'))
import profils
spec=importlib.util.spec_from_file_location('c17_http_transport',Path(__file__).with_name('c12-http.py'))
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
if __name__=='__main__':
    profils.guard('imagine-test-demo')
    accounts=json.loads((Path.home()/'.imagine-demo/identifiants.json').read_text(encoding='utf-8'))['c09_accounts']
    status,_,page=h.fetch('/mon-compte/',h.login(accounts['P-SOL-ATT']))
    result={'checks':{'depot_natif_B02':status==200 and 'data-imagine-justificatif' in page}}
    target=profils.b00.ROOT/'production/C-17/http-red.json'
    target.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result));sys.exit(0 if all(result['checks'].values()) else 1)
