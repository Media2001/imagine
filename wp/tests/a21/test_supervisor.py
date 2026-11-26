"""Supervisor report boundary tests use disposable files and no host PHP."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('a21_supervisor',ROOT/'wp/outils/bascule/a21/confine.py')
supervisor=importlib.util.module_from_spec(spec)
spec.loader.exec_module(supervisor)

class SupervisorTest(unittest.TestCase):
    def test_duplicate_json_cannot_smuggle_hidden_text(self):
        packet=ROOT/'production/A-21/preuves/final'
        source=packet/'classic-portes'
        with tempfile.TemporaryDirectory(prefix='a21-supervisor-test-',dir=os.environ.get('TMPDIR')) as directory:
            output=Path(directory)/'output'
            output.mkdir()
            raw=(source/'portes.json').read_bytes()
            markdown=(source/'portes.md').read_bytes()
            for name,data in [('portes.json',raw),('portes.md',markdown)]:
                (output/name).write_bytes(data)
            self.assertTrue(supervisor.complete_report(output,packet/'classic-audit/audit.json'))
            attack=b'"schema": "A21_HIDDEN_CANARY", "schema":'
            (output/'portes.json').write_bytes(raw.replace(b'"schema":',attack,1))
            (output/'portes.md').write_bytes(markdown.replace(b'"schema":',attack,1))
            self.assertFalse(supervisor.complete_report(output,packet/'classic-audit/audit.json'))

    def test_empty_native_topic_array_is_public_but_untrusted_text_is_not(self):
        packet=ROOT/'production/A-21/preuves/final'
        data=json.loads((packet/'classic-portes/portes.json').read_text(encoding='utf-8'))
        data['webhooks']['counts']['by_topic']=[]
        self.assertTrue(supervisor.public_projection(data))
        data['basis']['store']='A21_HIDDEN_CANARY'
        self.assertFalse(supervisor.public_projection(data))
        data['basis'].pop('store')
        self.assertFalse(supervisor.public_projection(data))

if __name__=='__main__':
    unittest.main()
