"""C26 : contrats offline, sans site et sans TMPDIR obligatoire."""
import sys
sys.dont_write_bytecode = True
import importlib.util
import json
import os
from pathlib import Path
import socket
import unittest
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'wp/outils/demo'))


def load(name, folder='wp/outils/demo'):
    path = ROOT / folder / (name + '.py')
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class ExtensionTest(unittest.TestCase):
    def fixture(self):
        return {'pages': [{'id': 10, 'path': '/soutenir/', 'title': 'Soutenir'}],
                'events': [{'id': 20, 'path': '/evenements/rencontre/', 'title': 'Rencontre'}],
                'registration': 30, 'subject': 31, 'order': 32,
                'markers': {'agenda': 'C26_AGENDA_FICTIF', 'personnalisation': '2001-01-01T01:26:24Z',
                            'retractation': 'C26_RETRACTATION_FICTIF', 'sujet': 'C26_SUJET_FICTIF'},
                'publics': ['anonyme', 'connecte-sans-abonnement', 'abonne-actif']}

    def test_sorties_page_rest_flux_recherche_embed_admin_inventoriees(self):
        m, f = load('c26'), self.fixture()
        routes = m.routes(f)
        self.assertTrue(routes)
        self.assertEqual(len(routes), len({r['name'] for r in routes}))
        for family in ['agenda', 'personnalisation', 'retractation', 'sujet', 'cooperative']:
            self.assertTrue(any(r['family'] == family for r in routes), family)
        for kind in ['page', 'rest', 'feed', 'search', 'oembed', 'embed', 'admin']:
            self.assertTrue(any(r['kind'] == kind for r in routes), kind)
        self.assertTrue(all(m.c23.validate_path(r['path']) for r in routes))

    def test_inventaire_vide_refuse(self):
        m, f = load('c26'), self.fixture()
        for key in ['pages', 'events']:
            with self.assertRaises(ValueError):
                m.routes(dict(f, **{key: []}))

    def test_absence_surface_non_vide_et_fuite_brute(self):
        m = load('c26')
        route = {'kind': 'page', 'title': 'Soutenir', 'statuses': [200]}
        clean = (200, {}, b'<main><h1>Soutenir</h1></main>')
        self.assertTrue(m.assess(route, clean, ['C26_SECRET'])['ok'])
        self.assertFalse(m.assess(route, (200, {}, b''), ['C26_SECRET'])['ok'])
        for payload in [b'<!-- C26_SECRET -->', b'<div data-x="C26_SECRET">']:
            red = m.assess(route, (200, {}, clean[2] + payload), ['C26_SECRET'])
            self.assertTrue(red['leak'])
            self.assertFalse(red['ok'])

    def test_privacy_exige_inverse_et_refuse_tiers_erreur_vide(self):
        m = load('c26')
        good = {'data': [{'value': 'C26_SECRET'}], 'done': True}
        self.assertTrue(m.privacy_assess(good, ['C26_SECRET'], True)['ok'])
        self.assertFalse(m.privacy_assess({'data': [], 'done': True}, ['C26_SECRET'], True)['ok'])
        self.assertTrue(m.privacy_assess({'data': [], 'done': True}, ['C26_SECRET'])['ok'])
        self.assertTrue(m.privacy_assess(good, ['C26_SECRET'])['leak'])
        for invalid in [{}, {'error': True}, {'data': [], 'done': False}]:
            self.assertFalse(m.privacy_assess(invalid, ['C26_SECRET'])['ok'])

    def test_chemin_compte_natif_et_titres_typographiques(self):
        m, f = load('c26'), self.fixture()
        f['account_path'] = '/compte/'
        catalog = m.routes(f)
        self.assertTrue(next(r for r in catalog if r['name']=='personnalisation-compte')['path'].startswith('/compte/'))
        route = {'kind':'page','title':"charte d'indépendance",'statuses':[200]}
        self.assertTrue(m.assess(route,(200,{},'<main><h1>charte d’indépendance</h1></main>'.encode()),[])['ok'])

    def test_droit_numero_achete_non_qualifie_fuite(self):
        m = load('c26')
        f = {'extension':{'markers':{'sujet':'C26_PRIVE'}},'buyer_issues':['1'],
             'posts':[{'reserved':True,'issue':1,'body':'CONTENU_FICTIF_RESERVE_T1'},
                      {'reserved':True,'issue':4,'body':'CONTENU_FICTIF_RESERVE_T4'}]}
        self.assertEqual(m.denied_markers(f,'acheteur-autre-numero'), ['C26_PRIVE','CONTENU_FICTIF_RESERVE_T4'])
        self.assertIn('CONTENU_FICTIF_RESERVE_T1',m.denied_markers(f,'anonyme'))
        self.assertEqual(m.denied_markers(f,'abonne-actif'), ['C26_PRIVE'])

    def test_temoins_complets_droits_numero_et_cooperateur_separes(self):
        m = load('c26')
        phrases = ['Les lucioles violettes de C08 gardent le secret du village fictif.',
                   'Les lanternes argentées de C08 composent un autre récit fictif.',
                   'Le texte réservé C12 reste fictif.',
                   'Les lanternes turquoise de C10 éclairent le jardin imaginaire.']
        f = {'extension':{'markers':{'sujet':'C26_PRIVE'}}, 'buyer_issues':['1'],
             'cooperator_publics':['profil-p-coop'],
             'cooperator_pages':[{'body':'<p>C23_COOP_TEMOIN_9</p>'}],
             'posts':[{'reserved':True,'issue':1,'body':'<p>'+p+'</p>'} for p in phrases]}
        denied = m.denied_markers(f, 'anonyme')
        for phrase in phrases+['C23_COOP_TEMOIN_9']:
            self.assertIn(phrase, denied)
            self.assertTrue(m.assess({'kind':'page','title':'Soutenir','statuses':[200]},
                (200,{},('<main><h1>Soutenir</h1><!-- '+phrase+' --></main>').encode()),denied)['leak'])
        self.assertIn('C23_COOP_TEMOIN_9',m.denied_markers(f,'abonne-actif'))
        self.assertIn(phrases[0],m.denied_markers(f,'profil-p-coop'))
        self.assertNotIn('C23_COOP_TEMOIN_9',m.denied_markers(f,'profil-p-coop'))
        self.assertNotIn(phrases[0],m.denied_markers(f,'acheteur-autre-numero'))
        self.assertIn('C23_COOP_TEMOIN_9',m.denied_markers(f,'acheteur-autre-numero'))
        f['posts'].append({'reserved':True,'issue':1,'body':'Texte sans témoin'})
        with self.assertRaises(ValueError):
            m.denied_markers(f,'abonne-actif')

    def test_archive_agenda_structure_et_injection(self):
        m, f = load('c26'), self.fixture()
        route = next((r for r in m.routes(f) if r['path']=='/evenements/'), None)
        self.assertIsNotNone(route)
        body = b'<main><h1>Agenda</h1><section id="agenda-futurs"><ul><li data-evenement="20"><a href="/evenements/rencontre/">Rencontre</a></li></ul></section><section id="agenda-passes"></section></main>'
        self.assertTrue(m.assess(route,(200,{},body),['C26_SECRET'])['ok'])
        self.assertFalse(m.assess(route,(200,{},b'<main><h1>Agenda</h1></main>'),[])['ok'])
        self.assertTrue(m.assess(route,(200,{},body+b'<!-- C26_SECRET -->'),['C26_SECRET'])['leak'])
        self.assertEqual(next(r for r in m.routes(f) if r['name']=='personnalisation-compte')['path'],'/my-account/')

    def test_oracle_b06_independant_decision_et_metadonnees(self):
        m = load('c26')
        f = {'cooperator_roles':['administrator'], 'cooperator_publics':['profil-p-coop'],
             'cooperator_actors':{'profil-p-coop':{'code':'P-COOP','roles':['customer'],'status':True},
                 'connecte-sans-abonnement':{'code':'V-INSCRIT','roles':['customer'],'status':False}}}
        self.assertEqual(m.cooperator_expected(f), ['profil-p-coop'])
        f['cooperator_publics'].append('connecte-sans-abonnement')
        with self.assertRaises(ValueError): m.validate_cooperator(f)
        f['cooperator_publics']=['profil-p-coop']
        f['cooperator_actors']['connecte-sans-abonnement']['status']=True
        with self.assertRaises(ValueError): m.validate_cooperator(f)
        f['cooperator_actors']['connecte-sans-abonnement'].update(status=False,roles=['editor'])
        f['cooperator_roles']=['editor']
        self.assertEqual(set(m.cooperator_expected(f)),{'profil-p-coop','connecte-sans-abonnement'})

    def test_scratch_sans_tmpdir_hors_systeme(self):
        m = load('c26-preparer')
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop('TMPDIR', None)
            p = m.scratch()
        self.assertTrue(p.is_dir())
        self.assertIn('hermes', str(p).lower())
        self.assertNotEqual(p, Path(os.environ.get('LOCALAPPDATA', str(Path.home()/'AppData/Local'))) / 'Temp')


    def test_fermeture_paquet_compte_cases_unique_et_non_vide(self):
        m = load('c26-verifier', 'wp/tests/demo')
        routes = [{'name':'page','path':'/soutenir/'}]
        row = {'name':'page','public':'anonyme','path':'/soutenir/','ok':True,'leak':False,'surface_present':True,'status':200,'bytes':1,'body_sha256':'a'*64}
        good = {'total':1,'leaks':0,'failures':0,'results':[row]}
        self.assertTrue(all(m.matrix_checks(good,routes,['anonyme']).values()))
        for bad in [dict(good,total=2),dict(good,results=[]),dict(good,results=[row,row]),dict(good,results=[dict(row,ok=False)])]:
            self.assertFalse(all(m.matrix_checks(bad,routes,['anonyme']).values()))
        self.assertFalse(m.restored({'exact_restoration':{},'business_preserved':True}))

    def test_mauvaise_page_et_recherche_vide_refusees(self):
        m = load('c26')
        page = {'kind':'page','title':'Soutenir','statuses':[200]}
        body = b'<nav>Soutenir</nav><main><h1>Autre page</h1></main>'
        self.assertFalse(m.assess(page,(200,{},body),[])['ok'])
        search = {'kind':'search','title':'Soutenir','target_path':'/soutenir/','statuses':[200]}
        self.assertFalse(m.assess(search,(200,{},b'<main><h1>Recherche Soutenir</h1><p>Aucun resultat</p></main>'),[])['ok'])
        self.assertTrue(m.assess(search,(200,{},b'<main><h1>Recherche</h1><h2><a href="/soutenir/">Soutenir</a></h2></main>'),[])['ok'])

    def test_recherche_date_reflexion_feed_encodee_et_commentaire_fuyant(self):
        m = load('c26')
        marker = '2001-01-01T01:26:24Z'
        body = ('<link rel="alternate" type="application/rss+xml" title="Flux '+marker+'" href="'+m.c23.BASE+'/search/2001-01-01T01%3A26%3A24Z/feed/rss2/">'
                '<main><h1>Recherche '+marker+'</h1><input type="search" name="s" value="'+marker+'"><p>Aucun résultat pour votre recherche.</p></main>').encode()
        route = {'kind':'search','reflected':marker,'statuses':[200]}
        self.assertTrue(m.assess(route,(200,{},body),[marker])['ok'])
        self.assertTrue(m.assess(route,(200,{},body+b'<!-- '+marker.encode()+b' -->'),[marker])['leak'])

    def test_privacy_inverse_ne_croit_pas_le_champ_positive(self):
        v = load('c26-verifier','wp/tests/demo')
        rows = [dict(public=p,family=family,name='privacy-'+family,positive=p=='inverse-proprietaire',
            ok=True,leak=False,surface_present=True,witnesses_found=1 if p=='inverse-proprietaire' else 0,
            payload_sha256='a'*64) for p in ['anonyme','inverse-proprietaire'] for family in ['agenda','personnalisation','retractation','sujet']]
        record = dict(total=len(rows),failures=0,leaks=0,results=rows)
        self.assertTrue(all(v.privacy_checks(record,['anonyme']).values()))
        for row in rows:
            if row['public']=='inverse-proprietaire': row.update(positive=False,witnesses_found=0)
        self.assertFalse(all(v.privacy_checks(record,['anonyme']).values()))

    def test_c23_exige_identites_inverses_et_recalcul_toutes_lignes(self):
        import copy
        v = load('c26-verifier','wp/tests/demo')
        # Vraie fixture historique sans inventer de réponse ; tests du vérificateur pur.
        f = json.loads((ROOT/'production/C-26/livraison-finale-inventaire.json').read_text(encoding='utf-8'))
        record = json.loads((ROOT/'production/C-26/livraison-finale-c23.json').read_text(encoding='utf-8'))
        self.assertTrue(all(v.c23_checks(record,f).values()))
        bad = copy.deepcopy(record)
        bad['results']=[r for r in bad['results'] if r['name'] not in ['identite-REST','inverse-article','inverse-pdf','inverse-C08','inverse-achat-C14']]
        bad['total']=len(bad['results'])
        self.assertFalse(all(v.c23_checks(bad,f).values()))
        bad = copy.deepcopy(record)
        next(r for r in bad['results'] if r['name']=='inverse-article').update(ok=False,leak=True)
        self.assertFalse(all(v.c23_checks(bad,f).values()))

    def test_restauration_independante_cleanup_et_b06_en_erreur(self):
        m = load('c26-preparer')
        saved = {'users':[{'ID':'1','user_login':'v-dec'}], 'posts':[], 'usermeta':[]}
        for stage in ['cleanup','b06']:
            with self.subTest(stage=stage), patch.object(m,'fixture',side_effect=RuntimeError('cleanup') if stage=='cleanup' else None) as clean, \
                 patch.object(m.prep,'restore_cooperator',side_effect=ValueError('derive') if stage=='b06' else None) as coop, \
                 patch.object(m,'wp',return_value=True) as meta:
                result = m.restoration(saved,[1],[])
                self.assertEqual(clean.call_count,1)
                self.assertEqual(coop.call_count,1)
                self.assertEqual(meta.call_count,1)
                self.assertFalse(result[stage]['ok'])
                self.assertTrue(result['usermeta']['ok'])

    def test_recu_restauration_ecrit_meme_si_relecture_echoue(self):
        m = load('c26-preparer')
        with patch.object(m,'restoration',return_value={'cleanup':{'attempted':True,'ok':False}}), \
             patch.object(m.b08,'snapshot',side_effect=RuntimeError('read failed')), \
             patch.object(m.b06,'state',side_effect=RuntimeError('state failed')), \
             patch.object(m.b06,'hashes',side_effect=RuntimeError('hash failed')), \
             patch.object(m,'save') as save:
            result = {'scope':'imagine-test-demo','run_error':'RuntimeError'}
            m.finish_restoration('error',result,{},[],[],{},[],{})
            save.assert_called_once_with('error-restauration',result)
            self.assertTrue(result['restoration_errors'])
            self.assertIs(result['business_preserved'],False)

    def test_marqueurs_prives_dedies_pas_de_dates(self):
        source = (ROOT/'wp/tests/demo/c26-fixture.php').read_text(encoding='utf-8')
        self.assertIn("'personnalisation' => 'C26_PERSONNALISATION_FICTIF'",source)
        self.assertIn("'accuse' => 'C26_ACCUSE_FICTIF'",source)
        self.assertNotIn('2001-01-01T01:26:24Z',source)

    def test_mutation_source_relecture_et_restauration_sur_erreur(self):
        import hashlib
        m = load('c26-preparer')
        name = 'themes/imagine/archive-imagine_evenement.php'
        original = (ROOT/'wp'/name).read_bytes()
        mutated = original+b'<!-- C26_SECRET -->'
        remote = {name:original}
        def hashes(names): return {n:hashlib.sha256(remote[n]).hexdigest() for n in names}
        with patch.object(m.b06,'hashes',side_effect=hashes), \
             patch.object(m.b06.profils.b00,'upload',side_effect=lambda n,b:remote.update({n:b})):
            with self.assertRaises(RuntimeError):
                m.mutate_source(name,mutated,lambda:(_ for _ in ()).throw(RuntimeError('test')))
        self.assertEqual(remote[name],original)

    def test_mutation_source_refuse_ecrasement_derive_concurrente(self):
        import hashlib
        m = load('c26-preparer')
        name = 'themes/imagine/archive-imagine_evenement.php'
        original = (ROOT/'wp'/name).read_bytes()
        remote = {name:original}
        def hashes(names): return {n:hashlib.sha256(remote[n]).hexdigest() for n in names}
        with patch.object(m.b06,'hashes',side_effect=hashes), \
             patch.object(m.b06.profils.b00,'upload',side_effect=lambda n,b:remote.update({n:b})):
            with self.assertRaises(ValueError):
                m.mutate_source(name,original+b' mutation',lambda:remote.update({name:b'concurrent'}))
        self.assertEqual(remote[name],b'concurrent')

    def test_commande_visiteur_ne_lance_pas_de_mutation(self):
        import ast
        m = load('c26')
        tree = ast.parse(Path(m.__file__).read_text(encoding='utf-8'))
        self.assertFalse(any(isinstance(n,ast.alias) and n.name in ['subprocess','b05','b06','b08','profils'] for n in ast.walk(tree)))
        self.assertNotIn('update_option',Path(m.__file__).read_text(encoding='utf-8'))


def load_tests(loader, suite, pattern):
    old = load('c23-tests','wp/tests/demo')
    suite.addTests(loader.loadTestsFromModule(old))
    return suite


if __name__ == '__main__':
    with patch.object(socket.socket, 'connect', side_effect=AssertionError('réseau interdit')):
        unittest.main(verbosity=2)
