"""Instantiate owned transport adapters from the accepted narrow launcher."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
DEST = ROOT / 'wp/outils/bascule/a25'
for name in ('confine.py', 'Command.php', 'inventorier-comptes', 'refusals.json'):
    text = (ROOT / 'wp/outils/bascule/a23' / name).read_text(encoding='utf-8')
    for a,b in [('A23','A25'),('a23','a25'),('ReaderAccounts','VisitorRetention'),('inventorier-comptes','inventorier-visiteurs'),('comptes.json','visiteurs.json'),('comptes.md','visiteurs.md'),('Comptes des lecteurs','Données des visiteurs'),('Comptes seulement ; aucune activation ni décision de reprise.','Comptes seulement ; aucune suppression ni durée de conservation.'),('imagine-a25-reader-accounts-v1','imagine-a25-visitor-retention-v1')]:
        text = text.replace(a,b)
    text = text.replace("    require dirname(__DIR__) . '/a17/Inventory.php';\n", '')
    text = text.replace('A25_CUSTOMER_LINK_UNSUPPORTED', 'A25_NATIVE_OBJECT_UNSUPPORTED')
    (DEST / name.replace('inventorier-comptes','inventorier-visiteurs')).write_text(text,encoding='utf-8',newline='\n')
print('A25 transport adapters written')
