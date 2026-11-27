"""B15 : pied de page structurel, seul site fictif, banc B13 inchangé."""
import sys
sys.dont_write_bytecode = True
import b13
ROOT = b13.ROOT
OUT = ROOT/'production/B-15'
FILES = ['plugins/imagine-site/PiedPage.php', 'themes/imagine/footer.php']
BLOCK = "// B15 — pied de page identique, sans géolocalisation.\nrequire_once __DIR__ . '/PiedPage.php';\nPiedPage::register();\n\n"
HEADING = '## B-15 — pied de page identique sur toutes les pages'
PREIMAGES = {'themes/imagine/footer.php':'33c8f45ac3c8b199b84b2f83c2fddcccbb401ab18faa57d683ed81e2fea8cbc9'}
sources, wp, php, guard = b13.sources, b13.wp, b13.php, b13.guard
if __name__ == '__main__':
    owner = sys.modules[__name__]
    OUT.mkdir(exist_ok=True)
    {'native':b13.runtime,'install':b13.install,'image':lambda o,n:b13.gate(o,'image',n),'replay':lambda o,n:b13.gate(o,'replay',n)}[sys.argv[1]](owner,sys.argv[2])
