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
    return b.cmd(['python3', '/subject/a12/confine.py', '--wp-path='+str(site), '--output='+str(out), '--audit='+str(audit), *extra], check=False)

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
    $dynamic = 'a12_dynamic';
    register_post_type($dynamic, []);
    register_taxonomy($dynamic . '_tax', ['a12_article'], []);
    register_post_type('a12_removed', []);
    unregister_post_type('a12_removed');
    register_taxonomy('a12_removed_tax', ['a12_article'], []);
    unregister_taxonomy('a12_removed_tax');
    if (false) { register_post_type('a12_never', []); }
    if (false) { register_taxonomy('a12_never_tax', ['a12_article'], []); }
});
if (getenv('A12_CONFINED') === '1') {
    global $wpdb;
    require_once ABSPATH . 'wp-includes/pluggable.php';
    $GLOBALS['a12_early_guards'] = [
        'before_plugins_loaded' => !did_action('plugins_loaded'),
        'native_write_denied' => $wpdb->query('UPDATE wp_posts SET ID=ID WHERE 1=0') === false,
        'server_write_denied' => @mysqli_query($wpdb->dbh, 'UPDATE wp_posts SET ID=ID WHERE 1=0') === false && mysqli_errno($wpdb->dbh) === 1792,
        'file_create_denied' => @file_put_contents(ABSPATH . 'a12-write-canary', 'FORBIDDEN') === false,
        'file_truncate_denied' => @file_put_contents(ABSPATH . 'index.php', 'FORBIDDEN') === false,
        'http_denied' => is_wp_error(wp_remote_get('https://must-not-connect.invalid/')),
        'mail_denied' => wp_mail('fiction@example.org', 'A12', 'A12') === false,
        'cron_denied' => wp_schedule_single_event(time() + 9999, 'a12_early_forbidden') === false,
        'direct_mail_disabled' => !function_exists('mail'),
    ];
    echo 'A12_BOOT_OUTPUT_PRIVATE_CANARY';
}
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
    b.check(storage+':exact_runtime_registry_dynamic_not_never', report['registry']['runtime_verified'] is True and 'a12_dynamic' in rows and 'a12_never' not in rows and set(rows) == set(oracle['runtime_post_types']))
    b.check(storage+':exact_runtime_taxonomies', set(tax) == set(oracle['runtime_taxonomies']))
    b.check(storage+':dynamic_taxonomy_excludes_unexecuted_and_removed', 'a12_dynamic_tax' in tax and not {'a12_never_tax', 'a12_removed_tax'}.intersection(tax) and 'a12_removed' not in rows)
    b.check(storage+':dynamic_declarant_is_executed_mu', rows['a12_dynamic']['declarations'] == row['declarations'] and tax['a12_dynamic_tax']['declarations'] == row['declarations'])
    b.check(storage+':native_core_and_woocommerce_declarants', rows['post']['declarations'] == [{'owner': 'core', 'file': 'wp-includes/post.php'}] and rows['product']['declarations'] == [{'owner': 'plugin', 'file': 'wp-content/plugins/woocommerce/includes/class-wc-post-types.php'}])
    gap = {'runtime_missing_from_snapshot': sorted(set(oracle['runtime_post_types'])-set(rows)), 'source_candidates_not_runtime': sorted(k for k,v in rows.items() if v['declarations'] and k not in oracle['runtime_post_types'])}
    (OUT/(storage+'-registry-gap.json')).write_text(json.dumps(gap, indent=2)+'\n')
    b.check(storage+':runtime_gap_empty', not any(gap.values()))
    b.check(storage+':registered_totals_match_oracle', report['registry']['post_type_count'] == len(oracle['runtime_post_types']) and report['registry']['taxonomy_count'] == len(oracle['runtime_taxonomies']))
    fields = {x['key']: x['content_count'] for x in row['metadata_keys']}
    b.check(storage+':metadata_distinct_owners_not_row_count', fields['a12_field'] == oracle['metadata_content_count'] == 5)
    t = tax['a12_rubrique']
    b.check(storage+':exact_taxonomy_terms_top_twenty', t['term_count'] == oracle['term_count'] == 23 and t['top_terms'] == oracle['top_terms'] and len(t['top_terms']) == 20)
    b.check(storage+':taxonomy_distinct_content_statuses', t['content_count'] == 4 and t['states'] == {'draft': 1, 'private': 1, 'publish': 2})
    b.check(storage+':taxonomy_publication_dates', t['first_published_utc'] == row['first_published_utc'] and t['last_published_utc'] == row['last_published_utc'])
    attachments = report['attachments']
    expected_pdf_bytes = sum(x['bytes'] for x in oracle['attachments'] if x['mime'] == 'application/pdf')
    pdf = next(x for x in attachments['by_mime'] if x['mime'] == 'application/pdf')
    b.check(storage+':two_pdfs_exact_sizes_one_orphan', attachments['pdf_count'] == 2 and attachments['orphan_count'] == oracle['all_orphan_count'] and pdf['count'] == 2 and pdf.get('orphan_count') == 1 and pdf['bytes'] == expected_pdf_bytes and attachments['missing_files'] == 0)
    png = next(x for x in attachments['by_mime'] if x['mime'] == 'image/png')
    b.check(storage+':non_pdf_size', png['bytes'] == next(x['bytes'] for x in oracle['attachments'] if x['mime'] == 'image/png'))
    links = {x['key']: x for x in report['product_links']}
    b.check(storage+':distinct_scalar_product_links', links['_a12_product_id']['linked_contents'] == 2 and links['_a12_product_id']['distinct_pairs'] == 2)
    b.check(storage+':case_sensitive_link_keys', links['_A12_product_id']['linked_contents'] == 1 and links['_A12_product_id']['distinct_pairs'] == 1)
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
    raw = b.cmd(['php', '/subject/a12/inventorier-contenus', '--wp-path='+str(site), '--output='+str(OUT/(storage+'-raw')), '--audit='+str(auditdir/'audit.json')], check=False)
    b.check(storage+':guard:unconfined_launcher', raw.returncode == 1 and raw.stderr == 'A12_CONFINEMENT_REQUIRED\n' and not (OUT/(storage+'-raw')).exists())
    import shutil
    canonical = pathlib.Path('/checkout/wp/outils/bascule')
    if not canonical.exists():
        canonical.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree('/subject', canonical)
    bad = b.cmd(['python3', str(canonical/'a12/confine.py'), '--wp-path='+str(site), '--audit='+str(auditdir/'audit.json'), '--output=/checkout/forbidden'], check=False)
    b.check(storage+':guard:canonical_repository', bad.returncode == 1 and bad.stderr == 'A12_OUTPUT_UNSAFE\n' and not pathlib.Path('/checkout/forbidden').exists())
    wrong = OUT/(storage+'-wrong-audit')
    wrong.mkdir()
    photo = json.loads((auditdir/'audit.json').read_text())
    photo['sections']['commerce']['order_storage'] = 'hpos' if storage == 'classic' else 'classic'
    (wrong/'audit.json').write_text(json.dumps(photo))
    bad = inventory(site, OUT/(storage+'-wrong-storage'), wrong/'audit.json')
    b.check(storage+':guard:audit_storage_mismatch', bad.returncode == 1 and bad.stderr == 'A12_AUDIT_STORAGE_MISMATCH\n' and not (OUT/(storage+'-wrong-storage')).exists())
    (wrong/'audit.json').write_text('{"schema":"wrong","read_only":true}')
    bad = inventory(site, OUT/(storage+'-wrong-schema'), wrong/'audit.json')
    b.check(storage+':guard:audit_schema', bad.returncode == 1 and bad.stderr == 'A12_AUDIT_GUARD\n' and not (OUT/(storage+'-wrong-schema')).exists())
    incomplete = pathlib.Path('/incomplete/a12')
    incomplete.mkdir(parents=True, exist_ok=True)
    shutil.copyfile('/subject/a12/inventorier-contenus', incomplete/'inventorier-contenus')
    bad = b.cmd(['php', str(incomplete/'inventorier-contenus')], check=False)
    b.check(storage+':guard:missing_dependency_closed_error', bad.returncode == 1 and re.fullmatch(r'A12_[A-Z_]+\n', bad.stderr) is not None and bad.stdout == '')
    # File-only negative variants restore the precise original path and bytes.
    pdfpath = next(site.rglob('first.pdf'))
    held = pathlib.Path('/scratch/held-'+storage+'.pdf')
    pdfpath.rename(held)
    try:
        bad = inventory(site, OUT/(storage+'-missing-media'), auditdir/'audit.json')
        variant = json.loads((OUT/(storage+'-missing-media')/'contenus.json').read_text()) if bad.returncode == 0 else {}
        b.check(storage+':missing_media_not_invented_size', bad.returncode == 0 and variant['attachments']['missing_files'] == 1 and next(x for x in variant['attachments']['by_mime'] if x['mime'] == 'application/pdf')['bytes'] == 28)
        pdfpath.symlink_to(held)
        bad = inventory(site, OUT/(storage+'-symlink-media'), auditdir/'audit.json')
        b.check(storage+':guard:symlink_media', bad.returncode == 1 and bad.stderr == 'A11_SYMLINK_UNSUPPORTED '+json.dumps({'file':pdfpath.relative_to(site).as_posix()},separators=(',',':'))+'\n' and not (OUT/(storage+'-symlink-media')).exists())
    finally:
        if pdfpath.is_symlink():
            pdfpath.unlink()
        held.rename(pdfpath)
    (site/'wp-config.php').write_text(config.replace("define('DB_USER', 'a02_"+storage+"')", "define('DB_USER', 'root')"))
    try:
        probe = b.cmd(['python3', '/opt/a12/probe.py'], env={'A12_SITE': str(site)}, check=False)
        (OUT/(storage+'-readonly-probe.json')).write_text(probe.stdout)
        b.check(storage+':root_transaction_blocks_writes_and_system_confines_bootstrap', probe.returncode == 0 and all(json.loads(probe.stdout).values()), {'exit_code': probe.returncode, 'stderr': probe.stderr[:120]})
    finally:
        (site/'wp-config.php').write_text(config)
    (site/'wp-config.php').write_text(config.replace("define('DB_PASSWORD', '')", "define('DB_PASSWORD', getenv('A12_SECRET_PRIVATE_CANARY'))"))
    try:
        bad = inventory(site, OUT/(storage+'-dynamic'), auditdir/'audit.json')
        b.check(storage+':guard:dynamic_config', bad.returncode == 1 and bad.stderr == 'A02_CONFIG_NON_LITERAL\n')
    finally:
        (site/'wp-config.php').write_text(config)
    for constant in ['WPMU_PLUGIN_DIR', 'UPLOADS']:
        (site/'wp-config.php').write_text(config + "\ndefine('"+constant+"', '/forbidden-layout');\n")
        try:
            bad = inventory(site, OUT/(storage+'-layout-'+constant.lower()), auditdir/'audit.json')
            b.check(storage+':guard:layout:'+constant, bad.returncode == 1 and bad.stderr == 'A11_CONFIG_OVERRIDE_UNSUPPORTED '+json.dumps({'constant':constant},separators=(',',':'))+'\n')
        finally:
            (site/'wp-config.php').write_text(config)
    dropin = site/'wp-content/object-cache.php'
    dropin.write_text("<?php throw new RuntimeException('A12_NEVER_EXECUTE_DROPIN');")
    try:
        bad = inventory(site, OUT/(storage+'-dropin'), auditdir/'audit.json')
        b.check(storage+':guard:dropin_before_execution', bad.returncode == 1 and bad.stderr == 'A11_DROPIN_UNSUPPORTED '+json.dumps({'file':'wp-content/object-cache.php'},separators=(',',':'))+'\n')
    finally:
        dropin.unlink()
    after = b.fingerprint(db)
    (OUT/(storage+'-db-after.json')).write_text(json.dumps(after, indent=2)+'\n')
    b.check(storage+':all_tables_identical_including_scheduler', before == after, {'before': before['logical_sha256'], 'after': after['logical_sha256'], 'tables': len(before['tables'])})
    b.check(storage+':site_files_identical', fb == b.files(site), {'before': fb, 'after': b.files(site)})
    b.check(storage+':config_never_executed', not pathlib.Path('/scratch/a02-bootstrap-trap').exists())

b.run_storage = run_storage
if __name__ == '__main__':
    php_sources = sorted(pathlib.Path('/subject/a12').glob('*.php')) + sorted(pathlib.Path('/opt/a12').glob('*.php')) + [pathlib.Path('/subject/a12/inventorier-contenus')]
    for p in php_sources:
        b.check('a12_lint:'+p.name, b.cmd(['php', '-l', str(p)], check=False).returncode == 0)
    exit_code = b.main()
    path = OUT/'result.json'
    result = json.loads(path.read_text())
    result['suite'] = 'A12-bounded-native-readonly-inventory'
    result['readiness'] = exit_code == 0
    result['unmet_requirements'] = [] if exit_code == 0 else ['Dedicated native suite failed.']
    path.write_text(json.dumps(result, indent=2)+'\n')
    sys.exit(exit_code)
