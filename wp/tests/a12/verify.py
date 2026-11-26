"""Verify native A12 evidence, exact source membership and real safety receipts."""
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
    ap.add_argument('--save', action='store_true')
    args = ap.parse_args()
    out = args.packet.resolve()
    checks = []
    def check(name, ok):
        checks.append({'check': name, 'status': 'PASS' if ok else 'FAIL'})
    try:
        owned = json.loads((out/'sources.json').read_text())
        check('exact_current_source_inventory_and_hashes', owned == run.manifest(['wp/tests/a12', 'wp/outils/bascule/a12']))
        protected = json.loads((out/'protected-sources.json').read_text())
        check('frozen_a02_a11_execution_dependencies_present', bool(protected))
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
        check('native_readiness_without_unmet_requirements', native['readiness'] is True and native['unmet_requirements'] == [])
        names = {x['check'] for x in native['checks']}
        for storage in ['classic', 'hpos']:
            required = ['exact_runtime_registry_dynamic_not_never', 'exact_runtime_taxonomies',
                'native_core_and_woocommerce_declarants', 'dynamic_declarant_is_executed_mu',
                'root_transaction_blocks_writes_and_system_confines_bootstrap',
                'metadata_distinct_owners_not_row_count', 'two_pdfs_exact_sizes_one_orphan',
                'all_tables_identical_including_scheduler', 'site_files_identical', 'config_never_executed',
                'guard:disjoint_launcher:ancestor-site', 'guard:disjoint_php:ancestor-site',
                'guard:disjoint_launcher:root', 'guard:disjoint_php:root',
                'link_collision_and_noncollision_fixture', 'non_posts_domain_unavailable:link_category',
                'non_posts_domain_unavailable:a12_mixed_tax']
            check(storage+':mandatory_native_cases_present', all(storage+':'+key in names for key in required))
            before = json.loads((out/(storage+'-db-before.json')).read_text())
            after = json.loads((out/(storage+'-db-after.json')).read_text())
            check(storage+':independent_all_table_snapshot_equality', before == after and len(before['tables']) > 20)
            check(storage+':scheduler_in_snapshot', all(k in before['tables'] for k in ['wp_options', 'wp_actionscheduler_actions', 'wp_actionscheduler_logs']))
            data = json.loads((out/(storage+'-contents')/'contenus.json').read_text())
            check(storage+':schema_storage_readonly', data['schema'] == 'imagine-a12-content-v1' and data['storage'] == storage and data['read_only'] is True)
            oracle = json.loads((out/(storage+'-oracle.json')).read_text())
            types = {row['name'] for row in data['post_types'] if row['registration'] == 'runtime_registered'}
            tax = {row['name'] for row in data['taxonomies'] if row['registration'] == 'runtime_registered'}
            check(storage+':exact_native_runtime_sets', data['registry']['runtime_verified'] is True and types == set(oracle['runtime_post_types']) and tax == set(oracle['runtime_taxonomies']))
            check(storage+':dynamic_included_conditional_excluded', 'a12_dynamic' in types and 'a12_never' not in types and 'a12_dynamic_tax' in tax and 'a12_never_tax' not in tax)
            check(storage+':exact_registered_totals', data['registry']['post_type_count'] == len(types) and data['registry']['taxonomy_count'] == len(tax))
            check(storage+':real_link_collision_and_noncollision',oracle['link_cases']=={'collision_exists':True,'noncollision_post_absent':True,'links':2})
            for taxonomy, domains in [('link_category',['link']),('a12_mixed_tax',['a12_article','link'])]:
                row=next(x for x in data['taxonomies'] if x['name']==taxonomy)
                check(storage+':unavailable_not_posts_invented:'+taxonomy,row['object_types']==domains
                    and row['count_status']=='unavailable_non_posts_or_mixed'
                    and all(row[k] is None for k in ['content_count','states','first_published_utc','last_published_utc','top_terms']))
            safety = json.loads((out/(storage+'-readonly-probe.json')).read_text())
            check(storage+':same_session_root_sql_kernel_and_early_guards', len(safety) >= 14 and all(value is True for value in safety.values())
                and {'site_create','site_truncate','site_rename','site_unlink','site_mkdir'}.issubset(safety))
            check(storage+':audit_bound_by_exact_bytes', data['audit_sha256'] == hashlib.sha256((out/(storage+'-audit')/'audit.json').read_bytes()).hexdigest())
            gap = json.loads((out/(storage+'-registry-gap.json')).read_text())
            check(storage+':empty_native_registry_gap', gap == {'runtime_missing_from_snapshot': [], 'source_candidates_not_runtime': []})
            for name in ['contenus.json', 'contenus.md']:
                payload = (out/(storage+'-contents')/name).read_text()
                check(storage+':privacy:'+name, not re.search(r'PRIVATE_CANARY|@example|DB_PASSWORD|/scratch|first\.pdf|second\.pdf|post_title|post_content|post_author|meta_value', payload))
        style = json.loads((out/'style/style.json').read_text())
        check('strict_psr12_pass', style['exit_code'] == 0 and style['phpcs_exit'] == 0 and style['totals']['errors'] == 0 and style['totals']['warnings'] == 0)
        check('style_exact_source_binding', style['sources'] == owned)
        check('style_cleanup', any(x['check'] == 'cleanup' and x['status'] == 'PASS' for x in style['checks']))
        totals['style.json'] = len(style['checks'])
        check('real_kernel_landlock_abi', int((out/'landlock-abi.txt').read_text()) >= 3)
        check('static_registry_parser_removed', not (run.REPO/'wp/outils/bascule/a12/Declarations.php').exists())
        missing = run.b.call(['inspect', runner['container']], check=False)
        check('exact_owned_runner_still_absent', missing.returncode != 0 and re.search(r'no such (object|container)', missing.stderr, re.I) is not None)
    except Exception as exc:
        check('verification_exception:'+type(exc).__name__, False)
        totals = locals().get('totals', {})
    exit_code = int(any(x['status'] != 'PASS' for x in checks))
    result = {'suite': 'A12-final-evidence-integrity', 'verdict': 'NATIVE_VERIFIE' if exit_code == 0 else 'NON_PRET', 'readiness': exit_code == 0, 'counts': totals, 'checks': checks, 'exit_code': exit_code}
    if args.save:
        (out/'verification.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf8')
    print(json.dumps(result, indent=2))
    return result['exit_code']

if __name__ == '__main__':
    sys.exit(main())
