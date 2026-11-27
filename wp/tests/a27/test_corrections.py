"""Source contracts, not PHP execution: parent owns the RED/GREEN PHP run."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]


class CorrectionContracts(unittest.TestCase):
    def test_r2_observes_actual_a19_boundary_once_and_removes_observer(self):
        source = (ROOT / 'wp/outils/bascule/a27/Inventory.php').read_text(encoding='utf-8')
        self.assertIn("add_filter('woocommerce_subscription_payment_meta', $observer, PHP_INT_MAX)", source)
        self.assertIn('SubscriptionCoherence\\Inventory::paymentReference($sub)', source)
        self.assertIn("remove_filter('woocommerce_subscription_payment_meta', $observer, PHP_INT_MAX)", source)
        self.assertIn('finally {', source)
        self.assertIn("$opaque && $reference === 'absent' ? 'unknown' : $reference", source)
        self.assertIn("'reference' => self::paymentReference($sub)", source)
        self.assertNotIn("apply_filters('woocommerce_subscription_payment_meta'", source)

    def test_r3_rejects_explicit_conflict_before_gateway_fallback(self):
        source = (ROOT / 'wp/outils/bascule/a27/Analysis.php').read_text(encoding='utf-8')
        guard = "if ($ids && (count($matches) !== 1 || !in_array($matches[0]['id'], $ids, true)))"
        self.assertIn(guard, source)
        self.assertLess(source.index(guard), source.index("$type = in_array($gateway"))
        guarded = source[source.index(guard):source.index('if (count($matches) === 1')]
        self.assertIn("'type' => 'illisible', 'link' => 'unknown'", guarded)


if __name__ == '__main__':
    unittest.main()
