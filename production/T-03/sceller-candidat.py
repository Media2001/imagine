"""Seal ONLY the current T03 pre-PRET correction candidate through its reader.

No PRET, no neighbouring seal, no global-gate approval. Failed verification
restores the previous manifest byte for byte; never edit digest values by hand.
"""
from datetime import datetime
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
BASE = Path(__file__).resolve().parent


def seal():
    if len(sys.argv) != 1 or (BASE / 'PRET').exists():
        raise ValueError('BEFORE_PRET_ONLY')
    spec = importlib.util.spec_from_file_location('t03_reader', BASE / 'verify-corrections.py')
    reader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reader)
    spec = importlib.util.spec_from_file_location('t03_qualification', BASE / 'qualifier-corrections.py')
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    files = reader.inventory(helper.source_hashes())
    manifest = {'lot': 'T-03', 'status': 'CORRECTIONS_TESTEES_GATES_PARENT_EN_ATTENTE',
                'readiness_claimed': False, 'parent_final_gates_pending': True,
                'at': datetime.now().astimezone().isoformat(),
                'verifier_scope': 'BEFORE_PRET_ONLY_CORRECTION_TESTS_NOT_GLOBAL_GATES',
                'files': files, 'file_count': len(files)}
    target = BASE / 'manifest.json'
    previous = target.read_bytes() if target.exists() else None
    try:
        target.write_text(json.dumps(manifest, indent=2, ensure_ascii=True) + '\n', encoding='utf-8')
        return reader.verify()
    except Exception:
        if previous is None:
            target.unlink(missing_ok=True)
        else:
            target.write_bytes(previous)
        raise


if __name__ == '__main__':
    try:
        result = seal()
    except Exception as error:
        result = {'lot': 'T-03', 'status': 'FAIL', 'exit_code': 1,
                  'readiness_claimed': False,
                  'code': str(error) if isinstance(error, ValueError) else 'PACKET_INVALID'}
    print(json.dumps(result, ensure_ascii=True))
    raise SystemExit(result['exit_code'])
