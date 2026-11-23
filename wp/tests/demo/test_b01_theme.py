"""Contrats B-01 : pas de site de voie 1, pas de règle métier ajoutée."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[3]
THEME = ROOT / 'wp/themes/imagine'


class B01Theme(unittest.TestCase):
    def test_b01_shell_contract(self):
        for name in ['style.css', 'assets/tokens.css', 'functions.php', 'header.php', 'footer.php', 'index.php', 'searchform.php']:
            self.assertTrue((THEME / name).is_file(), name + ' doit exister')
        header = (THEME / 'header.php').read_text(encoding='utf-8')
        footer = (THEME / 'footer.php').read_text(encoding='utf-8')
        for token in ['wp_head()', 'wp_body_open()', '<header', '<nav', '<main', 'id="imagine-main"', 'href="#imagine-main"']:
            self.assertIn(token, header)
        for token in ['wp_footer()', '</main>', '<footer', 'squelette, sans habillage']:
            self.assertIn(token, footer)
        css = (THEME / 'style.css').read_text(encoding='utf-8')
        self.assertIn('Theme Name: Imagine', css)
        self.assertNotIn('@font-face', css)
        self.assertFalse(list(THEME.rglob('*.js')))
        # Les seuls littéraux CSS admis sont mots-clés structurels et variables.
        values = re.findall(r'(?m)^\s*[a-z-]+:\s*([^;]+);', css)
        self.assertTrue(values)
        for value in values:
            self.assertFalse(re.search(r'#[0-9a-fA-F]{3,8}\b|\d+(?:px|rem|em|ch|vh|vw|%)', value), value)
        for source in THEME.rglob('*.php'):
            text = source.read_text(encoding='utf-8')
            self.assertIn('declare(strict_types=1);', text, str(source))
            self.assertIn('namespace Imagine\\Theme;', text, str(source))
            self.assertNotIn('style="', text, str(source))
            self.assertNotIn('<script', text, str(source))

    def test_b01_editorial_templates_and_body_seam(self):
        for name in ['front-page.php', 'archive-imagine_numero.php', 'single-imagine_numero.php',
                     'single.php', 'taxonomy-imagine_thematique.php', 'archive-imagine_evenement.php',
                     'single-imagine_evenement.php', 'archive-imagine_partenaire.php',
                     'single-imagine_partenaire.php', 'page.php', 'search.php', '404.php']:
            self.assertTrue((THEME / name).is_file(), name + ' doit exister')
        functions = (THEME / 'functions.php').read_text(encoding='utf-8')
        self.assertIn('function imagine_article_body(): void', functions)
        single = (THEME / 'single.php').read_text(encoding='utf-8')
        self.assertEqual(single.count('imagine_article_body();'), 1)
        self.assertNotIn('the_content(', single)
        self.assertNotIn('post_content', single)
        for token in ['post_excerpt', 'get_the_author', 'imagine_numero_id', 'imagine_thematique']:
            self.assertIn(token, single)
        number = (THEME / 'single-imagine_numero.php').read_text(encoding='utf-8')
        for token in ['imagine_numero_id', 'imagine_pdf_id', 'get_the_post_thumbnail', 'Sommaire']:
            self.assertIn(token, number)
        self.assertIn('pre_get_posts', functions)
        self.assertIn('is_main_query()', functions)
        self.assertIn("'imagine_sortie'", functions)
        self.assertIn("'DESC'", functions)
        for template in THEME.glob('*.php'):
            if template.name not in ['functions.php', 'header.php', 'footer.php', 'searchform.php']:
                text = template.read_text(encoding='utf-8')
                self.assertEqual(text.count('<h1'), 1, template.name)
                self.assertIn('get_header()', text, template.name)
                self.assertIn('get_footer()', text, template.name)
        home = (THEME / 'front-page.php').read_text(encoding='utf-8')
        for anchor in ['imagine-thematiques', 'imagine-abonnement']:
            self.assertIn('id="' + anchor + '"', home)

    def test_b01_targeted_installation_refuses_other_site(self):
        import importlib.util
        from unittest.mock import patch
        spec = importlib.util.spec_from_file_location('b01_builder', ROOT / 'wp/outils/demo/construire.py')
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        self.assertTrue(hasattr(builder, 'activate_theme'), 'Branchement ciblé B-01 absent')
        for site in [{'slug': 'autre-site', 'status': 'running'}, {'slug': 'imagine-test-demo', 'status': 'stopped'}]:
            with patch.object(builder, 'request_api', return_value=site), patch.object(builder, 'upload') as upload:
                with self.assertRaises((ValueError, RuntimeError)):
                    builder.activate_theme()
                upload.assert_not_called()
        with patch.object(builder, 'request_api', return_value={'slug': 'imagine-test-demo', 'status': 'running'}), \
             patch.object(builder, 'wp', return_value={'stdout': '{"environment":"production","demo":"imagine-test-demo"}'}), \
             patch.object(builder, 'upload') as upload:
            with self.assertRaises(RuntimeError):
                builder.activate_theme()
            upload.assert_not_called()

    def test_b01_html_validator_rejects_structural_regressions(self):
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from b01_html import validate_html
        valid = '<!doctype html><html lang="fr"><head><title>Fictif</title></head><body><a href="#imagine-main">Contenu</a><header><nav aria-label="Menu"><a href="/">Accueil</a></nav></header><main id="imagine-main"><h1>Fictif</h1><p>Texte</p></main><footer>squelette, sans habillage</footer></body></html>'
        self.assertEqual(validate_html(valid), [])
        for bad in [valid.replace('<p>Texte</p>', '<p><div>Texte</p></div>'),
                    valid.replace('<h1>Fictif</h1>', '<h1>Fictif</h1><h1>Double</h1>'),
                    valid.replace('<p>Texte</p>', '<h3>Saut</h3>'),
                    valid.replace('<p>Texte</p>', '<img src="/fictif.png">'),
                    valid.replace('<p>Texte</p>', '<p id="imagine-main">Doublon</p>')]:
            self.assertTrue(validate_html(bad), bad)


if __name__ == '__main__':
    unittest.main(verbosity=2)
