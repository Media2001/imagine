"""A33 real WordPress + SQL/kernel immutability, one classic store only."""
import ctypes
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import time
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('fixture', '/opt/a02/inside.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
OUT = Path('/report')


def cmd(args, check=True, env=None, data=None, timeout=240):
    p = subprocess.run(args, input=data, text=True, encoding='utf-8', errors='strict', capture_output=True, env={**os.environ, **(env or {})}, timeout=timeout)
    if check and p.returncode:
        raise RuntimeError('A33_FIXTURE_COMMAND_' + str(p.returncode))
    return p


b.cmd = cmd
basecheck = b.check

def check(name, ok, detail=None):
    if name.endswith(':commercial_fixture'):
        detail = {'storage': 'classic', 'versions': detail['versions']}
    return basecheck(name, ok, detail)


b.check = check


def weight(count, present, missing, known, imported=False):
    return {'count': count, 'present': present, 'missing': missing, 'known_bytes': known, 'total_bytes': ('inconnu après import' if imported else 'inconnu fichiers absents') if missing else known}


def run_storage(storage):
    site, db, _ = b.install(storage)
    cfg = (site / 'wp-config.php').read_text(encoding='utf-8')
    rootcfg = cfg.replace("define('DB_USER', 'a02_" + storage + "')", "define('DB_USER', 'root')").split("\nfile_put_contents('/scratch/a02-bootstrap-trap'")[0]
    (site / 'wp-config.php').write_text(rootcfg, encoding='utf-8')
    try:
        seed = b.wp(site, ['eval-file', '/opt/a33/seed.php', '--use-include'])
        oracle = json.loads(next(s[9:] for s in seed.stdout.splitlines() if s.startswith('A33_JSON=')))
    finally:
        (site / 'wp-config.php').write_text(cfg, encoding='utf-8')
    (OUT / 'oracle.json').write_text(json.dumps(oracle), encoding='utf-8')
    mu = site / 'wp-content/mu-plugins/a33-runtime.php'
    nominal = '''<?php
register_post_type('a16_numero', ['public'=>false]);
register_post_type('a16_article', ['public'=>false]);
register_post_type('PRIVATE_TYPE_CANARY', ['public'=>false]);
register_post_type('OTHER_TYPE_CANARY', ['public'=>false]);
register_taxonomy('a16_theme', ['a16_article', 'a16_numero']);
register_taxonomy('a16_issue', 'a16_article');
if (getenv('A33_CONFINED') === '1') {
 add_filter('query', static function ($sql) {
  if (preg_match('/(?:FROM|JOIN)\\s+`?wp_(?:wc_orders|woocommerce_order_items)/i', $sql)) {throw new RuntimeException('A33_ORDER_READ');}
  return $sql;
 });
 global $wpdb; require_once ABSPATH.'wp-includes/pluggable.php';
 if ($wpdb->query('UPDATE wp_posts SET ID=ID WHERE 1=0') !== false
 || @mysqli_query($wpdb->dbh,'UPDATE wp_posts SET ID=ID WHERE 1=0') !== false
 || @file_put_contents(ABSPATH.'forbidden','NO') !== false
 || wp_mail('fictif@example.org','A33_PRIVATE_CANARY','A33_PRIVATE_CANARY') !== false
 || !is_wp_error(wp_remote_get('https://forbidden.invalid/'))
 || wp_schedule_single_event(time()+9999,'a33_forbidden') !== false
 || function_exists('mail') || function_exists('exec')) {throw new RuntimeException('A33_EARLY_GUARDS_FAILED');}
}
'''
    mu.write_text(nominal, encoding='utf-8')
    audit = OUT / 'audit'
    check('native_audit', b.audit(site, audit).returncode == 0)
    mapping = Path('/subject/a33/correspondance.exemple.json')
    counter = 0

    def inventory(label, config=mapping):
        nonlocal counter
        counter += 1
        output = OUT / ('r' + str(counter) + '-' + label)
        p = cmd(['python3', '/subject/a33/confine.py', '--wp-path=' + str(site), '--audit=' + str(audit / 'audit.json'), '--correspondance=' + str(config), '--output=' + str(output)], check=False)
        return p, output

    def clean(p, output):
        data = p.stdout + p.stderr + ''.join(f.read_text(encoding='utf-8') for f in output.rglob('*') if f.is_file())
        return not re.search('CANARY|/scratch|@|post_title|post_content|PRIVATE_TYPE', data)

    before, files = b.fingerprint(db), b.files(site)
    (OUT / 'db-before.json').write_text(json.dumps(before), encoding='utf-8')
    # Watch actual media inode opens/accesses ONLY around the subject, not oracle hashing.
    libc = ctypes.CDLL(None, use_errno=True)
    watch = libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
    assert watch >= 0
    observed = sorted((site / 'wp-content/uploads').glob('A33_FILE*'))
    assert len(observed) == 10
    for f in observed:
        assert libc.inotify_add_watch(watch, os.fsencode(f), 0x01 | 0x20) >= 0
    observed[0].read_bytes()
    check('media_watch_positive_inverse', bool(os.read(watch, 65536)))
    try:
        p, out = inventory('nominal')
        try:
            events = os.read(watch, 65536)
        except BlockingIOError:
            events = b''
    finally:
        os.close(watch)
    check('native_success', p.returncode == 0 and p.stdout == 'A33_OK archives.json archives.md\n' and p.stderr == '', {'exit': p.returncode, 'stderr_sha256': hashlib.sha256(p.stderr.encode()).hexdigest()})
    d = json.loads((out / 'archives.json').read_text(encoding='utf-8'))
    check('twelve_selects_ten_exact', d['selected_issues'] == 10 and len(oracle['issues']) == 12)
    expected = [{'type': 'article', 'type_group': 0, 'year': 2010, 'count': 1}, {'type': 'article', 'type_group': 0, 'year': 2012, 'count': 1}, {'type': 'autre', 'type_group': 1, 'year': 2023, 'count': 1}, {'type': 'autre', 'type_group': 2, 'year': 2023, 'count': 1}, {'type': 'numero', 'type_group': 0, 'year': 2010, 'count': 1}, {'type': 'numero', 'type_group': 0, 'year': 2012, 'count': 1}, {'type': 'post', 'type_group': 0, 'year': 2022, 'count': 1}, {'type': 'post', 'type_group': 0, 'year': 'inconnu', 'count': 1}]
    check('published_outside_exact_closed_types_years', d['published_outside'] == expected, d['published_outside'])
    check('outside_files_exact_years_missing_not_zero', d['outside_media_by_year'] == [{'year': 2010, 'files': weight(3, 2, 1, 18)}, {'year': 2012, 'files': weight(1, 1, 0, 13)}, {'year': 2022, 'files': weight(1, 1, 0, 0)}, {'year': 'inconnu', 'files': weight(1, 1, 0, 37)}])
    check('orphan_zero_and_missing_parent', d['orphan_media'] == weight(2, 2, 0, 52))
    check('recent_comparison_exact', d['recent_media'] == weight(3, 3, 0, 59))
    check('pdf_post_orphan_and_shared_deduplicated', d['recent_media'] == weight(3, 3, 0, 59) and d['orphan_media'] == weight(2, 2, 0, 52))
    check('unknown_year_attachment_json', d['outside_media_by_year'][-1] == {'year': 'inconnu', 'files': weight(1, 1, 0, 37)})
    check('tie_boundary_a16_id_order', [r for r in d['published_outside'] if r['type'] == 'numero'] == [expected[4], expected[5]] and d['outside_media_by_year'][1] == {'year': 2012, 'files': weight(1, 1, 0, 13)})
    check('nonpublished_parent_separate', d['other_media'] == weight(1, 1, 0, 31))
    check('no_media_content_open_or_access', events == b'')
    check('no_site_identifiers_all_nominal_channels', clean(p, out))
    check('db_identical_nominal', before == b.fingerprint(db))
    check('files_identical_nominal', files == b.files(site))
    repeat, rout = inventory('repeat')
    check('deterministic_replay', repeat.returncode == 0 and {f.name: f.read_bytes() for f in out.iterdir()} == {f.name: f.read_bytes() for f in rout.iterdir()})
    line = next(x for x in Path('/subject/README.md').read_text(encoding='utf-8').splitlines() if x.startswith('python3 wp/outils/bascule/a33/'))
    check('common_and_owned_readme_commands_identical', line in Path('/subject/a33/README.md').read_text(encoding='utf-8').splitlines())
    documented = shlex.split(line)
    docout = OUT / 'documented'
    replacements = {'wp/outils/bascule/a33/confine.py': '/subject/a33/confine.py', '/copie-verifiee': str(site), '/hors-web/audit-date/audit.json': str(audit / 'audit.json'), '/hors-web/correspondance.json': str(mapping), '/hors-web/archives-date': str(docout)}
    for i, token in enumerate(documented):
        for old, new in replacements.items():
            token = token.replace(old, new)
        documented[i] = token
    documented_run = cmd(documented, check=False)
    check('readme_only_exact_arguments', documented_run.returncode == 0 and json.loads((docout / 'archives.json').read_bytes()) == d, {'arguments': [s.split('=')[0] for s in documented[2:]]})
    for label, update in [('parent', {'liaison': {'source': 'post_parent', 'cle': 'post_parent'}}), ('taxonomy', {'numero_source': 'taxonomy', 'numero_type': 'a16_issue', 'date_cle': '_a33_date', 'liaison': {'source': 'taxonomy', 'cle': 'a16_issue'}})]:
        m = json.loads(mapping.read_bytes())
        m.update(update)
        config = OUT / ('variant-' + label + '.json')
        config.write_text(json.dumps(m), encoding='utf-8')
        q, dest = inventory('variant-' + label, config)
        variant = json.loads((dest / 'archives.json').read_bytes()) if dest.exists() else {}
        if label == 'parent':
            check('a16_variant_parent_exact', q.returncode == 0 and all(variant.get(k) == d[k] for k in d if k != 'mapping_sha256'))
        else:
            check('a16_variant_taxonomy_ten_no_term_post_id_inference', q.returncode == 0 and variant.get('selected_issues') == 10 and variant.get('recent_media') == weight(5, 4, 1, 70))
            check('pdf_taxonomy_and_multilink_deduplicated', variant.get('recent_media') == weight(5, 4, 1, 70) and variant.get('outside_media_by_year', [None])[0] == {'year': 2010, 'files': weight(1, 1, 0, 7)})
    shared = json.loads(mapping.read_bytes())
    shared.update(article_type='a16_numero', liaison={'source': 'post_parent', 'cle': 'post_parent'})
    shared_config = OUT / 'variant-shared-type.json'
    shared_config.write_text(json.dumps(shared), encoding='utf-8')
    q, dest = inventory('shared-type', shared_config)
    variant = json.loads((dest / 'archives.json').read_bytes()) if dest.exists() else {}
    check('shared_type_selected_issue_stays_kept', q.returncode == 0 and sum(r['count'] for r in variant.get('published_outside', []) if r['type'] == 'numero') == 2 and variant.get('recent_media') == weight(2, 2, 0, 40))
    forbidden_map = json.loads(mapping.read_bytes())
    forbidden_map['article_type'] = 'shop_order'
    forbidden_config = OUT / 'noneditorial.json'
    forbidden_config.write_text(json.dumps(forbidden_map), encoding='utf-8')
    bad, dest = inventory('noneditorial', forbidden_config)
    check('no_commerce_mapping_bootstrap', (bad.returncode, bad.stdout, bad.stderr) == (1, '', 'A33_NONEDITORIAL_MAPPING_UNSUPPORTED\n') and not dest.exists())
    for field in ['numero_type', 'thematique', 'pdf_cle', 'liaison.cle', 'article_type', 'date_cle']:
        m = json.loads(mapping.read_bytes())
        if field == 'liaison.cle':
            m['liaison']['cle'] = 'A33_MAPPING_CANARY'
        else:
            m[field] = 'A33_MAPPING_CANARY'
        config = OUT / ('mapping-' + field.replace('.', '-') + '.json')
        config.write_text(json.dumps(m), encoding='utf-8')
        bad, dest = inventory('mapping', config)
        # A16's exact closed four field suffixes; all other fields stay code-only.
        suffix = ' ' + json.dumps({'field': field}, separators=(',', ':')) if field in ('numero_type', 'thematique', 'pdf_cle', 'liaison.cle') else ''
        check('same_a16_refusal_' + field, (bad.returncode, bad.stdout, bad.stderr) == (1, '', 'A16_MAPPING_KEY_ABSENT' + suffix + '\n') and not dest.exists())
    variants = [
        ('echo', "echo 'A33_ECHO_CANARY';", True),
        ('stdout', "fwrite(STDOUT,'A33_STDOUT_CANARY');", False),
        ('stderr', "fwrite(STDERR,'A33_STDERR_CANARY');", False),
        ('early', "exit('A33_EARLY_CANARY');", False),
        ('shutdown', "register_shutdown_function(static function(){fwrite(STDOUT,'A33_SHUTDOWN_CANARY');});", False),
        ('file', "register_shutdown_function(static function(){foreach($GLOBALS['argv'] as $a){if(str_starts_with($a,'--output=')){file_put_contents(substr($a,9).'/archives.json','A33_FILE_OUTPUT_CANARY');}}});", False),
        ('exception', "throw new RuntimeException('A33_SITE_EXCEPTION_CANARY');", False),
    ]
    for label, code, success in variants:
        mu.write_text(nominal + "\nif(getenv('A33_CONFINED')==='1'){" + code + '}\n', encoding='utf-8')
        fb, ff = b.fingerprint(db), b.files(site)
        try:
            q, dest = inventory('channel-' + label)
            check('channel_' + label, (q.returncode == 0 if success else q.returncode == 1 and not dest.exists()) and clean(q, dest))
            check('immutable_channel_' + label, fb == b.fingerprint(db) and ff == b.files(site))
        finally:
            mu.write_text(nominal, encoding='utf-8')
    symlink = site / 'A33_SYMLINK_CANARY'
    symlink.symlink_to(site / 'wp-config.php')
    q, dest = inventory('symlink')
    check('symlink_closed_refusal', (q.returncode, q.stdout, q.stderr) == (1, '', 'A11_SYMLINK_UNSUPPORTED\n') and not dest.exists())
    symlink.unlink()
    for label, target, code in [('existing', out, 'A33_OUTPUT_EXISTS'), ('site', site / 'blocked', 'A33_OUTPUT_UNSAFE'), ('repository', Path('/subject/blocked'), 'A33_OUTPUT_UNSAFE'), ('ancestor', site.parent / 'blocked', 'A33_OUTPUT_UNSAFE'), ('root', Path('/blocked'), 'A33_OUTPUT_UNSAFE')]:
        q = cmd(['python3', '/subject/a33/confine.py', '--wp-path=' + str(site), '--audit=' + str(audit / 'audit.json'), '--correspondance=' + str(mapping), '--output=' + str(target)], check=False)
        check('output_guard_' + label, (q.returncode, q.stdout, q.stderr) == (1, '', code + '\n') and (target == out or not target.exists()))
    check('all_base_tables_and_scheduler_unchanged', before == b.fingerprint(db))
    check('all_site_files_unchanged', files == b.files(site))
    (OUT / 'db-after.json').write_text(json.dumps(b.fingerprint(db)), encoding='utf-8')
    (OUT / 'files.json').write_text(json.dumps({'before': files, 'after': b.files(site)}), encoding='utf-8')
    # Real import footprint: unknown even when excluded folders leave no attachments.
    b.sql(db, "INSERT INTO wp_options(option_name,option_value,autoload) VALUES ('imagine_staging_disabled_plugins','a:0:{}','no')")
    ib, iff = b.fingerprint(db), b.files(site)
    q, dest = inventory('imported')
    imported = json.loads((dest / 'archives.json').read_bytes()) if dest.exists() else {}
    check('imported_excluded_unknown_not_zero', q.returncode == 0 and imported.get('excluded_directories_bytes') == 'inconnu après import' and imported['outside_media_by_year'][0]['files'] == weight(3, 2, 1, 18, True))
    check('imported_readable_local_counts_unchanged', imported.get('published_outside') == d['published_outside'] and imported.get('recent_media') == d['recent_media'])
    check('imported_db_files_identical', ib == b.fingerprint(db) and iff == b.files(site))
    (OUT / 'imported-db-before.json').write_text(json.dumps(ib), encoding='utf-8')
    (OUT / 'imported-db-after.json').write_text(json.dumps(b.fingerprint(db)), encoding='utf-8')


def main():
    b.SCRATCH.mkdir()
    cmd(['mariadb-install-db', '--datadir=/scratch/mysql', '--auth-root-authentication-method=normal', '--skip-test-db', '--user=root'])
    process = subprocess.Popen(['mariadbd', '--user=root', '--datadir=/scratch/mysql', '--socket=' + b.SOCKET, '--skip-networking', '--skip-log-bin', '--pid-file=/scratch/mysql.pid', '--log-error=/scratch/mysql.log'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(100):
            if cmd(['mariadb-admin', '--socket=' + b.SOCKET, '-uroot', 'ping'], check=False).returncode == 0:
                break
            time.sleep(.2)
        try:
            run_storage('classic')
        except Exception as error:
            b.CHECKS.append({'check': 'native_exception', 'status': 'FAIL', 'detail': {'class': type(error).__name__, 'code': str(error)}})
        check('no_network_interfaces', [p.name for p in Path('/sys/class/net').iterdir()] == ['lo'])
    finally:
        process.terminate()
        process.wait(timeout=30)
        result = {'suite': 'A33-native-wordpress', 'stores': ['classic'], 'checks': b.CHECKS, 'exit_code': int(any(c['status'] != 'PASS' for c in b.CHECKS))}
        (OUT / 'result.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    return result['exit_code']


if __name__ == '__main__':
    sys.exit(main())
