"""Régressions du runner B02 : réserves réellement observées et déploiement ciblé."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import b02


class B02RunnerTest(unittest.TestCase):
    def test_reservations_are_derived_from_observed_capabilities(self):
        self.assertTrue(callable(getattr(b02, 'acceptance_blockers', None)), 'Calcul des réserves absent')
        complete = {k: True for k in ['profile_sepa4', 'four_states_complete', 'margin', 'counter', 'documents',
                    'failed_order', 'carte_paid', 'native_bacs', 'current_block', 'address_edit_replayed']}
        self.assertEqual([], b02.acceptance_blockers(complete))
        self.assertEqual(1, len(b02.acceptance_blockers(dict(complete, margin=False))))
        observed = dict(complete, native_bacs=False, counter=False, documents=False)
        blockers = b02.acceptance_blockers(observed)
        self.assertEqual(3, len(blockers))
        self.assertNotIn('A-4x-J45', ' '.join(blockers))
        self.assertNotIn('A-CARTE', ' '.join(blockers))
        self.assertEqual(len(complete), len(b02.acceptance_blockers({})))

    def test_deployment_never_overwrites_shared_bootstrap_or_theme(self):
        self.assertEqual({'plugins/imagine-site/MonCompte.php', 'plugins/imagine-site/MonCompteRegles.php',
                          'themes/imagine/parts/mon-compte.php'}, set(b02.FILES))


if __name__ == '__main__':
    unittest.main()
