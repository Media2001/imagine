"""T03 no-argument adapter: unchanged current verifier, unique current packet."""
import os
from pathlib import Path
import subprocess
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
if len(sys.argv) != 1:
    print('{"exit_code":1,"code":"NO_ARGUMENTS"}')
    raise SystemExit(1)
raise SystemExit(subprocess.run([sys.executable, '-B', str(ROOT / 'wp/tests/a21/verify.py'), *['production/A-21/preuves/final']],
    cwd=ROOT, env={**os.environ, 'PYTHONDONTWRITEBYTECODE':'1', 'PYTHONIOENCODING':'utf-8', 'PYTHONUTF8':'1'}).returncode)
