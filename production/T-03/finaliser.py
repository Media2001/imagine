"""Finalize T03 only after checked correction, native and closure gates.

Never edits shared code or a neighbouring seal. Roll back manifest and PRET on
any failure. All digests are computed from current bytes, never supplied by hand.
"""
from datetime import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
BASE = Path(__file__).resolve().parent


def finalise():
    if len(sys.argv) != 1 or (BASE / 'PRET').exists():
        raise ValueError('BEFORE_PRET_ONLY')
    spec = importlib.util.spec_from_file_location('t03_final_reader', BASE / 'verify-final.py')
    reader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reader)
    candidate = reader.load('t03_candidate_preseal', 'verify-corrections.py')
    candidate.verify()
    reader.verify_gates()
    helper = reader.load('t03_qualification_preseal', 'qualifier-corrections.py')
    files = candidate.inventory(helper.source_hashes())
    manifest = {'lot': 'T-03', 'status': 'PRET', 'readiness_claimed': True,
                'parent_final_gates_pending': False,
                'at': datetime.now().astimezone().isoformat(),
                'verifier_scope': 'FINAL_STATE_READ_ONLY',
                'pret_sha256': hashlib.sha256(reader.PRET_BYTES).hexdigest(),
                'independent_post_pret_receipt': 'C:/Users/Ced/AppData/Local/hermes/cache/scratch/t03-final-20261127-postPRET/reception.json',
                'files': files, 'file_count': len(files)}
    target = BASE / 'manifest.json'
    before = target.read_bytes()
    try:
        target.write_text(json.dumps(manifest, indent=2, ensure_ascii=True) + '\n', encoding='utf-8')
        reader.verify(require_pret=False)
        (BASE / 'PRET').write_bytes(reader.PRET_BYTES)
        return reader.verify()
    except Exception:
        (BASE / 'PRET').unlink(missing_ok=True)
        target.write_bytes(before)
        raise


if __name__ == '__main__':
    try:
        result = finalise()
    except Exception as error:
        result = {'lot': 'T-03', 'status': 'FAIL', 'exit_code': 1,
                  'code': str(error) if isinstance(error, ValueError) else 'FINAL_GATES_INVALID'}
    print(json.dumps(result, ensure_ascii=True))
    raise SystemExit(result['exit_code'])
