"""Create lot-owned test scaffolding; never modify shared sources."""
from pathlib import Path
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
TEST = ROOT / 'wp/tests/a25'
TOOL = ROOT / 'wp/outils/bascule/a25'
PROD = ROOT / 'production/A-25'
TOOL.mkdir(parents=True, exist_ok=True)
PROD.mkdir(parents=True, exist_ok=True)
# Established harness topology only; new business tests and collector are authored separately.
for name in ('run.py', 'matrix.py', 'style.py', 'test_launcher.py'):
    text = (ROOT / 'wp/tests/a23' / name).read_text(encoding='utf-8')
    text = text.replace('A23', 'A25').replace('a23', 'a25').replace('A-23', 'A-25').replace('readers', 'visitors').replace('inventorier-comptes', 'inventorier-visiteurs')
    if name == 'run.py':
        text = text.replace("'a17/Inventory.php', ", '').replace("            b.call(['exec', name, 'mkdir', '-p', '/subject/a17'])\n            b.call(['cp', b.local(ROOT / 'wp/outils/bascule/a17/Inventory.php'), name + ':/subject/a17/Inventory.php'])\n", '')
    (TEST / name).write_text(text, encoding='utf-8', newline='\n')
print('A25 scaffolding ready')
