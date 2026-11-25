"""B03 scoped guard: immutable historical evidence, exact current-run stability."""
from pathlib import Path
import hashlib
import json

C15_PATHS = [
    'plugins/imagine-site/EcheancesAdmin.php',
    'plugins/imagine-site/EcheancesNatives.php',
    'plugins/imagine-site/EcheancesRegles.php',
    'plugins/imagine-site/imagine-site.php',
]
TABLES = ['wp_postmeta', 'wp_posts', 'wp_wc_orders', 'wp_wc_orders_meta']
C15_LOCAL_DOCUMENT = 'plugins/imagine-site/README.md'
LINKS = ['production/B-03/corrections-before.json',
         'production/B-03/preservation-corrections.json',
         'production/B-03/verification-finale.json',
         'production/C-15/verification.json', 'production/C-15/restauration.json',
         'production/C-15/livraison.json', 'production/C-15/installation.json',
         'production/C-15/action.json', 'production/C-15/PRET',
         'production/C-15/A-VOIR.md', 'wp/tests/demo/c15-action.py']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def links(root):
    return {p: digest(root / p) for p in LINKS}


def local_snapshot(root):
    return {p.relative_to(root / 'wp').as_posix(): digest(p)
            for d in ['themes/imagine', 'plugins'] for p in (root / 'wp' / d).rglob('*') if p.is_file()}


def changed(old, new):
    return sorted(k for k in set(old) | set(new) if old.get(k) != new.get(k))


def compare(baseline, start, end, allowed_assets, c15_sources, c15_local_documents=None):
    c15_local_documents = c15_local_documents or {}
    remote_delta = changed(baseline['remote'], end['remote'])
    local_delta = changed(baseline['local'], end['local'])
    expected_sources = sorted(list(allowed_assets) + C15_PATHS)
    tables = [k for k in remote_delta if '/' not in k]
    checks = {
        'snapshot_courant_distant_exact_stable': start['remote'] == end['remote'],
        'snapshot_courant_local_exact_stable': start['local'] == end['local'],
        'sources_historiques_deltas_exactement_B03_et_C15':
            [k for k in remote_delta if '/' in k] == expected_sources
            and local_delta == sorted(expected_sources + list(c15_local_documents)),
        'documents_C15_locaux_exactement_lies_livraison':
            set(c15_local_documents) <= {C15_LOCAL_DOCUMENT}
            and all(end['local'].get(k) == v and k not in baseline['remote'] and k not in end['remote']
                    for k, v in c15_local_documents.items()),
        'sources_C15_exactes_recu_final_local_distant': set(c15_sources) == set(C15_PATHS)
            and all(end['local'].get(k) == v == end['remote'].get(k) for k, v in c15_sources.items()),
        'tables_historiques_inventaire_delta_attendu': tables == TABLES,
    }
    return checks, {
        'historical_remote_changed': remote_delta, 'historical_local_changed': local_delta,
        'C15_local_only_document_deltas': {k: {'baseline_sha256': baseline['local'].get(k),
                                              'current_sha256': end['local'].get(k),
                                              'delivery_sha256': v,
                                              'remote': 'Absent du snapshot distant historique et courant ; aucun deploiement'}
                                          for k, v in c15_local_documents.items()},
        'historical_table_deltas': {k: {'baseline_sha256': baseline['remote'].get(k),
                                      'current_sha256': end['remote'].get(k)} for k in tables},
        'current_remote_changed': changed(start['remote'], end['remote']),
        'current_local_changed': changed(start['local'], end['local']),
        'historical_whole_tables_unchanged': not tables,
        'historical_table_classification': 'Compatible avec action/reset C15 documente ; attribution exhaustive ligne par ligne NON prouvee par les seules empreintes historiques.',
        'reservation': 'La reference historique contient seulement des empreintes de tables, pas les lignes. Ni identite historique des tables ni attribution exclusive de chaque delta a C15 ne sont revendiquees. Acceptation B03 fondee sur stabilite exacte de son propre rejeu, sources fermees, C09 natif frais et HTTP frais.',
    }


def documentary(root):
    def read(name):
        return json.loads((root / 'production/C-15' / name).read_text(encoding='utf-8'))
    verification, restored, delivery, installation, action = [read(n) for n in
        ['verification.json', 'restauration.json', 'livraison.json', 'installation.json', 'action.json']]
    sources = {k.removeprefix('wp/'): v for k, v in verification['source_sha256'].items()}
    local_documents = {C15_LOCAL_DOCUMENT: delivery['files_sha256']['wp/' + C15_LOCAL_DOCUMENT]}
    c09 = verification['C09_paiements_natifs']
    checks = {
        'C15_lien_documentaire_action_reset_semantique':
            verification['status'] == 'PRET_RELECTURE'
            and verification['scope'] == 'imagine-test-demo'
            and all(v is True for v in verification['action_HTTP_et_reset'].values())
            and restored == {'C09_reset': True, 'dependent_discovery_restored': True,
                             'baseline_semantic_equal': True, 'theme_written': False}
            and delivery['verified'] is True and delivery['semantic_restore'] is True
            and delivery['source_readback_exact'] is True
            and c09 == {'total': 149, 'failures': [], 'exit': 0}
            and bool(action['checks']) and all(v is True for v in action['checks'].values())
            and not action['failures'] and (root / 'production/C-15/PRET').is_file(),
        'C15_action_source_liee_livraison': delivery['files_sha256']['wp/tests/demo/c15-action.py']
            == digest(root / 'wp/tests/demo/c15-action.py'),
        'C15_sources_liees_installation_livraison': set(sources) == set(C15_PATHS)
            and all(v == installation['sha256_readback'][Path(k).name]
                    == delivery['files_sha256']['wp/' + k] for k, v in sources.items()),
    }
    return checks, sources, local_documents
