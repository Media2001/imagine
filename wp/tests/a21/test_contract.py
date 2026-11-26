"""Shared documentation contract, Python-only and portable."""
from pathlib import Path
import unittest
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
class ContractTest(unittest.TestCase):
    def test_current_two_lines_exactly_once(self):
        self.assertTrue((HERE/'verify.py').is_file(), 'A21 verifier missing')
        from verify import readme_contract
        appendix=(ROOT/'production/A-21/readme-ajout.txt').read_bytes()
        self.assertTrue(readme_contract((ROOT/'wp/tests/a02-audit/README.md').read_bytes(),appendix))
    def test_adversarial_shared_document_contract(self):
        self.assertTrue((HERE/'verify.py').is_file(), 'A21 verifier missing')
        from verify import readme_contract
        appendix=b'first\nsecond\n'
        self.assertTrue(readme_contract(b'other\n'+appendix+b'unrelated A20\n',appendix))
        for bad in [b'first\n',b'first changed\nsecond\n',appendix+appendix,b'first\r\nsecond\n']:
            self.assertFalse(readme_contract(bad,appendix))
if __name__=='__main__':
    unittest.main()
