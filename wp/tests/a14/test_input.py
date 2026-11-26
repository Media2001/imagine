"""A13 parsing reuse and no values in public diagnostics."""
import importlib.util
import importlib.machinery
import json
from pathlib import Path
import tempfile
import unittest
import os
import subprocess
import sys
sys.dont_write_bytecode=True
SOURCE=Path(__file__).resolve().parents[2]/'outils/bascule/a14/main.py'
if not SOURCE.is_file():SOURCE=Path('/checkout/wp/outils/bascule/a14/main.py')
TEMP=Path('/report') if Path('/report').is_dir() else Path(os.environ['TMPDIR'])

class InputTest(unittest.TestCase):
    def test_reader_uses_mapping_and_preserves_physical_line(self):
        source=SOURCE
        self.assertTrue(source.is_file(), 'A14 reader missing')
        spec=importlib.util.spec_from_file_location('contacts_input',source)
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        with tempfile.TemporaryDirectory(dir=TEMP) as d:
            p=Path(d); config={'version':1,'encodage':'auto','separateur':';','colonnes':{'email':'Courriel','statut':'Statut'},'statuts':{'inscrit':['oui'],'desinscrit':['non'],'bloque':['stop']}}
            (p/'mapping.json').write_text(json.dumps(config),encoding='utf-8')
            (p/'input.csv').write_text('Courriel;Statut;Autre\n"SAME @example.org";non;"deux\nlignes"\nsecond@example.org;stop;x\n',encoding='utf-8')
            rows=m.read_contacts(p/'input.csv',p/'mapping.json')
            self.assertEqual([r['line'] for r in rows],[2,4])
            self.assertEqual([r['status'] for r in rows],['desinscrit','bloque'])
            config['statuts']['bloque']=['oui'];(p/'mapping.json').write_text(json.dumps(config),encoding='utf-8')
            with self.assertRaisesRegex(RuntimeError,'A14_MAPPING_INVALID'):
                m.read_contacts(p/'input.csv',p/'mapping.json')

    def test_refusals_and_decoders(self):
        spec=importlib.util.spec_from_file_location('contacts_input',SOURCE)
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        with tempfile.TemporaryDirectory(dir=TEMP) as d:
            p=Path(d); config={'version':1,'encodage':'auto','separateur':'auto','colonnes':{'email':'Courriel','statut':'Statut'},'statuts':{'inscrit':['oui'],'desinscrit':['non'],'bloque':['stop']}}
            sample='Courriel;Statut\nfiction@example.org;inattendu\n'
            for encoding in ['utf-8-sig','utf-16']:
                with self.subTest(encoding=encoding):
                    (p/'mapping.json').write_text(json.dumps(config),encoding='utf-8');(p/'input.csv').write_bytes(sample.encode(encoding))
                    self.assertEqual(m.read_contacts(p/'input.csv',p/'mapping.json')[0]['status'],'inconnu')
            for text in ['Courriel;Statut\nfiction@example.org;oui;extra\n','Courriel;Statut\n"broken;oui\n','Courriel;IBAN;Statut\nfiction@example.org;x;oui\n','Courriel;Statut\nfiction@example.org;oui\n\n']:
                with self.subTest(refusal=text[:20]):
                    (p/'input.csv').write_text(text,encoding='utf-8')
                    with self.assertRaises(RuntimeError):m.read_contacts(p/'input.csv',p/'mapping.json')
            (p/'input.csv').write_text(sample,encoding='utf-8')
            (p/'mapping.json').write_text('{"version":1,"version":1}',encoding='utf-8')
            with self.assertRaises(RuntimeError):m.read_contacts(p/'input.csv',p/'mapping.json')

    def test_php_transport_encoding_is_explicit(self):
        import ast
        tree=ast.parse(SOURCE.read_text(encoding='utf-8'))
        calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)
               and isinstance(n.func.value,ast.Name) and n.func.value.id=='guard' and n.func.attr=='inventory']
        self.assertEqual(len(calls),1)
        keywords={k.arg:k.value for k in calls[0].keywords}
        transport=keywords['input_data']
        self.assertIsInstance(transport,ast.Call)
        self.assertEqual(transport.func.attr,'encode')
        self.assertEqual(ast.literal_eval(transport.args[0]),'utf-8')
        self.assertIn('fence',keywords)

if __name__=='__main__':unittest.main()
