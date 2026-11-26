"""C23 : tests du détecteur et de ses garde-fous, sans site ni secret."""
from pathlib import Path
import importlib.util
import sys
import unittest
sys.dont_write_bytecode = True
SOURCE = Path(__file__).resolve().parents[2] / 'outils/demo/c23.py'

class DetectorTest(unittest.TestCase):
    def test_fuite_texte_reel_refusee(self):
        self.assertTrue(SOURCE.is_file(), 'Le détecteur C23 reste à construire')
        spec = importlib.util.spec_from_file_location('c23', SOURCE)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertFalse(module.assess(200, b'<p>LE TEMOIN SECRET</p>', ['LE TEMOIN SECRET'], present='titre')['ok'])

def load():
    spec = importlib.util.spec_from_file_location('c23', SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class ContractTest(unittest.TestCase):
    def test_voie_absente_ne_passe_pas_a_vide(self):
        m = load()
        self.assertFalse(m.assess(200, b'<h1>Autre page</h1>', ['secret'], present='article-cible')['ok'])
    def test_500_ne_passe_pas(self):
        self.assertFalse(load().assess(500, b'panne', ['secret'])['ok'])
    def test_temoin_encode_json_et_html_detecte(self):
        m = load()
        self.assertTrue(m.assess(200, b'{"content":"caf\\u00e9 &amp; secret"}', ['café & secret'])['leak'])
    def test_inverse_est_necessaire(self):
        m = load()
        self.assertFalse(m.assess(200, b'extrait', ['secret'], positive=True)['ok'])
        self.assertTrue(m.assess(200, b'secret', ['secret'], positive=True)['ok'])
    def test_reseau_hors_demo_refuse_avant_requete(self):
        m = load()
        self.assertTrue(callable(getattr(m, 'validate_path', None)), 'Garde réseau à construire')
        for path in ['//example.org/', 'https://example.org/', '/\\\\example.org/', '/x\r\nCookie: secret']:
            with self.assertRaises(ValueError):
                m.validate_path(path)
    def test_cdata_ne_masque_jamais_temoin(self):
        self.assertTrue(load().assess(200,b'<title><![CDATA[secret]]></title>',['secret'])['leak'])
    def test_recherche_reflechie_n_est_pas_fuite(self):
        m=load()
        self.assertTrue(callable(getattr(m,'search_results_body',None)), 'Extraction réelle des résultats à construire')
        body=b'<title>secret</title><main><h1>Recherche secret</h1><form>secret</form><p>Aucun resultat</p></main>'
        self.assertFalse(m.assess(200,m.search_results_body(body),['secret'])['leak'])
        leaking=body.replace(b'Aucun resultat',b'<li data-imagine-id="42">secret</li>')
        self.assertTrue(m.assess(200,m.search_results_body(leaking),['secret'])['leak'])
    def test_faux_sitemap_html_et_archive_vide_refuses(self):
        m=load()
        for kind in ['sitemap','cards','rest-item','rest-list','rest-error','oembed','empty-search','feed','sharing','pdf-denied','admin-denied']:
            self.assertFalse(m.structure_ok({'structure':kind,'name':'archives'},200,b'<html><p>Tout va bien</p></html>',{'article':42}),kind)
    def test_catalogue_routes_non_vide_et_complet(self):
        m = load()
        self.assertTrue(callable(getattr(m, 'build_routes', None)), 'Inventaire des voies à construire')
        f = {'article':42,'article_path':'/demo-2026-t4-reserve-1/', 'issue':39,
             'issue_path':'/numeros/demo-2026-t4/', 'pdf':41, 'issue_slug':'demo-2026-t4',
             'auto':82, 'auto_path':'/c08-article-reserve-automatique/', 'term_path':'/thematique/demo-thematique-1/',
             'c08':81,'c12':235, 'posts_archive':'/2026/', 'attachment_path':'/demo-2026-t4-pdf/', 'partners':[]}
        rows = m.build_routes(f)
        names = [r['name'] for r in rows]
        self.assertEqual(len(names), len(set(names)))
        for name in ['article','accueil','numero','kiosque','thematique','archives','rest-contenu',
                     'rest-recherche','rest-revisions','rss2','oembed','embed','recherche',
                     'partage','extrait-automatique','sitemap','pdf-telechargement','pdf-direct','pdf-piece-jointe']:
            self.assertIn(name, names)
        self.assertTrue(all(r.get('present') or r.get('denied') for r in rows))

if __name__ == '__main__':
    unittest.main(verbosity=2)
