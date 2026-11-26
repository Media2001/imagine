"""Publication contract, exercised without PHP or WordPress."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
PATH = ROOT / 'wp/outils/bascule/a26/report.py'


def load():
    if not PATH.is_file():
        raise AssertionError('A26 closed publication validator is not implemented')
    spec = importlib.util.spec_from_file_location('a26_report', PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fixture(r):
    services = {k: 0 for k in r.SERVICES}
    return {'schema': 'imagine-a26-third-parties-v1', 'read_only': True, 'storage': 'classic',
            'neutralisation': 'observe', 'families': {k: {'active': 0, 'identifier': 'non'} for k in r.FAMILIES},
            'content': {'all': dict(services), 'selection': {'mode': 'annee', 'years': [], 'last_ten': None}},
            'audit_sha256': '0' * 64}


class ReportTests(unittest.TestCase):
    def test_nominal_closed_projection(self):
        r = load()
        self.assertTrue(r.projection(fixture(r), '0' * 64))


if __name__ == '__main__':
    unittest.main()
