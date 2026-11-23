"""C09 — profils natifs fictifs, cible unique, aucun paiement externe."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import construire as b00
import json


def catalogue():
    rows = json.loads(Path(__file__).with_name('c09-profils.json').read_text(encoding='utf-8'))
    for row in rows:
        row['login'] = row['code'].lower() if row['compte'] else None
    return rows


def validate_target(slug):
    if not slug.startswith('imagine-test-') or slug != 'imagine-test-demo':
        raise ValueError('Voie 2 : seul imagine-test-demo est autorisé')
