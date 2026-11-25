"""B03 : rejeu B01/C08 local ; adaptation explicite du contrat pré-B03 sans JS."""
from pathlib import Path
import hashlib
import importlib.util
import io
import json
import sys
import types
import unittest
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PROOF = ROOT / 'production/B-03'
sys.path.insert(0, str(HERE))


def module(filename):
    spec = importlib.util.spec_from_file_location('b03_reg_' + filename.replace('-', '_'), HERE / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def execute(suite):
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    return {'tests': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
            'skipped': len(result.skipped), 'output': stream.getvalue()}


def run():
    source = HERE / 'test_b01_theme.py'
    original = module(source.name)
    before = execute(unittest.defaultTestLoader.loadTestsFromModule(original))
    text = source.read_text(encoding='utf-8')
    old = "self.assertFalse(list(THEME.rglob('*.js')))"
    new = "self.assertEqual(sorted(p.relative_to(THEME).as_posix() for p in THEME.rglob('*.js')), ['assets/reading.js'])"
    if text.count(old) != 1:
        raise RuntimeError('Le test historique a changé : adaptation B03 à relire')
    adapted = types.ModuleType('b03_b01_adapter')
    adapted.__file__ = str(source)
    exec(compile(text.replace(old, new), str(source) + ':adaptation-B03', 'exec'), adapted.__dict__)
    suite = unittest.defaultTestLoader.loadTestsFromModule(adapted)
    for name in ['b01-corrections.py', 'test_c08_scope.py', 'test_b03_contract.py']:
        suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module(name)))
    after = execute(suite)
    # Conserver le rouge historique, pas le cacher : son assertion est remplacée par une liste fermée.
    record = {'historical_source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'original_b01': before, 'adaptation': {'old': old, 'new': new, 'changes': 1}, 'current_contract': after}
    (PROOF / 'local-regression.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: {x:v for x,v in val.items() if x != 'output'} for k,val in [('original_b01',before),('current_contract',after)]}, ensure_ascii=False))
    if after['failures'] or after['errors'] or after['skipped']:
        raise SystemExit(1)


if __name__ == '__main__':
    run()
