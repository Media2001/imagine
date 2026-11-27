"""Owned PHP architecture contract only; not PHP execution evidence."""
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[3]


class ContractTests(unittest.TestCase):
    def test_native_readers_and_pure_rules_present(self):
        base = ROOT / 'wp/outils/bascule/a31'
        for name in ('Analysis.php', 'Inventory.php', 'Command.php', 'inventorier-commandes'):
            self.assertTrue((base / name).is_file(), 'missing owned A31 PHP subject')
        inventory = (base / 'Inventory.php').read_text(encoding='utf-8')
        for marker in ('OrderUtil::custom_orders_table_usage_is_enabled', 'wc_get_order(',
                       'wcs_get_subscription(', 'WCS_Related_Order_Store', 'get_related_subscription_ids(',
                       "get_parent_id('edit')", 'imagine_staging_disabled_plugins'):
            self.assertIn(marker, inventory)
        pure = (base / 'Analysis.php').read_text(encoding='utf-8')
        for forbidden in ('wpdb', 'get_option(', 'file_put_contents(', 'wc_get_order(', 'get_total('):
            self.assertNotIn(forbidden, pure)
        for name in ('Analysis.php', 'Inventory.php'):
            source = (base / name).read_text(encoding='utf-8')
            for forbidden in ('->save(', '->delete(', 'wp_insert_', 'update_option(', 'wp_remote_', 'get_total('):
                self.assertNotIn(forbidden, source)


if __name__ == '__main__':
    unittest.main()
