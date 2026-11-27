"""A33 read-only packet verifier; no arguments, no writes or subprocess."""
import importlib.util
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
root = Path(__file__).resolve().parents[2]
try:
    if len(sys.argv) != 1:
        raise ValueError('A33_ARGUMENTS_REFUSED')
    spec = importlib.util.spec_from_file_location('a33packet', root / 'wp/tests/a33/delivery.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    code = module.verify(root)
except Exception as error:
    code = str(error) if str(error) == 'A33_ARGUMENTS_REFUSED' else 'A33_PACKET_INVALID'
result = {'lot': 'A-33', 'exit_code': int(code is not None), 'checks': [{'check': code or 'A33_PACKAGE_PASS', 'status': 'FAIL' if code else 'PASS'}]}
print(json.dumps(result, ensure_ascii=True))
sys.exit(result['exit_code'])
