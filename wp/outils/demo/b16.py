"""B16 : enveloppe article, C08/B03 inchangés."""
import sys
sys.dont_write_bytecode = True
import b13
ROOT = b13.ROOT
OUT = ROOT/'production/B-16'
FILES = ['plugins/imagine-site/PageArticle.php', 'themes/imagine/single.php']
BLOCK = "// B16 — enveloppe éditoriale publique, corps C08 inchangé.\nrequire_once __DIR__ . '/PageArticle.php';\nPageArticle::register();\n\n"
HEADING = '## B-16 — enveloppe de la page article'
PREIMAGES = {}
sources, wp, php, guard = b13.sources, b13.wp, b13.php, b13.guard
if __name__ == '__main__':
    owner = sys.modules[__name__]
    OUT.mkdir(exist_ok=True)
    {'native':b13.runtime, 'install':b13.install, 'image':lambda o,n:b13.gate(o,'image',n), 'replay':lambda o,n:b13.gate(o,'replay',n)}[sys.argv[1]](owner, sys.argv[2])
