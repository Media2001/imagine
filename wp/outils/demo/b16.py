"""B16 : enveloppe article, C08/B03 inchangés."""
import sys
sys.dont_write_bytecode = True
import os
os.environ['TMPDIR'] = 'C:/Users/Ced/AppData/Local/hermes/cache/scratch'
import b13
ROOT = b13.ROOT
OUT = ROOT/'production/B-16'
FILES = ['plugins/imagine-site/PageArticle.php', 'themes/imagine/single.php']
BLOCK = "// B16 — enveloppe éditoriale publique, corps C08 inchangé.\nrequire_once __DIR__ . '/PageArticle.php';\nPageArticle::register();\n\n"
HEADING = '## B-16 — enveloppe de la page article'
PREIMAGES = {'plugins/imagine-site/PageArticle.php':'d5e57aed64a1434b72f80588191d6ff1ebd80270c8da824f9c0d254355a0ee87','themes/imagine/single.php':'71b98dcdd3f3a9f537224f8e6c574dc5754760795de78369f7a526a46af0bfad'}
sources, wp, php, guard = b13.sources, b13.wp, b13.php, b13.guard
if __name__ == '__main__':
    owner = sys.modules[__name__]
    OUT.mkdir(exist_ok=True)
    {'native':b13.runtime, 'install':b13.install, 'image':lambda o,n:b13.gate(o,'image',n), 'replay':lambda o,n:b13.gate(o,'replay',n)}[sys.argv[1]](owner, sys.argv[2])
