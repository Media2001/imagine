"""Régressions P1/P2 sans site ; --legacy montre les faux verts antérieurs."""
import sys
sys.dont_write_bytecode = True
import ast
import importlib.util
import json
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'wp/outils/demo'))
import c33_control as c
legacy = '--legacy' in sys.argv
if legacy:
    sys.argv.remove('--legacy')
    source = ROOT / 'production/C-33/historique-avant-corrections-V2/c33-browser.py'
    fn = next(node for node in ast.parse(source.read_text(encoding='utf-8')).body if isinstance(node, ast.FunctionDef) and node.name == 'control')
    env = {'json': json, 'ET': ET, 'login': 'LOGIN_C33', 'display': 'NOM_C33', 'signature': 'SIGNATURE', 'fixture': {'path': '/temoin/'}}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), str(source), 'exec'), env)


def assess(body, headers, expected='SITE & FICTIF'):
    if legacy:
        # Reproduit la sélection faite AVANT l'ancien control().
        return env['control']('feed', 200, body, c.archive_headers(headers), expected)
    return c.control('feed', 200, body, headers, '/temoin/', 'LOGIN_C33', 'NOM_C33', expected)


def feed(kind, author='SITE &amp; FICTIF', uri=''):
    if kind == 'rss2':
        return '<rss xmlns:dc="'+c.RSS+'"><channel><title>SITE &amp; FICTIF</title><item><link>https://example.org/autre/</link><dc:creator>SITE &amp; FICTIF</dc:creator></item><item><link>https://example.org/temoin/</link><dc:creator>'+author+'</dc:creator>'+uri+'</item></channel></rss>'
    return '<feed xmlns="'+c.ATOM+'"><title>SITE &amp; FICTIF</title><entry><link href="https://example.org/autre/"/><author><name>SITE &amp; FICTIF</name></author></entry><entry><link href="https://example.org/temoin/"/><author><name>'+author+'</name>'+uri+'</author></entry></feed>'


class C33ControlTest(unittest.TestCase):
    def test_entetes_hors_trois_noms_valeurs_et_noms_doublons(self):
        for name, value in [('X-Compte', 'LOGIN_C33'), ('NOM_C33', 'neutre'), ('Set-Cookie', 'opaque=LOGIN_C33')]:
            with self.subTest(name=name):
                verdict = assess(feed('rss2'), [{'name': 'Content-Type', 'value': 'application/xml'}, {'name': name, 'value': value}])
                self.assertFalse(verdict['ok'])
                self.assertTrue(verdict['leak'])
        headers = [{'name': 'X-Compte', 'value': 'NOM_C33'}, {'name': 'X-Compte', 'value': 'neutre'}]
        self.assertFalse(assess(feed('rss2'), headers)['ok'])

    def test_occultation_cookie_et_secret_apres_controle(self):
        headers = [{'name': 'Content-Type', 'value': 'application/xml'}, {'name': 'Set-Cookie', 'value': 'secret=opaque'}, {'name': 'Authorization', 'value': 'Bearer opaque'}]
        self.assertTrue(assess(feed('rss2'), headers)['ok'])
        self.assertEqual({'content-type': 'application/xml'}, c.archive_headers(headers))
        self.assertNotIn('opaque', json.dumps(c.archive_headers(headers)))

    def test_auteur_exact_xml_rss2_atom_signature_et_repli(self):
        for kind in ['rss2', 'atom']:
            for expected, encoded in [('SITE & FICTIF', 'SITE &amp; FICTIF'), ('Signé & FICTIF', 'Signé &amp; FICTIF')]:
                with self.subTest(kind=kind, expected=expected):
                    self.assertTrue(assess(feed(kind, encoded), {}, expected)['ok'])

    def test_retrait_auteur_temoin_refuse_meme_si_site_ailleurs(self):
        for kind in ['rss2', 'atom']:
            with self.subTest(kind=kind):
                body = c.remove_feed_author(feed(kind), '/temoin/')
                self.assertIn('SITE &amp; FICTIF', body)
                self.assertFalse(assess(body, {})['ok'])

    def test_mauvais_auteur_et_approximation_refuses(self):
        for kind in ['rss2', 'atom']:
            for author in ['AUTRE', 'SITE &amp; FICTIF suffixe']:
                with self.subTest(kind=kind, author=author):
                    self.assertFalse(assess(feed(kind, author), {})['ok'])

    def test_uri_et_url_compte_refusees_separement(self):
        for field in ['uri', 'url']:
            with self.subTest(field=field):
                self.assertFalse(assess(feed('atom', uri='<'+field+'>https://example.org/auteur/</'+field+'>'), {})['ok'])
        self.assertFalse(assess(feed('rss2', uri='<author><url>https://example.org/auteur/</url></author>'), {})['ok'])

    def test_temoin_absent_et_xml_invalide_refuses(self):
        for body in [feed('rss2').replace('/temoin/', '/absent/'), feed('atom').replace('/temoin/', '/absent/'), 'SITE & FICTIF']:
            self.assertFalse(assess(body, {})['ok'])


if __name__ == '__main__':
    unittest.main()
