"""C09 — profils natifs fictifs, cible unique, aucun paiement externe."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import construire as b00


def validate_target(slug):
    if not slug.startswith('imagine-test-') or slug != 'imagine-test-demo':
        raise ValueError('Voie 2 : seul imagine-test-demo est autorisé')
