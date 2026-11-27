"""Adaptation locale des paramètres, socle lot_reception_contract inchangé."""
import sys
sys.dont_write_bytecode = True
import hashlib
from contextlib import contextmanager
from unittest.mock import patch
import lot_reception_contract as core

@contextmanager
def bound(owner):
    # Le socle livré fixe B11/C29 dans config : injection temporaire, aucun edit.
    with patch.object(core, 'config', return_value=(owner, owner.OUT.name, owner.HEADING, {})), patch.object(core, 'sources', side_effect=lambda lot: owner.sources(owner)):
        yield core

def seal(owner, evidence, historical):
    with bound(owner) as c:
        return {'scope': 'imagine-test-demo', 'ready': True, 'contract_version': 1,
            'sources': owner.sources(owner), 'bootstrap_contract': c.registration(owner.OUT.name.replace('-', '')),
            'readme_section': hashlib.sha256(c.section(owner.OUT.name.replace('-', '')).encode()).hexdigest(),
            'evidence': {p.name:c.digest(p) for p in evidence},
            'historical_files': {p.name:c.digest(p) for p in historical}}

def integrity(owner, manifest):
    with bound(owner) as c:
        c.integrity(owner.OUT.name.replace('-', ''), manifest, owner.OUT)
