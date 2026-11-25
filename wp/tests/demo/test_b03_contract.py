"""B03 : contrat CSS neutre et préservation de la sortie serveur unique."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[3]
THEME = ROOT / 'wp/themes/imagine'


class B03Contract(unittest.TestCase):
    def test_css_dedie_active_uniquement_par_racine_et_variables(self):
        path = THEME / 'assets/reading.css'
        self.assertTrue(path.is_file(), 'Feuille dédiée absente')
        css = path.read_text(encoding='utf-8')
        self.assertIn('html.imagine-reading', css)
        self.assertNotIn('prefers-reduced-motion', css)
        self.assertEqual(css.count('scroll-behavior: auto;'), 1)
        self.assertIn('--imagine-reading-column', css)
        self.assertIn('[hidden]', css)
        self.assertRegex(css, r'(?s)#imagine-reading-progress\s*\{[^}]*position:\s*fixed;')
        for value in re.findall(r'(?m)^\s*[a-z-]+:\s*([^;]+);', css):
            self.assertFalse(re.search(r'#[0-9a-fA-F]{3,8}\b|\d+(?:px|rem|em|ch|vh|vw|%)', value), value)
        self.assertNotRegex(css, r'\.imagine-paywall-bloc[^{}]*\{[^}]*display:\s*none')

    def test_trois_fonds_neutres_contraste_AA(self):
        tokens = (THEME / 'assets/tokens.css').read_text(encoding='utf-8')
        def luminance(color):
            channels = [int(color[i:i+2], 16) / 255 for i in [0, 2, 4]]
            linear = [v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in channels]
            return sum(v*w for v,w in zip(linear, [.2126, .7152, .0722]))
        for name in ['light', 'sepia', 'dark']:
            values = []
            for role in ['paper', 'ink']:
                found = re.search(r'--imagine-reading-' + name + '-' + role + r':\s*#([0-9a-fA-F]{6});', tokens)
                self.assertIsNotNone(found, name + ' ' + role + ' absent')
                values.append(luminance(found[1]))
            ratio = (max(values)+.05)/(min(values)+.05)
            self.assertGreaterEqual(ratio, 4.5, name)
        self.assertRegex(tokens, r'--imagine-reading-column:\s*70ch;')

    def test_HTTP_lit_la_constante_du_serveur_sans_valeur_magique(self):
        import importlib.util
        from unittest.mock import patch
        path = Path(__file__).with_name('b03-http.py')
        spec = importlib.util.spec_from_file_location('b03_http_contract', path)
        http = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(http)
        self.assertTrue(hasattr(http, 'reading_speed'), 'Lecture de la constante serveur absente')
        for speed in [137, 299]:
            with patch.object(http.c08.b00, 'wp', return_value={'stdout': str(speed), 'stderr': ''}) as remote:
                self.assertEqual(http.reading_speed(), speed)
                self.assertIn('IMAGINE_READING_WORDS_PER_MINUTE', remote.call_args.args[1])
        source = path.read_text(encoding='utf-8')
        self.assertIn('speed = reading_speed()', source)
        self.assertIn('(words + speed - 1) // speed', source)
        self.assertNotRegex(source, r'//\s*200\b|\bwords\s*\+\s*199\b')

    def test_sortie_unique_et_script_sans_reseau(self):
        single = (THEME / 'single.php').read_text(encoding='utf-8')
        self.assertEqual(single.count('imagine_article_body();'), 1)
        self.assertNotIn('post_content', single)
        self.assertNotIn('the_content(', single)
        script = (THEME / 'assets/reading.js').read_text(encoding='utf-8')
        self.assertNotRegex(script, r'\b(fetch|XMLHttpRequest|sendBeacon|WebSocket)\b')
        self.assertLess(len(script.encode()), 12000)


if __name__ == '__main__':
    unittest.main(verbosity=2)
