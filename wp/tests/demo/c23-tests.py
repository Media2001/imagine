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
        body = b'<h1>titre</h1><p>LE TEMOIN SECRET</p>'
        result = module.assess(200, body, ['LE TEMOIN SECRET'], present='titre')
        self.assertTrue(result['surface_present'])
        self.assertTrue(result['leak'])
        self.assertFalse(result['ok'])
        self.assertTrue(module.assess(200, b'<h1>titre</h1><p>extrait public</p>', ['LE TEMOIN SECRET'], present='titre')['ok'])

    def test_temoins_attributs_et_commentaires_avec_surface_valide(self):
        m = load()
        for support in ['<meta property="og:description" content="{}">',
                        '<meta name="twitter:description" content="{}">',
                        '<meta name="description" content="{}">',
                        '<div data-secret="{}"></div>', '<!-- {} -->']:
            with self.subTest(support=support):
                body = ('<h1>titre</h1>' + support.format('LE TEMOIN SECRET')).encode()
                result = m.assess(200, body, ['LE TEMOIN SECRET'], present='titre')
                self.assertTrue(result['surface_present'])
                self.assertTrue(result['leak'])
                self.assertFalse(result['ok'])
                self.assertTrue(m.assess(200, body.replace(b'LE TEMOIN SECRET', b'extrait public'), ['LE TEMOIN SECRET'], present='titre')['ok'])

def load():
    spec = importlib.util.spec_from_file_location('c23', SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class RedirectTest(unittest.TestCase):
    def test_corps_302_inspecte_avant_200(self):
        import io
        from email.message import Message
        from unittest.mock import patch
        m = load()
        class Response(io.BytesIO):
            def __init__(self, code, body, location=None):
                super().__init__(body)
                self.code = code
                self.headers = Message()
                if location:
                    self.headers['Location'] = location
        class Client:
            def __init__(self):
                self.paths = []
            def open(self, request, timeout):
                self.paths.append(request.full_url)
                if len(self.paths) == 1:
                    return Response(302, b'<p>LE TEMOIN SECRET</p>', '/arrivee')
                return Response(200, b'<h1>titre</h1>extrait public')
        client = Client()
        with patch.object(m, 'build_opener', return_value=client):
            response = m.fetch('/depart')
        self.assertEqual(client.paths, [m.BASE+'/depart', m.BASE+'/arrivee'])
        result = m.assess_response(response, ['LE TEMOIN SECRET'], present='titre')
        self.assertTrue(result['surface_present'])
        self.assertTrue(result['leak'])
        self.assertFalse(result['ok'])
        self.assertEqual(result['redirects_inspected'], 1)
        self.assertNotIn('LE TEMOIN SECRET', str(result))

    def test_redirection_externe_refusee(self):
        from unittest.mock import patch
        from urllib.request import Request
        from io import BytesIO
        m = load()
        with self.assertRaises(ValueError):
            m.DemoRedirect().redirect_request(Request(m.BASE+'/depart'), BytesIO(), 302, '', {}, 'https://example.org/')

def load_preparer():
    sys.path.insert(0, str(SOURCE.parent))
    spec = importlib.util.spec_from_file_location('c23_preparer_tests', SOURCE.with_name('c23-preparer.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DiscoveryTest(unittest.TestCase):
    def test_preparation_normale_ne_recrit_aucune_politique(self):
        from unittest.mock import patch
        m = load_preparer()
        policy = {'ouverture':'premiere_lecture','forme':'articles','jours':7,'nombre':2,'numeros':['11']}
        f = {'discovery':{'debut':'2026-11-20 00:00:00','reglages':policy,'articles':[1,2]},
             'discovery_policy':policy, 'discovery_relecture':'fermee',
             'users':{'V-INSCRIT':1,'V-DEC-FIN':2,'P-NUMERO':3,'A-CARTE':4}}
        calls = []
        with patch.object(m, 'wp', side_effect=lambda code: calls.append(code) or {}):
            m.prepare(f)
        self.assertEqual(len(calls), 1)
        self.assertNotIn('update_option', calls[0])
        self.assertIn('WP_Session_Tokens', calls[0])

    def test_prerequis_incompatible_refuse_avant_session(self):
        from unittest.mock import patch
        m = load_preparer()
        for policy in [{'ouverture':'fermee','forme':'articles','nombre':2,'numeros':[]},
                       {'ouverture':'premiere_lecture','forme':'articles','nombre':3,'numeros':['11']}]:
            f = {'discovery_policy':policy, 'discovery_relecture':'fermee',
                 'discovery':{'reglages':{'ouverture':'premiere_lecture','forme':'articles','nombre':2,'numeros':['11']},'articles':[1,2]}}
            with patch.object(m, 'wp') as native:
                with self.assertRaisesRegex(ValueError, 'découverte'):
                    m.prepare(f)
                native.assert_not_called()

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
    def test_tous_pdf_inventories_retenus_et_commande_GET_seule(self):
        m=load()
        f={'article':42,'article_path':'/article/','issue':39,'issue_slug':'demo-2026-t4','pdf':41,
           'issue_path':'/numeros/demo-2026-t4/','auto':82,'auto_path':'/auto/','term_path':'/thematique/',
           'c08':81,'c12':235,'posts_archive':'/2026/','partners':[],
           'issues':[{'id':18,'slug':'demo-2026-t2','pdf':20,'title':'Numero 2'}]}
        rows=m.build_routes(f)
        self.assertIn('pdf-inventorie-18-direct',[r['name'] for r in rows])
        import ast
        tree=ast.parse(SOURCE.read_text(encoding='utf-8'))
        methods=[k.value.value for n in ast.walk(tree) if isinstance(n,ast.Call) for k in n.keywords if k.arg=='method' and isinstance(k.value,ast.Constant)]
        self.assertEqual(methods,['GET'])
        self.assertNotIn('subprocess',[n.name for n in ast.walk(tree) if isinstance(n,ast.alias)])
    def test_profils_sans_droit_supplementaires_inclus(self):
        m=load()
        self.assertTrue(callable(getattr(m,'audience_order',None)), 'Publics de la matrice à compléter')
        self.assertEqual(m.audience_order({'additional_publics':{'profil-a-vir':'A-VIR','profil-p-coop':'P-COOP'}}),m.PUBLICS+['profil-a-vir','profil-p-coop'])
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
