"""Pure C19 shared-file predecessor contract; no site access."""
from pathlib import Path
import hashlib, sys, unittest
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import c19


class C19SharedContract(unittest.TestCase):
    def test_only_c19_bootstrap_addition_is_a_successor(self):
        self.assertTrue(hasattr(c19, 'matches_predecessor'), 'C19 shared predecessor contract missing')
        old = b'<?php\n// C17 C18 preserved\n'
        sha = hashlib.sha256(old).hexdigest()
        new = old + c19.BLOCK.encode()
        self.assertTrue(c19.matches_predecessor('wp/plugins/imagine-site/imagine-site.php', new, sha))
        self.assertFalse(c19.matches_predecessor('wp/plugins/imagine-site/imagine-site.php', new.replace(b'C18', b'CHANGED'), sha))
        self.assertFalse(c19.matches_predecessor('wp/plugins/imagine-site/EcheancesNatives.php', new, sha))

    def test_readme_preserves_exact_predecessor_bytes(self):
        self.assertTrue(hasattr(c19, 'matches_predecessor'), 'C19 shared predecessor contract missing')
        old = b'# B00\nC17 C18\n'
        sha = hashlib.sha256(old).hexdigest()
        new = old + '\n## C-19 — tableau de bord\nC19 only\n'.encode()
        self.assertTrue(c19.matches_predecessor('wp/plugins/imagine-site/README.md', new, sha))
        self.assertFalse(c19.matches_predecessor('wp/plugins/imagine-site/README.md', new.replace(b'C17', b'changed'), sha))
        self.assertTrue(c19.matches_predecessor('wp/plugins/imagine-site/README.md', old, sha))


if __name__ == '__main__':
    unittest.main()
