"""Read-only candidate verification; never claims production readiness."""
import argparse
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from delivery import local_valid


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--evidence', required=True, type=Path)
    a = ap.parse_args()
    try:
        valid = local_valid(a.evidence.resolve())
    except Exception:
        valid = False
    result = {'lot': 'A-32', 'scope': 'local_matrix_only', 'readiness_claimed': False,
              'exit_code': int(not valid), 'checks': [{'check': 'A32_LOCAL_MATRIX', 'status': 'PASS' if valid else 'FAIL'}]}
    print(json.dumps(result))
    return result['exit_code']


if __name__ == '__main__':
    sys.exit(main())
