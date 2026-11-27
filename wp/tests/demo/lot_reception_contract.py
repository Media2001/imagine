"""Bounded B11/C29 receipt checks, following B12's 16h30 contract.

Only acceptance tooling: no functional PHP, bootstrap or demo writes.
"""
import sys
sys.dont_write_bytecode = True
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BOOT = 'wp/plugins/imagine-site/imagine-site.php'
README = ROOT/'wp/plugins/imagine-site/README.md'
RECEIPT = 'reception-contrat-V2.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def config(lot):
    sys.path.insert(0, str(ROOT/'wp/outils/demo'))
    if lot == 'B11':
        import b11 as owner
        return owner, 'B-11', '## B-11 — vidéos, podcasts et sommaire audio', {
            'wp/tests/demo/b11-verifier1330.py': 'production/B-11/verifier1330-avant-contrat-V2.py'}
    assert lot == 'C29', 'LOT'
    import c29 as owner
    return owner, 'C-29', '## C-29 — la fiche du contact pour Brevo, sans Brevo', {
        'production/C-29/verifier.py': 'production/C-29/verifier-avant-contrat-V2.py'}


def registration(lot, raw=None):
    owner, _, _, _ = config(lot)
    raw = (ROOT/BOOT).read_bytes() if raw is None else raw
    block = owner.BLOCK.encode()
    assert raw.count(block) == 1, lot+'_BOOTSTRAP_CONTRACT'
    # A second partial/changed registration must not hide beside the exact block.
    calls = re.findall(rb'^\w+::register\(\);$', block, re.M)
    assert calls and all(raw.count(call) == 1 for call in calls), lot+'_BOOTSTRAP_CONTRACT'
    return {'block': owner.BLOCK, 'sha256': hashlib.sha256(block).hexdigest(), 'occurrences': 1}


def section(lot, text=None):
    _, _, heading, _ = config(lot)
    text = README.read_text(encoding='utf-8') if text is None else text
    starts = list(re.finditer('^'+re.escape(heading)+r'\r?$', text, re.M))
    assert len(starts) == 1, lot+'_README_UNIQUE'
    body = text[starts[0].end():].split('\n## ', 1)[0].strip()
    assert body, lot+'_README_EMPTY'
    return body


def sources(lot):
    owner, folder, _, _ = config(lot)
    paths = [ROOT/'wp'/name for name in owner.FILES if 'wp/'+name != BOOT]
    prefix = lot.lower()
    for pattern in [f'wp/outils/demo/{prefix}*', f'wp/tests/demo/{prefix}*']:
        paths.extend(p for p in ROOT.glob(pattern) if p.is_file())
    pattern = 'wp/plugins/imagine-site/tests/MediasB11*' if lot == 'B11' else 'wp/plugins/imagine-site/tests/ContactBrevoC29*'
    paths.extend(p for p in ROOT.glob(pattern) if p.is_file())
    if lot == 'C29':
        paths.extend([ROOT/'wp/plugins/imagine-site/tests/fixtures/c29-cases.php', ROOT/'production/C-29/verifier.py'])
    paths.extend([Path(__file__), ROOT/'wp/tests/demo/b11-c29-contract-tests.py', ROOT/'wp/outils/demo/b11-c29-contract.py'])
    return {p.relative_to(ROOT).as_posix(): digest(p) for p in sorted(set(paths))}


def tested_sources(lot, recorded):
    """Old runtime receipts bind unchanged owned bytes, never neighboring code.

    Only verifier edits are allowed, and their original bytes stay archived.
    New verification-only files are sealed by the new receipt, not retroactively
    presented as having run in the historical PHP/browser experiments.
    """
    _, _, _, changed = config(lot)
    current = sources(lot)
    tested = {name: value for name, value in recorded.items() if name in current}
    assert tested, lot+'_TESTED_SOURCES_EMPTY'
    for name, value in tested.items():
        path = ROOT/changed[name] if name in changed else ROOT/name
        assert digest(path) == value, lot+'_TESTED_OWNED_BYTES: '+name
    owner, _, _, _ = config(lot)
    functional = {'wp/'+name for name in owner.FILES if 'wp/'+name != BOOT}
    assert functional <= set(tested), lot+'_FUNCTIONAL_TEST_COVERAGE'
    return True


def integrity(lot, manifest, out):
    assert manifest['contract_version'] == 1, 'CONTRACT_VERSION'
    assert manifest['sources'] == sources(lot), 'OWNED_SOURCES'
    assert manifest['bootstrap_contract'] == registration(lot), 'BOOTSTRAP_CONTRACT'
    assert manifest['readme_section'] == hashlib.sha256(section(lot).encode()).hexdigest(), 'README_SECTION'
    assert manifest['evidence'] and all(digest(out/name) == value for name, value in manifest['evidence'].items()), 'EVIDENCE'
    assert manifest['historical_files'] and all(digest(out/name) == value for name, value in manifest['historical_files'].items()), 'HISTORICAL_FILES'


def live_registration(lot, wp, php):
    owner, _, _, _ = config(lot)
    result = wp('$s=file_get_contents(WP_CONTENT_DIR."/plugins/imagine-site/imagine-site.php");echo wp_json_encode(substr_count($s,'+php(owner.BLOCK)+')===1);')
    assert result is True, lot+'_LIVE_BOOTSTRAP_CONTRACT'
