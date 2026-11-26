"""C21: run current source on the existing offline test image."""
from pathlib import Path
import importlib.util, sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('c21_unit_runner', Path(__file__).with_name('c18-unit.py'))
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
runner.PROOF = ROOT / 'production/C-21'
if __name__ == '__main__':
    selected = sys.argv[2] if len(sys.argv) > 2 else 'ConfidentialiteReglesTest'
    sys.exit(runner.run(sys.argv[1] if len(sys.argv) > 1 else 'unit-final', '' if selected == '--root' else selected))
