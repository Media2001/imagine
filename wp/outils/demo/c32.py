import sys
sys.dont_write_bytecode=True
import os
os.environ['TMPDIR']='C:/Users/Ced/AppData/Local/hermes/cache/scratch'
import b13
ROOT=b13.ROOT
OUT=ROOT/'production/C-32'
FILES=['plugins/imagine-site/Cookies.php']
BLOCK="// C32 — inventaire fermé, aucun consentement ni script ajouté.\nrequire_once __DIR__ . '/Cookies.php';\nCookies::register();\n\n"
HEADING='## C-32 — cookies observés sur la démonstration'
sources,wp,php,guard=b13.sources,b13.wp,b13.php,b13.guard
if __name__=='__main__':
    OUT.mkdir(exist_ok=True);owner=sys.modules[__name__]
    {'native':b13.runtime,'install':b13.install,'image':lambda o,n:b13.gate(o,'image',n),'replay':lambda o,n:b13.gate(o,'replay',n)}[sys.argv[1]](owner,sys.argv[2])
