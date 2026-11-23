"""Prove the regression test kills the old cardinality-only oracle, without editing sources."""
import sys, unittest, importlib.util, io, json
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'wp/tests/demo'))
import b01_expectations
spec=importlib.util.spec_from_file_location('b01_corrections',ROOT/'wp/tests/demo/b01-corrections.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
stream=io.StringIO()
with patch.object(b01_expectations,'home_matches',lambda actual,expected:len(actual)==5):
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.TestSuite([module.Corrections('test_home_exact_fixture_ids_and_order_reject_intruder_and_permutation')]))
proof={'mutant':'cardinality only: len(actual) == 5','tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'killed':len(result.failures)==1 and not result.errors,'output':stream.getvalue()}
(ROOT/'production/B-01/tests/oracle-cardinality-mutant.json').write_text(json.dumps(proof,indent=2),encoding='utf-8')
print(json.dumps(proof,indent=2));assert proof['killed']
