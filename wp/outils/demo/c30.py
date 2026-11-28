import sys
sys.dont_write_bytecode=True
import b13
ROOT=b13.ROOT
OUT=ROOT/'production/C-30'
FILES=['plugins/imagine-site/'+n for n in ['CodesSuivisRegles.php','CodesSuivis.php','CodesSuivisAdmin.php','CodesSuivisConfidentialite.php']]
BLOCK="// C30 — accueil et code suivi local, sans avantage financier.\nrequire_once __DIR__ . '/CodesSuivisRegles.php';\nrequire_once __DIR__ . '/CodesSuivis.php';\nrequire_once __DIR__ . '/CodesSuivisAdmin.php';\nrequire_once __DIR__ . '/CodesSuivisConfidentialite.php';\nCodesSuivis::register();\nCodesSuivisAdmin::register();\nCodesSuivisConfidentialite::register();\n\n"
PREIMAGES={'plugins/imagine-site/CodesSuivisAdmin.php':'45f6716689531d2977e742408c965840cf4b618a35b9e205d2da078216911223','plugins/imagine-site/CodesSuivis.php':'2e91d95dd4a29948527fd68e0974aa6a00bfe6ec353dc31d7f2c566d23be3b60','plugins/imagine-site/CodesSuivisConfidentialite.php':'12ba2bb1166a55c5ab685b07790caa52407c34bf9b94eaf353986f8614894d83'}
HEADING='## C-30 — bienvenue et codes suivis'
sources,wp,php,guard=b13.sources,b13.wp,b13.php,b13.guard
if __name__=='__main__':
    OUT.mkdir(exist_ok=True);owner=sys.modules[__name__]
    {'native':b13.runtime,'install':b13.install,'image':lambda o,n:b13.gate(o,'image',n),'replay':lambda o,n:b13.gate(o,'replay',n)}[sys.argv[1]](owner,sys.argv[2])
