import sys
sys.dont_write_bytecode=True
import b13
ROOT=b13.ROOT
OUT=ROOT/'production/C-31'
FILES=['plugins/imagine-site/'+n for n in ['DomainesRefusesRegles.php','DomainesRefuses.php','DomainesRefusesReglages.php']]
BLOCK="// C31 — domaines exacts refusés dans les parcours publics natifs.\nrequire_once __DIR__ . '/DomainesRefusesRegles.php';\nrequire_once __DIR__ . '/DomainesRefuses.php';\nrequire_once __DIR__ . '/DomainesRefusesReglages.php';\nDomainesRefuses::register();\nDomainesRefusesReglages::register();\n\n"
HEADING='## C-31 — domaines refusés à l’inscription'
sources,wp,php,guard=b13.sources,b13.wp,b13.php,b13.guard
if __name__=='__main__':
    OUT.mkdir(exist_ok=True);owner=sys.modules[__name__]
    {'native':b13.runtime,'install':b13.install,'image':lambda o,n:b13.gate(o,'image',n),'replay':lambda o,n:b13.gate(o,'replay',n)}[sys.argv[1]](owner,sys.argv[2])
