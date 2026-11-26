"""A13 parsing reuse and no values in public diagnostics."""
import importlib.util
import importlib.machinery
import json
from pathlib import Path
import tempfile
import unittest

class InputTest(unittest.TestCase):
    def test_reader_uses_mapping_and_preserves_physical_line(self):
        source=Path('/subject/a14/main.py')
        self.assertTrue(source.is_file(), 'A14 reader missing')
        spec=importlib.util.spec_from_file_location('contacts_input',source)
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        with tempfile.TemporaryDirectory(dir='/report') as d:
            p=Path(d); config={'version':1,'encodage':'auto','separateur':';','colonnes':{'email':'Courriel','statut':'Statut'},'statuts':{'inscrit':['oui'],'desinscrit':['non'],'bloque':['stop']}}
            (p/'mapping.json').write_text(json.dumps(config))
            (p/'input.csv').write_text('Courriel;Statut;Autre\n"SAME @example.org";non;"deux\nlignes"\nsecond@example.org;stop;x\n')
            rows=m.read_contacts(p/'input.csv',p/'mapping.json')
            self.assertEqual([r['line'] for r in rows],[2,4])
            self.assertEqual([r['status'] for r in rows],['desinscrit','bloque'])
            config['statuts']['bloque']=['oui'];(p/'mapping.json').write_text(json.dumps(config))
            with self.assertRaisesRegex(RuntimeError,'A14_MAPPING_INVALID'):
                m.read_contacts(p/'input.csv',p/'mapping.json')

if __name__=='__main__':unittest.main()
