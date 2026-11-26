"""C17 real HTTP acceptance on imagine-test-demo only. RED test retained."""
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
    from c17_http import run
    sys.exit(run(sys.argv[1] if len(sys.argv)>1 else 'http-final'))
