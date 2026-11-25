"""Exact-byte additive README regressions; all mutations are in memory."""
import importlib.util
from pathlib import Path
import sys
import unittest
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('a10_verifier_contract', HERE/'verifier.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class ReadmeContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.appendix = (v.REPO/'production/A-10/readme-ajout.txt').read_bytes()
        cls.current = (v.REPO/'wp/tests/a02-audit/README.md').read_bytes()
        cls.suffix = cls.appendix+v.INTEGRATION_APPENDIX
        cls.original = cls.current[:-len(cls.suffix)]

    def test_exact_integrated_bytes(self):
        self.assertEqual(v.readme_original_digest(self.current, self.appendix), v.A02_README_SHA256)

    def test_original_and_each_appended_byte_cannot_drift(self):
        # Every byte in the original and all authorized additions is protected.
        for position in range(len(self.current)):
            mutated = self.current[:position]+bytes([self.current[position] ^ 1])+self.current[position+1:]
            with self.subTest(position=position), self.assertRaises(RuntimeError):
                v.readme_original_digest(mutated, self.appendix)

    def test_omitted_duplicate_reordered_or_extra_appends_refused(self):
        lines = v.INTEGRATION_APPENDIX.splitlines(keepends=True)
        candidates = [self.original, self.original+self.appendix,
                      self.current+b'\n', self.current+b'Extra lot\n',
                      self.current+self.appendix, b'prefix\n'+self.current,
                      self.current.replace(b'\n', b'\r\n'),
                      self.original+self.appendix+b''.join(lines[1:]),
                      self.original+self.appendix+b''.join(lines[:1]+lines[3:]+lines[1:3]),
                      self.original+self.appendix+b''.join(lines[:3]+lines[:3]+lines[3:])]
        for candidate in candidates:
            with self.subTest(candidate_length=len(candidate)), self.assertRaises(RuntimeError):
                v.readme_original_digest(candidate, self.appendix)

    def test_modified_a10_appendix_contract_refused(self):
        with self.assertRaises(RuntimeError):
            v.readme_original_digest(self.current, self.appendix+b'\n')


if __name__ == '__main__':
    unittest.main(verbosity=2)
