"""Read-only independent verification of a complete A02 evidence packet."""
import argparse
import collections
import hashlib
import json
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[3]
REQUIRED = {'versions', 'commerce', 'memberships', 'content', 'database', 'scheduling', 'risks'}

def load(path):
    return json.loads(path.read_text(encoding='utf8'))

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('evidence', type=pathlib.Path)
    args = p.parse_args()
    evidence = args.evidence.resolve()
    assert evidence.is_relative_to((REPO / 'production/A-02/preuves').resolve())
    runner = load(evidence / 'runner.json')
    result = load(evidence / 'result.json')
    unit = load(evidence / 'unit.json')
    assert runner['mode'] == 'full' and runner['exit_code'] == 0 and result['exit_code'] == 0
    counts = {}
    for label, value in [('unit', unit), ('integration', result), ('runner', runner)]:
        assert value['checks'] and all(c['status'] == 'PASS' for c in value['checks'])
        assert len({c['check'] for c in value['checks']}) == len(value['checks'])
        counts[label] = len(value['checks'])
    passed = {c['check'] for c in result['checks']}
    for storage in ['classic', 'hpos']:
        for key in ['commercial_fixture', 'cli_success', 'db_identical', 'site_files_identical', 'never_bootstrap', 'transaction_blocks_even_root', 'dynamic_config_safe_refusal', 'symlink_parent_refused', 'negative_probes_no_database_change', 'negative_probes_files_restored', 'no_private_values', 'seven_sections', 'replay_success']:
            assert storage + ':' + key in passed
        before = load(evidence / (storage + '-db-before.json'))
        after = load(evidence / (storage + '-db-after.json'))
        assert before == after and before['tables']
        # Recompute the top-level independent fingerprint from its frozen per-table hashes.
        compact = json.dumps(before['tables'], separators=(',', ':'))
        assert hashlib.sha256(compact.encode()).hexdigest() == before['logical_sha256']
        report = load(evidence / storage / 'audit.json')
        md = (evidence / storage / 'audit.md').read_text(encoding='utf8')
        assert set(report['sections']) == REQUIRED and report['read_only'] is True
        assert report['sections']['commerce']['order_storage'] == storage
        assert len(report['priorities']) == 5 and md.count('```json') == 7
        blocks = re.findall(r'```json\n(.*?)\n```', md, re.S)
        assert [json.loads(b) for b in blocks] == list(report['sections'].values())
        assert not re.search(r'A02_[A-Z_]*CANARY|@example\.org|/scratch/|sk_live_', md + json.dumps(report))
        repeated = load(evidence / (storage + '-repeat') / 'audit.json')
        assert repeated['sections'] == report['sections']
        seed = load(evidence / (storage + '-seed.json'))
        assert seed['restriction_real'] and seed['rules'] == 2 and seed['subscriptions'] == 3
        assert len(report['sections']['database']['tables']) == len(before['tables'])
        variant_before = load(evidence / (storage + '-no-cache-db-before.json'))
        assert variant_before == load(evidence / (storage + '-no-cache-db-after.json'))
        unknown = load(evidence / (storage + '-no-cache') / 'audit.json')
        assert all(v['latest'] is None for v in unknown['sections']['versions']['plugins'])
        assert unknown['sections']['risks']['debug_log_coverage'] == 'absent'
    for audit in evidence.rglob('audit.json'):
        assert not re.search(r'A02_[A-Z_]*CANARY|@example\.org|/scratch/|sk_live_', audit.read_text())
    sources = load(evidence / 'sources.json')
    current_files = [p for p in pathlib.Path(__file__).resolve().parent.iterdir() if p.is_file()]
    current_files.append(REPO / 'wp/outils/bascule/audit')
    current_names = {str(p.relative_to(REPO)).replace('\\', '/') for p in current_files}
    assert set(sources) == current_names, 'SOURCE_INVENTORY_DRIFT'
    for relative, digest in sources.items():
        source = REPO / relative
        assert source.is_file() and hashlib.sha256(source.read_bytes()).hexdigest() == digest, 'SOURCE_DRIFT:' + relative
    assert any(c['check'] == 'cleanup' and c['detail']['absent'] for c in runner['checks'])
    # Verify Docker is responding, then semantic absence of the exact owned runner.
    docker = ['wsl.exe', '-d', 'Ubuntu', '--', 'docker']
    live = subprocess.run(docker + ['version', '--format', '{{.Server.Version}}'], capture_output=True, text=True, timeout=30)
    assert live.returncode == 0
    name = runner['container']
    assert re.fullmatch(r'imagine-a02-audit-[a-f0-9]{12}', name)
    gone = subprocess.run(docker + ['inspect', name], capture_output=True, text=True, timeout=30)
    assert gone.returncode != 0 and re.search(r'no such (object|container)', gone.stderr, re.I)
    print(json.dumps({'status': 'PASS', 'evidence': str(evidence), 'counts': counts, 'total_assertions': sum(counts.values()), 'current_source_hashes_match': True, 'container_absent': True, 'database_fingerprints_equal': ['classic', 'hpos']}, indent=2))
    return 0

if __name__ == '__main__':
    sys.exit(main())
