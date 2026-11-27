"""B14 : accueil, seul adaptateur et gabarit du lot ; banc B13 inchangé."""
import sys
sys.dont_write_bytecode = True
import b13
ROOT = b13.ROOT
OUT = ROOT/'production/B-14'
FILES = ['plugins/imagine-site/Accueil.php', 'themes/imagine/front-page.php']
BLOCK = "// B14 — accueil structurel, sans texte réservé.\nrequire_once __DIR__ . '/Accueil.php';\nAccueil::register();\n\n"
HEADING = '## B-14 — accueil dans l’ordre du cahier des charges'
PREIMAGES = {'themes/imagine/front-page.php':'5d1d62a541a785373d5061b9ea194e34a7472febeefae098a58a112bf9cae7b9'}
sources, wp, php, guard = b13.sources, b13.wp, b13.php, b13.guard
if __name__ == '__main__':
    owner = sys.modules[__name__]
    OUT.mkdir(exist_ok=True)
    {'native':b13.runtime,'install':b13.install,'image':lambda o,n:b13.gate(o,'image',n),'replay':lambda o,n:b13.gate(o,'replay',n)}[sys.argv[1]](owner,sys.argv[2])
