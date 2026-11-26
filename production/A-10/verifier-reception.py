"""A10-only reception: current packaging and immutable native evidence.

Other lots and their mutable documentation are not A10 acceptance criteria.
The delegated verifier checks only A10's two exact shared README lines.
"""
import os
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]

if __name__ == '__main__':
    result = subprocess.run(
        [sys.executable, '-B', 'wp/tests/a10/verifier.py'], cwd=ROOT,
        env={**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1',
             'PYTHONDONTWRITEBYTECODE': '1'},
        capture_output=True, text=True, encoding='utf-8', timeout=180,
    )
    # The child emits ASCII JSON; the host console may remain cp1252.
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    sys.exit(result.returncode)