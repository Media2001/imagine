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
        events = []
        original_open = client.open
        def opened(request, timeout):
            events.append('open:'+request.full_url)
            return original_open(request, timeout)
        def inspected(status, headers, body):
            events.append('inspect:'+str(status))
            self.assertTrue(m.assess(status,body,['LE TEMOIN SECRET'],expected=(status,))['leak'])
        client.open = opened
        with patch.object(m, 'build_opener', return_value=client):
            response = m.fetch('/depart', on_redirect=inspected)
        self.assertEqual(events,['open:'+m.BASE+'/depart','inspect:302','open:'+m.BASE+'/arrivee'])
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
                 'users':{'V-INSCRIT':1,'V-DEC-FIN':2,'P-NUMERO':3,'A-CARTE':4},
                 'discovery':{'reglages':{'ouverture':'premiere_lecture','forme':'articles','nombre':2,'numeros':['11']},'articles':[1,2]}}
            with patch.object(m, 'wp') as native:
                with self.assertRaisesRegex(ValueError, 'découverte'):
                    m.prepare(f)
                native.assert_not_called()

def load_verifier():
    spec = importlib.util.spec_from_file_location('c23_verifier_tests', Path(__file__).with_name('c23-verifier.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class VerifierTest(unittest.TestCase):
    def test_sortie_json_sans_ecriture(self):
        from unittest.mock import patch
        from contextlib import redirect_stdout
        import io, json
        m = load_verifier()
        output = io.StringIO()
        with patch.object(Path, 'write_text', side_effect=AssertionError('écriture interdite')), redirect_stdout(output):
            m.verify()
        value = json.loads(output.getvalue())
        self.assertEqual(value['scope'], 'imagine-test-demo')
        self.assertGreater(value['total'], 0)

    def test_matrice_vide_total_et_case_manquante_refuses(self):
        import copy, json, hashlib
        m, core, f = load_verifier(), load(), CooperatorsTest().fixture()
        routes, publics = core.cooperator_routes(f), core.audience_order(f)
        rows = [dict(name=r['name'],public=p,ok=True,leak=False) for r in routes for p in publics]
        record = dict(results=rows,total=len(rows),routes=len(routes),publics=publics,leaks=0,failures=0,
                      fixture_sha256=hashlib.sha256(json.dumps(f,sort_keys=True).encode()).hexdigest())
        self.assertTrue(all(m.matrix_checks(core,record,f,True).values()))
        for key, replacement, rejected in [('results',[],'nonempty'),('results',rows[:-1],'complete'),('total',len(rows)+1,'counts')]:
            mutated = dict(record, **{key:replacement})
            self.assertFalse(m.matrix_checks(core,mutated,f,True)[rejected])

    def test_sha_etat_derive_accepte_evolution_legitime_refuse_derive(self):
        import hashlib, json
        m = load_verifier()
        for state in [{'fictif':'version-1'}, {'fictif':'version-2'}]:
            sha = hashlib.sha256(json.dumps(state, sort_keys=True).encode()).hexdigest()
            receipt = {'native_before_sha256':sha, 'native_after_sha256':sha}
            self.assertTrue(m.business_original_exact(state, receipt, receipt))
            self.assertFalse(m.business_original_exact(state, receipt, dict(receipt, native_after_sha256='0'*64)))
        self.assertFalse(m.business_original_exact({}, {}, {}))

class CooperatorsTest(unittest.TestCase):
    def fixture(self):
        import json
        f = json.loads((SOURCE.parents[3]/'production/C-23/inventaire-source.json').read_text(encoding='utf-8'))
        f['cooperator_pages'] = [{'id':900+i,'path':'/espace-cooperateurs/p'+str(i)+'/',
                                  'title':'Page fictive '+str(i),'body':'C23_COOP_TEMOIN_'+str(i)} for i in range(5)]
        f['cooperator_publics'] = ['profil-p-coop']
        return f

    def test_cinq_pages_reellement_inventoriees_et_sorties_ajoutees(self):
        m, f = load(), self.fixture()
        rows = m.cooperator_routes(f)
        self.assertEqual(len({r['cooperator_page'] for r in rows}), 5)
        for page in f['cooperator_pages']:
            names = [r['name'] for r in rows if r['cooperator_page']==page['id']]
            for suffix in ['html','rest','rest-route','collection','oembed','embed','recherche']:
                self.assertIn('b06-'+str(page['id'])+'-'+suffix, names)
        self.assertNotIn('flux', [r['cooperator_kind'] for r in rows], 'Ne pas créditer un flux de posts comme un flux des pages B06')
        all_names = [r['name'] for r in m.build_routes(f)]
        self.assertTrue(all(r['name'] in all_names for r in rows))

    def test_pages_vides_ou_absentes_ne_prouvent_pas_absence(self):
        m, f = load(), self.fixture()
        for pages in [[], f['cooperator_pages'][:4], [dict(p, body='') for p in f['cooperator_pages']]]:
            with self.subTest(count=len(pages)):
                with self.assertRaisesRegex(ValueError, 'B06'):
                    m.cooperator_routes(dict(f, cooperator_pages=pages))

    def test_embed_natif_expurge_reste_inspectable(self):
        m, f = load(), self.fixture()
        route = next(r for r in m.cooperator_routes(f) if r['cooperator_kind']=='embed')
        body = ('<h1>'+route['present']+'</h1><div class="wp-embed-excerpt"></div>').encode()
        self.assertTrue(m.assess_cooperator(route,(200,{},body),False)['ok'])


    def test_controle_B06_reel_non_vide_mutation_par_sortie(self):
        import json
        m, f = load(), self.fixture()
        for route in m.cooperator_routes(f):
            marker, kind = route['cooperator_marker'], route['cooperator_kind']
            if kind in ['rest','rest-route','oembed']:
                body = json.dumps({'code':'imagine_cooperateurs_reserve','data':{'status':403}}).encode()
                status = 403
                leaking = body[:-1]+b',"leak":"'+marker.encode()+b'"}'
            elif kind == 'collection':
                body, status = b'[]', 200
                leaking = json.dumps([{'id':route['cooperator_page'],'content':marker}]).encode()

            elif kind == 'recherche':
                body, status = b'<main><h1>Recherche</h1><p>Aucun resultat</p></main>', 200
                leaking = body.replace(b'</main>',marker.encode()+b'</main>')
            else:
                body, status = ('<h1>'+route['present']+'</h1><p data-imagine-cooperateurs-refus>Reserve</p>').encode(), 200
                leaking = body+b'<!-- '+marker.encode()+b' -->'
            with self.subTest(route=route['name']):
                result = m.assess_cooperator(route,(status,{},body),False)
                self.assertTrue(result['surface_present'])
                self.assertTrue(result['ok'])
                red = m.assess_cooperator(route,(status,{},leaking),False)
                self.assertTrue(red['leak'])
                self.assertFalse(red['ok'])
                self.assertFalse(m.assess_cooperator(route,(status,{},b''),False)['ok'])

    def test_mutation_par_voie_B06_surface_presente_et_inverse(self):
        m, f = load(), self.fixture()
        for route in m.cooperator_routes(f):
            marker = 'C23_COOP_TEMOIN_'+str(route['cooperator_page']-900)
            # Corps synthétique pour isoler chaque contrôle ; le HTTP natif est une recette séparée.
            clean = b'<h1>Page fictive</h1><p>surface publique valide</p>'
            self.assertTrue(m.assess(200,clean,[marker],present='Page fictive')['ok'])
            red = m.assess(200,clean+b'<!-- '+marker.encode()+b' -->',[marker],present='Page fictive')
            self.assertTrue(red['surface_present'])
            self.assertTrue(red['leak'])
            self.assertFalse(red['ok'])
            self.assertTrue(m.assess(200,clean+marker.encode(),[marker],positive=True)['ok'])
            self.assertFalse(m.assess(200,clean,[marker],positive=True)['ok'])

class PreparationSafetyTest(unittest.TestCase):
    def test_pages_non_vides_refusees_avant_ecriture(self):
        from unittest.mock import patch
        m = load_preparer()
        with patch.object(m, 'wp') as native:
            with self.assertRaisesRegex(ValueError, 'B06'):
                m.seed_cooperator_witness([{'ID':1,'post_content':'contenu existant','post_excerpt':''}])
            native.assert_not_called()

    def test_label_V2_accepte_et_collision_refusee_sans_site(self):
        import tempfile
        from unittest.mock import patch
        m = load_preparer()
        with tempfile.TemporaryDirectory(dir=__import__('os').environ.get('TMPDIR')) as directory:
            proof = Path(directory)
            (proof/'livraison-V2.json').write_text('{}',encoding='utf-8')
            with patch.object(m,'PROOF',proof), patch.object(m.profils,'guard') as guard, patch.object(m,'inventory',side_effect=AssertionError('site interdit au test')):
                with self.assertRaisesRegex(ValueError,'existe'):
                    m.run('livraison-V2')
                guard.assert_not_called()

class LiveMutationHarnessTest(unittest.TestCase):
    def test_mutation_de_vrais_corps_preserve_json_et_restaure_source(self):
        import json
        source = Path(__file__).with_name('c23-mutations.py')
        self.assertTrue(source.is_file(), 'Recette de mutations des réponses natives à construire')
        spec = importlib.util.spec_from_file_location('c23_live_mutations',source)
        m = importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        for body in [b'[]',b'{"code":"imagine_cooperateurs_reserve","data":{"status":403}}',b'<h1>Page</h1>']:
            original = bytes(body)
            changed = m.inject(body,'C23_COOP_TEMOIN_1')
            self.assertIn(b'C23_COOP_TEMOIN_1',changed)
            self.assertEqual(body,original)
            if body.startswith(b'{'):
                self.assertEqual(json.loads(changed)['code'],json.loads(body)['code'])
            if body.startswith(b'['):
                self.assertIsInstance(json.loads(changed),list)

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
        body=b'<title>Recherche : secret</title><main><h1>Recherche : secret</h1><form><input type="search" name="s" value="secret"></form><p>Aucun resultat</p></main>'
        self.assertFalse(m.assess(200,m.search_results_body(body,'secret'),['secret'])['leak'])
        leaking=body.replace(b'Aucun resultat',b'<li data-imagine-id="42">secret</li>')
        self.assertTrue(m.assess(200,m.search_results_body(leaking,'secret'),['secret'])['leak'])
        for extra in [b'<meta property="og:description" content="secret">', b'<!-- secret -->', b'<div data-x="secret"></div>']:
            with self.subTest(extra=extra):
                # Aucun bout de réponse hors <main>, attribut de formulaire, ni commentaire supprimé.
                self.assertTrue(m.assess(200,m.search_results_body(extra+body,'secret'),['secret'])['leak'])
                self.assertTrue(m.assess(200,m.search_results_body(body.replace(b'</form>',extra+b'</form>'),'secret'),['secret'])['leak'])
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
