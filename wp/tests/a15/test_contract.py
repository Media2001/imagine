"""A15 owns exactly two shared documentation lines, not other lots."""
import importlib.util
from pathlib import Path
import sys
import unittest
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('a15verify',Path(__file__).with_name('verify.py'))
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)

class ContractTest(unittest.TestCase):
    def test_later_and_earlier_lots_are_independent(self):
        self.assertTrue(v.doc_contract(b'Un autre lot\n'+v.APPENDIX+b'Lot suivant\n'))
    def test_own_lines_exact_once(self):
        self.assertTrue(v.doc_contract(v.APPENDIX))
        for doc in [v.APPENDIX[:-1],v.APPENDIX+v.APPENDIX,v.APPENDIX.replace(b'A-15',b'A-XX'),v.APPENDIX.splitlines(keepends=True)[0]]:
            with self.subTest(doc=doc):self.assertFalse(v.doc_contract(doc))
if __name__=='__main__':unittest.main()
