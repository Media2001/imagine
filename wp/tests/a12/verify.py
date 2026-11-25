"""Verify final A12 receipts and current source membership; never authorizes PRET."""
import argparse
import hashlib
import json
import pathlib
import re
import sys
sys.dont_write_bytecode = True
import run


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('packet', type=pathlib.Path)
    args = ap.parse_args()
    out = args.packet.resolve()
    checks = []
    def check(name, ok):
        checks.append({'check': name, 'status': 'PASS' if ok else 'FAIL'})
    try:
        owned = json.loads((out/'sources.json').read_text())
        check('exact_current_source_inventory_and_hashes', owned == run.manifest(['wp/tests/a12', 'wp/outils/bascule/a12']))
        protected = json.loads((out/'protected-sources.json').read_text())
        check('immutable_a02_dependency_hashes', protected == run.manifest(run.PROTECTED))
        totals = {}
        for filename in ['unit.json', 'result.json', 'runner.json']:
            receipt = json.loads((out/filename).read_text())
            names = [x['check'] for x in receipt['checks']]
            check(filename+':actual_success', receipt['exit_code'] == 0 and len(names) > 0 and all(x['status'] == 'PASS' for x in receipt['checks']))
            # A02 native lint and A12 native lint have different prefixes.
            check(filename+':no_duplicate_assertions', len(names) == len(set(names)))
            totals[filename] = len(names)
        runner = json.loads((out/'runner.json').read_text())
        check('native_not_unit_only', runner['mode'] == 'native')
        must = ['isolation_before', 'isolation_after', 'cleanup_exact_owned_runner', 'owned_sources_stable', 'protected_sources_unchanged']
        check('mandatory_runner_gates', set(must).issubset({x['check'] for x in runner['checks']}))
        native = json.loads((out/'result.json').read_text())
        check('honest_partial_readiness', native['readiness'] is False and len(native['unmet_requirements']) >= 1)
        for storage in ['classic', 'hpos']:
            before = json.loads((out/(storage+'-db-before.json')).read_text())
            after = json.loads((out/(storage+'-db-after.json')).read_text())
            check(storage+':independent_all_table_snapshot_equality', before == after and len(before['tables']) > 20)
            check(storage+':scheduler_in_snapshot', all(k in before['tables'] for k in ['wp_options', 'wp_actionscheduler_actions', 'wp_actionscheduler_logs']))
            data = json.loads((out/(storage+'-contents')/'contenus.json').read_text())
            check(storage+':schema_storage_readonly', data['schema'] == 'imagine-a12-content-v1' and data['storage'] == storage and data['read_only'] is True)
            check(storage+':explicit_runtime_limit', data['registry']['runtime_verified'] is False)
            check(storage+':audit_bound_by_exact_bytes', data['audit_sha256'] == hashlib.sha256((out/(storage+'-audit')/'audit.json').read_bytes()).hexdigest())
            gap = json.loads((out/(storage+'-registry-gap.json')).read_text())
            check(storage+':observed_unmet_runtime_registry', 'a12_dynamic' in gap['runtime_missing_from_snapshot'] and 'a12_never' in gap['source_candidates_not_runtime'])
            for name in ['contenus.json', 'contenus.md']:
                payload = (out/(storage+'-contents')/name).read_text()
                check(storage+':privacy:'+name, not re.search(r'PRIVATE_CANARY|@example|DB_PASSWORD|/scratch|first\.pdf|second\.pdf|post_title|post_content|post_author|meta_value', payload))
        style = json.loads((out/'style/style.json').read_text())
        check('strict_psr12_pass', style['exit_code'] == 0 and style['phpcs_exit'] == 0 and style['totals']['errors'] == 0 and style['totals']['warnings'] == 0)
        check('style_exact_source_binding', style['sources'] == owned)
        check('style_cleanup', any(x['check'] == 'cleanup' and x['status'] == 'PASS' for x in style['checks']))
        totals['style.json'] = len(style['checks'])
        check('no_pret', not (run.REPO/'production/A-12/PRET').exists())
        missing = run.b.call(['inspect', runner['container']], check=False)
        check('exact_owned_runner_still_absent', missing.returncode != 0 and re.search(r'no such (object|container)', missing.stderr, re.I) is not None)
    except Exception as exc:
        check('verification_exception:'+type(exc).__name__, False)
        totals = locals().get('totals', {})
    result = {'suite': 'A12-final-evidence-integrity', 'verdict': 'PARTIEL_NON_PRET', 'readiness': False, 'counts': totals, 'checks': checks, 'exit_code': int(any(x['status'] != 'PASS' for x in checks))}
    print(json.dumps(result, indent=2))
    return result['exit_code']

if __name__ == '__main__':
    sys.exit(main())
