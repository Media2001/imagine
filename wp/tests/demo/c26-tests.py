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

    def test_scratch_sans_tmpdir_hors_systeme(self):
        m = load('c26-preparer')
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop('TMPDIR', None)
            p = m.scratch()
        self.assertTrue(p.is_dir())
        self.assertIn('hermes', str(p).lower())
        self.assertNotEqual(p, Path(os.environ.get('LOCALAPPDATA', str(Path.home()/'AppData/Local'))) / 'Temp')


if __name__ == '__main__':
    with patch.object(socket.socket, 'connect', side_effect=AssertionError('réseau interdit')):
        unittest.main(verbosity=2)
