import sys
sys.dont_write_bytecode = True
from pathlib import Path
# Point d'entrée historique conservé pour les lecteurs de paquets.
path = Path(__file__).with_name('verifier-corrections.py')
exec(compile(path.read_text(encoding='utf-8'), str(path), 'exec'))

