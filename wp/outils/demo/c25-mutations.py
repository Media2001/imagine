"""Mutations témoins C25 sur sources jetables, jamais sur le site."""
import sys
sys.dont_write_bytecode = True
import contextlib
import hashlib
import io
import json
import re
import c25


def run(label):
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (c25.ROOT / 'wp/plugins/imagine-site').glob('Retractation*.php')}
    rows = []
    cases = {
        'antislash': 'testAntislashWordPressReluEtExporteSansPerte',
        'journal-reglages': 'testReglagesJournalAjoutModificationEtRollbackPreimage',
        'rollback-reglages': 'testReglagesJournalAjoutModificationEtRollbackPreimage',
        'preimage-reglages': 'testReglagesJournalAjoutModificationEtRollbackPreimage',
        'delai': 'testDelaiEtOriginesAvecBornesEtFermeturePrudente',
        'proprietaire': 'testRefusHorsDelaiTitulaireConfirmationEtVerrou',
        'confirmation': 'testRefusHorsDelaiTitulaireConfirmationEtVerrou',
        'doublon': 'testDemandeSeulePersistanteEtRejeuSansAucunEffet',
        'export': 'testConfidentialiteExportReprisePaginationEtEffacementSansTiers',
        'effacement': 'testConfidentialiteExportReprisePaginationEtEffacementSansTiers',
        'export-tiers': 'testConfidentialiteExportReprisePaginationEtEffacementSansTiers',
        'nonce': 'testDeuxEtapesAbandonConfirmationEtOrigineManuelle',
        'mail': 'testDemandeSeulePersistanteEtRejeuSansAucunEffet',
        'http': 'testDemandeSeulePersistanteEtRejeuSansAucunEffet',
        'financier': 'testDemandeSeulePersistanteEtRejeuSansAucunEffet',
    }
    for case, expected in cases.items():
        name = label + '-' + case
        with contextlib.redirect_stdout(io.StringIO()):
            code = c25.local(name, case)
        text = (c25.PROOF / (name + '.log')).read_text(encoding='utf-8')
        failures = re.findall(r'<failure[^>]*>.*?::([^\s]+)', text, re.S)
        assert code == 1 and expected in failures and '<error ' not in text, (case, code, failures)
        rows.append({'mutation': case, 'exit': code, 'required_failure': expected, 'failures': failures, 'log': name + '.log'})
        print(case, 'DETECTED', expected)
    assert hashes == {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (c25.ROOT / 'wp/plugins/imagine-site').glob('Retractation*.php')}
    c25.save(label, {'sources': hashes, 'mutations': rows, 'total': len(rows), 'all_detected': True})


if __name__ == '__main__':
    run(sys.argv[1])
