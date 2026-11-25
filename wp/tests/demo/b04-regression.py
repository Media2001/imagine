"""Selected read-only non-regressions; never replay C09/C14/C15 mutating fixtures."""
from pathlib import Path
import importlib.util
import io
import json
import sys
import unittest
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
def module(name):
    s=importlib.util.spec_from_file_location('b04_reg_'+name.replace('-','_'),HERE/name)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
w=module('b04-work.py');w.guard()
b03=module('b03-http.py');b03.PROOF=w.PROOF
http=b03.run('regression-b03')
source=HERE/'b03-runtime.php';target='imagine-demo-build/b04-regression-b03.php'
w.c08.b00.upload(target,source.read_bytes())
assert w.readback([target])[target]==w.digest(source)
runtime=w.wp('require WP_CONTENT_DIR . "/'+target+'";')
stream=io.StringIO();suite=unittest.TestSuite()
for name in ['test_b03_contract.py','test_c08_scope.py']:
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module(name)))
r=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
result={'scope':'imagine-test-demo','B03_HTTP':{'total':http['total'],'failures':http['failures']},'B03_PHP':runtime,
    'local_contracts':{'total':r.testsRun,'failures':len(r.failures),'errors':len(r.errors),'skipped':len(r.skipped),'output':stream.getvalue()}}
(w.PROOF/'regressions.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='local_contracts'},ensure_ascii=False))
print(json.dumps({k:v for k,v in result['local_contracts'].items() if k!='output'}))
if http['failures'] or runtime['failures'] or not r.wasSuccessful() or r.skipped:raise SystemExit(1)
