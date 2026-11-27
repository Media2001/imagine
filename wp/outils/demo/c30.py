import sys
sys.dont_write_bytecode=True
import b13
ROOT=b13.ROOT
OUT=ROOT/'production/C-30'
FILES=['plugins/imagine-site/'+n for n in ['CodesSuivisRegles.php','CodesSuivis.php','CodesSuivisAdmin.php','CodesSuivisConfidentialite.php']]
BLOCK="// C30 — accueil et code suivi local, sans avantage financier.\nrequire_once __DIR__ . '/CodesSuivisRegles.php';\nrequire_once __DIR__ . '/CodesSuivis.php';\nrequire_once __DIR__ . '/CodesSuivisAdmin.php';\nrequire_once __DIR__ . '/CodesSuivisConfidentialite.php';\nCodesSuivis::register();\nCodesSuivisAdmin::register();\nCodesSuivisConfidentialite::register();\n\n"
PREIMAGES={'plugins/imagine-site/CodesSuivisAdmin.php':'5ee2c088691a329c9a6bc8f0dd4076215ccb1f54a8dee2d16d6e141aefbe7245','plugins/imagine-site/CodesSuivis.php':'00afe7e063efde7f9a1684f811ba68158f4c51b5f4b9a626c32c8195337b61b8','plugins/imagine-site/CodesSuivisConfidentialite.php':'6afa4314f319920a27a6e8b3cb6c1a31010a93a88c4a2f6784ef2beee4ccc7a1'}
HEADING='## C-30 — bienvenue et codes suivis'
sources,wp,php,guard=b13.sources,b13.wp,b13.php,b13.guard
if __name__=='__main__':
    OUT.mkdir(exist_ok=True);owner=sys.modules[__name__]
    {'native':b13.runtime,'install':b13.install,'image':lambda o,n:b13.gate(o,'image',n),'replay':lambda o,n:b13.gate(o,'replay',n)}[sys.argv[1]](owner,sys.argv[2])
