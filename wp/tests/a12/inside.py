"""A12 native integration; inherited A02 files are read-only, not patched."""
import importlib.util
import json
import pathlib
import re
import sys
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('a02_native', '/opt/a02/inside.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
OUT = pathlib.Path('/report')
original_check = b.check

def safe_check(name, ok, detail=None):
    if name.endswith(':commercial_fixture') and isinstance(detail, dict):
        detail = {k: detail[k] for k in ['versions', 'hpos', 'subscriptions', 'rules', 'restriction_real']}
    return original_check(name, ok, detail)
b.check = safe_check

def inventory(site, out, audit, *extra):
    return b.cmd(['php', '/subject/a12/inventorier-contenus', '--wp-path='+str(site), '--output='+str(out), '--audit='+str(audit), *extra], check=False)

def run_storage(storage):
    site, db, _ = b.install(storage)
    (OUT/(storage+'-seed.json')).unlink()
    config = (site/'wp-config.php').read_text()
    writable = config.replace("define('DB_USER', 'a02_"+storage+"')", "define('DB_USER', 'root')").split("\nfile_put_contents('/scratch/a02-bootstrap-trap'")[0]
    (site/'wp-config.php').write_text(writable)
    mu = site/'wp-content/mu-plugins/a12-declarations.php'
    mu.write_text("""<?php
/* Plugin Name: A12 fixture declarations */
add_action('init', function () {
    register_post_type('a12_article', ['public' => true]);
    register_post_type('a12_empty', ['public' => false]);
    register_taxonomy('a12_rubrique', ['a12_article'], ['public' => true]);
    if (false) { register_post_type('a12_never', []); }
});
""")
    (site/'wp-content/themes/a02-child/functions.php').write_text("<?php add_action('init', function () { register_post_type('a12_theme', []); });")
    (site/'wp-content/plugins/inactive-fixture/decl.php').write_text("<?php register_post_type('a12_inactive', []);")
    try:
        seeded = b.wp(site, ['eval-file', '/opt/a12/seed.php', '--use-include'], check=False)
        if seeded.returncode:
            (OUT/(storage+'-seed-error.log')).write_text(seeded.stdout+seeded.stderr)
            raise RuntimeError('A12_NATIVE_SEED_FAILED')
        oracle = json.loads(next(x[9:] for x in seeded.stdout.splitlines() if x.startswith('A12_JSON=')))
    finally:
        (site/'wp-config.php').write_text(config)
    (OUT/(storage+'-oracle.json')).write_text(json.dumps(oracle, indent=2)+'\n')
    b.check(storage+':native_registration_and_storage', all(oracle['runtime_registered'].values()) and oracle['hpos'] == (storage == 'hpos'))
    auditdir = OUT/(storage+'-audit')
    audit = b.audit(site, auditdir)
    b.check(storage+':a02_audit_compatible', audit.returncode == 0)
    before = b.fingerprint(db)
    fb = b.files(site)
    (OUT/(storage+'-db-before.json')).write_text(json.dumps(before, indent=2)+'\n')
    target = OUT/(storage+'-contents')
    p = inventory(site, target, auditdir/'audit.json')
    b.check(storage+':inventory_implemented', pathlib.Path('/subject/a12/inventorier-contenus').is_file())
    b.check(storage+':cli_success', p.returncode == 0, {'exit_code': p.returncode, 'stderr': p.stderr if re.fullmatch(r'A(?:12|02)_[A-Z_]+\n', p.stderr) else 'suppressed'})
    report = json.loads((target/'contenus.json').read_text())
    rows = {r['name']: r for r in report['post_types']}
    tax = {r['name']: r for r in report['taxonomies']}
    row = rows['a12_article']
    b.check(storage+':exact_states_and_distinct_content_count', row['states'] == oracle['states'] and row['content_count'] == 5)
    b.check(storage+':publication_utc_not_drafts_or_trash', row['first_published_utc'] == '2024-02-03T11:00:00Z' and row['last_published_utc'] == '2025-02-03T11:00:00Z')
    b.check(storage+':empty_declared_type', rows['a12_empty']['content_count'] == 0 and rows['a12_empty']['first_published_utc'] is None)
    b.check(storage+':source_mu_and_theme', any(x['file'] == 'wp-content/mu-plugins/a12-declarations.php' and x['owner'] == 'mu_plugin' for x in row['declarations']) and rows['a12_theme']['declarations'] == [{'owner': 'theme', 'file': 'wp-content/themes/a02-child/functions.php'}])
    b.check(storage+':inactive_source_excluded', 'a12_inactive' not in rows)
    b.check(storage+':no_false_runtime_claim', report['registry']['runtime_verified'] is False and rows['a12_never']['registration'] == 'literal_source_candidate_not_runtime_verified')
    fields = {x['key']: x['content_count'] for x in row['metadata_keys']}
    b.check(storage+':metadata_distinct_owners_not_row_count', fields['a12_field'] == oracle['metadata_content_count'] == 5)
    t = tax['a12_rubrique']
    b.check(storage+':exact_taxonomy_terms_top_twenty', t['term_count'] == oracle['term_count'] == 23 and t['top_terms'] == oracle['top_terms'] and len(t['top_terms']) == 20)
    b.check(storage+':taxonomy_distinct_content_statuses', t['content_count'] == 4 and t['states'] == {'draft': 1, 'private': 1, 'publish': 2})
    b.check(storage+':taxonomy_publication_dates', t['first_published_utc'] == row['first_published_utc'] and t['last_published_utc'] == row['last_published_utc'])
    attachments = report['attachments']
    expected_pdf_bytes = sum(x['bytes'] for x in oracle['attachments'] if x['mime'] == 'application/pdf')
    pdf = next(x for x in attachments['by_mime'] if x['mime'] == 'application/pdf')
    b.check(storage+':two_pdfs_exact_sizes_one_orphan', attachments['pdf_count'] == 2 and attachments['orphan_count'] == 1 and pdf['count'] == 2 and pdf['bytes'] == expected_pdf_bytes and attachments['missing_files'] == 0)
    png = next(x for x in attachments['by_mime'] if x['mime'] == 'image/png')
    b.check(storage+':non_pdf_size', png['bytes'] == next(x['bytes'] for x in oracle['attachments'] if x['mime'] == 'image/png'))
    links = {x['key']: x for x in report['product_links']}
    b.check(storage+':distinct_scalar_product_links', links['_a12_product_id']['linked_contents'] == 2 and links['_a12_product_id']['distinct_pairs'] == 2)
    b.check(storage+':reverse_product_to_article_link', links['_a12_article_id']['linked_contents'] == 1 and links['_a12_article_id']['distinct_pairs'] == 1)
    b.check(storage+':serialized_link_not_interpreted', links['_a12_product_ids']['distinct_pairs'] == 0 and links['_a12_product_ids']['non_scalar_rows'] == 1)
    full = (target/'contenus.json').read_text()+(target/'contenus.md').read_text()+p.stdout+p.stderr
    b.check(storage+':privacy_no_titles_values_contacts_paths', not re.search(r'PRIVATE_CANARY|@example|DB_PASSWORD|/scratch|first\.pdf|second\.pdf|post_title|post_content|post_author|meta_value', full))
    b.check(storage+':modes', target.stat().st_mode & 0o777 == 0o700 and all(x.stat().st_mode & 0o777 == 0o600 for x in target.iterdir()))
    repeat = OUT/(storage+'-repeat')
    replay = inventory(site, repeat, auditdir/'audit.json')
    other = json.loads((repeat/'contenus.json').read_text()) if replay.returncode == 0 else {}
    b.check(storage+':replay_exact', replay.returncode == 0 and all(other.get(k) == report[k] for k in ['post_types', 'taxonomies', 'attachments', 'product_links', 'registry']))
    for label, dest, extras in [
        ('existing_output', target, []), ('web_output', site/'forbidden', []),
        ('source_output', pathlib.Path('/subject/forbidden'), []),
        ('bad_argument', OUT/(storage+'-badarg'), ['--unknown=yes']),
    ]:
        bad = inventory(site, dest, auditdir/'audit.json', *extras)
        b.check(storage+':guard:'+label, bad.returncode == 1 and (dest == target or not dest.exists()))
    link = OUT/(storage+'-link')
    link.symlink_to(site, target_is_directory=True)
    bad = inventory(site, link/'forbidden', auditdir/'audit.json')
    b.check(storage+':guard:symlink_parent_web', bad.returncode == 1 and not (site/'forbidden').exists())
    link.unlink()
    no_audit = b.cmd(['php', '/subject/a12/inventorier-contenus', '--wp-path='+str(site), '--output=/report/no-audit-'+storage], check=False)
    b.check(storage+':guard:missing_audit', no_audit.returncode == 1 and no_audit.stderr == 'A12_USAGE\n')
    (site/'wp-config.php').write_text(config.replace("define('DB_USER', 'a02_"+storage+"')", "define('DB_USER', 'root')"))
    try:
        probe = b.cmd(['php', '/opt/a12/readonly-probe.php'], env={'A12_SITE': str(site)}, check=False)
        b.check(storage+':root_transaction_blocks_writes', probe.returncode == 0 and json.loads(probe.stdout)['blocked'])
    finally:
        (site/'wp-config.php').write_text(config)
    (site/'wp-config.php').write_text(config.replace("define('DB_PASSWORD', '')", "define('DB_PASSWORD', getenv('A12_SECRET_PRIVATE_CANARY'))"))
    try:
        bad = inventory(site, OUT/(storage+'-dynamic'), auditdir/'audit.json')
        b.check(storage+':guard:dynamic_config', bad.returncode == 1 and bad.stderr == 'A02_CONFIG_NON_LITERAL\n')
    finally:
        (site/'wp-config.php').write_text(config)
    after = b.fingerprint(db)
    (OUT/(storage+'-db-after.json')).write_text(json.dumps(after, indent=2)+'\n')
    b.check(storage+':all_tables_identical_including_scheduler', before == after, {'before': before['logical_sha256'], 'after': after['logical_sha256'], 'tables': len(before['tables'])})
    b.check(storage+':site_files_identical', fb == b.files(site), {'before': fb, 'after': b.files(site)})
    b.check(storage+':never_bootstrap', not pathlib.Path('/scratch/a02-bootstrap-trap').exists())

b.run_storage = run_storage
if __name__ == '__main__':
    for p in sorted(pathlib.Path('/subject/a12').glob('*.php')) + sorted(pathlib.Path('/opt/a12').glob('*.php')):
        b.check('a12_lint:'+p.name, b.cmd(['php', '-l', str(p)], check=False).returncode == 0)
    exit_code = b.main()
    path = OUT/'result.json'
    result = json.loads(path.read_text())
    result['suite'] = 'A12-bounded-native-readonly-inventory'
    result['readiness'] = False
    result['unmet_requirements'] = ['Exhaustive runtime registry without WordPress bootstrap is not proven.', 'Shared test image preparation reserved for parent; not run here.']
    path.write_text(json.dumps(result, indent=2)+'\n')
    sys.exit(exit_code)
