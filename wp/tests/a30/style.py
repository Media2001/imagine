"""Reuse the accepted offline style harness on A30-owned PHP files only."""
import importlib.util
from pathlib import Path
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location('a30_style_base', ROOT / 'wp/tests/a20/style.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
spec = importlib.util.spec_from_file_location('a30_style_runner', HERE / 'run.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
runner.DEPENDENCIES = runner.DEPS
base.r = runner
base.HERE = HERE
base.LOT = 'a30'
if __name__ == '__main__':
    sys.exit(base.main())
