"""T02 packet-verifier regressions; only synthetic scratch copies are changed."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
SCRATCH = Path('C:/Users/Ced/AppData/Local/hermes/cache/scratch/imagine-t02-correction')
spec = importlib.util.spec_from_file_location('t02_packet', ROOT / 'production/T-02/verifier.py')
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


class PacketTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='packet-test-', dir=SCRATCH)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifest = json.loads((ROOT / 'production/T-02/manifest.json').read_text(encoding='utf-8'))
        for name in list(self.manifest['files']) + ['production/T-02/manifest.json', 'production/T-01/notes.md']:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)

    def reseal_outer(self):
        for name in self.manifest['files']:
            self.manifest['files'][name] = hashlib.sha256((self.root / name).read_bytes()).hexdigest()
        (self.root / 'production/T-02/manifest.json').write_text(json.dumps(self.manifest), encoding='utf-8')

    def test_current_packet_without_readiness_is_valid(self):
        self.assertTrue(verifier.verify(self.root)['verified'])
        self.assertFalse(verifier.verify(self.root)['parent_gates_claimed'])

    def test_parent_pret_does_not_invalidate_candidate_packet(self):
        (self.root / 'production/T-02/PRET').write_text('Synthetic parent marker, no actual gate claimed.\n', encoding='utf-8')
        self.assertTrue(verifier.verify(self.root)['verified'])

    def test_source_mutation_is_rejected(self):
        with (self.root / 'wp/tests/t01/tools.php').open('ab') as stream:
            stream.write(b'\n// synthetic tampering\n')
        with self.assertRaisesRegex(ValueError, 'Manifest hash differs'):
            verifier.verify(self.root)

    def test_journal_mutation_is_rejected(self):
        with (self.root / 'production/T-02/preuves/final/utf8/rejeu.log').open('ab') as stream:
            stream.write(b'\nsynthetic tampering\n')
        with self.assertRaisesRegex(ValueError, 'Manifest hash differs'):
            verifier.verify(self.root)

    def test_stale_internal_output_hash_is_rejected_after_outer_reseal(self):
        path = self.root / 'production/T-02/preuves/final/cp1252/verification.json'
        receipt = json.loads(path.read_text(encoding='utf-8'))
        receipt['commands']['rejeu']['output_sha256'] = '0' * 64
        path.write_text(json.dumps(receipt), encoding='utf-8')
        self.reseal_outer()
        with self.assertRaisesRegex(ValueError, 'Receipt/log hash differs: cp1252/rejeu'):
            verifier.verify(self.root)

    def test_unrelated_shared_documentation_appendix_is_allowed(self):
        with (self.root / 'production/T-01/notes.md').open('a', encoding='utf-8') as stream:
            stream.write('\nSynthetic unrelated appendix.\n')
        self.assertTrue(verifier.verify(self.root)['verified'])

    def test_owned_shared_documentation_line_is_required(self):
        path = self.root / 'production/T-01/notes.md'
        path.write_text('\n'.join(line for line in path.read_text(encoding='utf-8').splitlines()
                                  if not line.startswith('- T-02 :')), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'T01 owned documentation line differs'):
            verifier.verify(self.root)


if __name__ == '__main__':
    unittest.main(verbosity=2)
