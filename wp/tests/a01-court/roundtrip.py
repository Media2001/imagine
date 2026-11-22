"""Synthetic round-trip only. Archives never leave this disposable container."""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import struct
import sys

sys.path.insert(0, '/opt/court')
from inside import restore_and_verify, SITE, DB, command

spec = importlib.util.spec_from_file_location('e2e', '/opt/e2e/inside.py')
e2e = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e2e)

CHECKS = []


def check(label, condition, detail=None):
    CHECKS.append({'name': label, 'pass': bool(condition), 'detail': detail})
    if not condition:
        raise AssertionError(label)


def write_archive(path, source, sql):
    def entry(stream, relative, value):
        parts = relative.rsplit('/', 1)
        prefix, name = parts if len(parts) == 2 else ('', parts[0])
        header = struct.pack('255s14s12s4096s', name.encode(), str(len(value)).encode(), b'0', prefix.encode())
        stream.write(header)
        stream.write(value)
    with path.open('xb') as stream:
        entry(stream, 'database.sql', sql)
        version = re.search(r"^\$wp_version\s*=\s*'([^']+)';", (source / 'wp-includes/version.php').read_text(), re.M)[1]
        entry(stream, 'package.json', json.dumps({'SyntheticFixtureOnly': True, 'WordPress': {'Version': version}}).encode())
        for p in sorted((source / 'wp-content').rglob('*')):
            if p.is_file():
                entry(stream, p.relative_to(source / 'wp-content').as_posix(), p.read_bytes())
        stream.write(bytes(4377))


def expected_removed(path):
    return (path in ('advanced-cache.php', 'object-cache.php')
            or path.startswith(('ai1wm-backups/', 'uploads/wc-logs/', 'cache/'))
            or bool(re.search(r'\.(?:sql|wpress|log)$', path)))


def main():
    process = None
    runs = []
    status = 0
    try:
        process = e2e.database_start()
        for storage in ('classic', 'hpos'):
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    source, database, before = e2e.install(storage)
                theme = source / 'wp-content/themes/fixture-court'
                theme.mkdir()
                (theme / 'style.css').write_text('/*\nTheme Name: Fixture Court Fictive\n*/\n')
                (theme / 'index.php').write_text('<?php echo "FICTION ONLY";')
                e2e.wp(source, ['theme', 'activate', 'fixture-court'])
                (source / 'wp-content/uploads').mkdir(exist_ok=True)
                (source / 'wp-content/uploads/fixture-court.txt').write_text('MEDIA ENTIEREMENT INVENTE\n')
                (source / 'wp-content/mu-plugins/fixture-court.php').write_text('<?php /* MU fictif à conserver */')
                # Expected purge differences, generated here, never taken from a real backup.
                (source / 'wp-content/ai1wm-backups').mkdir(exist_ok=True)
                (source / 'wp-content/ai1wm-backups/fiction.wpress').write_bytes(b'FICTION NOT AN ARCHIVE')
                (source / 'wp-content/object-cache.php').write_text('<?php /* CACHE FICTIF */')
                (source / 'wp-content/advanced-cache.php').write_text('<?php /* CACHE FICTIF */')
                fidelity_before = e2e.wp_json(source, 'fidelity.php')
                plugins_before = sorted(json.loads(e2e.wp(source, ['option', 'get', 'active_plugins', '--format=json']).stdout))
                theme_before = e2e.wp(source, ['option', 'get', 'stylesheet']).stdout.strip()
                sql = command(['php', '/opt/court/export.php'], env={'E2E_DATABASE': database}).stdout
                archive = Path('/scratch/fixture-' + storage + '.wpress')
                write_archive(archive, source, sql)
                request = {'target_url': 'https://fixture.synthetic.test', 'production_url': 'https://source.invalid',
                           'password': secrets.token_urlsafe(32), 'decisions': {}}
                # First run demonstrates the exact unresolved-table refusal, never invents an operator approval.
                result = restore_and_verify(archive, request)
                final = result['steps'][-1]
                check(storage + ':unknown_table_refused_before_decision',
                      not result['data_verified'] and 'TABLE_PERSONNELLE_A_TRANCHER' in final['report'].get('issues', []),
                      final['report'].get('issues'))
                check(storage + ':all_files_restored_exactly',
                      result['restored_files_before_cleanup'] == {
                          p.relative_to(source / 'wp-content').as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in (source / 'wp-content').rglob('*') if p.is_file()})
                # Explicit decision belongs solely to this generated fixture context.
                shutil.rmtree(SITE)
                command(['mariadb', '--socket=/scratch/mariadb.sock', '--user=root', '-e', 'DROP DATABASE ' + DB])
                request['decisions'] = {'wp_yoast_primary_term': {'action': 'garder'}}
                result = restore_and_verify(archive, request)
                check(storage + ':native_three_phases_pass', result['data_verified'],
                      [{'phase': p['phase'], 'exit': p['exit']} for p in result['steps']])
                first = result['restored_files_before_cleanup']
                after = result['files_after_cleanup']
                removed = sorted(set(first) - set(after))
                added = sorted(set(after) - set(first))
                changed = sorted(p for p in set(first) & set(after) if first[p] != after[p])
                check(storage + ':only_expected_purge_differences',
                      all(expected_removed(p) for p in removed) and not changed
                      and added == ['mu-plugins/000-imagine-staging-safety.php'],
                      {'removed': removed, 'added': added, 'changed': changed})
                check(storage + ':active_plugins_unchanged', plugins_before == sorted(json.loads(
                    e2e.wp(SITE, ['option', 'get', 'active_plugins', '--format=json']).stdout)))
                check(storage + ':active_theme_unchanged', theme_before == e2e.wp(SITE, ['option', 'get', 'stylesheet']).stdout.strip())
                fidelity_after = e2e.wp_json(SITE, 'fidelity.php')
                check(storage + ':post_restore_form_seo_fields_intact', fidelity_before == fidelity_after)
                after_business = e2e.wp_json(SITE, 'snapshot.php')
                check(storage + ':business_orders_unchanged', before['orders'] == after_business['orders'])
                counts = {}
                for folder in ('plugins', 'themes', 'uploads', 'mu-plugins'):
                    counts[folder] = {'before': sum(p.startswith(folder + '/') for p in first),
                                      'after': sum(p.startswith(folder + '/') for p in after)}
                runs.append({'storage': storage, 'archive_created_in_same_container': True,
                             'archive_never_exported': True, 'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
                             'status': result['status'], 'phases': result['steps'], 'file_counts': counts,
                             'retained_sha256': {p: after[p] for p in [
                                 'themes/fixture-court/style.css', 'uploads/fixture-court.txt',
                                 'mu-plugins/fixture-court.php', 'plugins/contact-form-7/wp-contact-form-7.php']},
                             'purged': removed, 'active_theme': theme_before, 'active_plugins': plugins_before,
                             'settings_sha256': fidelity_after['settings_sha256'],
                             'publication': result['publication']})
                shutil.rmtree(SITE)
                command(['mariadb', '--socket=/scratch/mariadb.sock', '--user=root', '-e', 'DROP DATABASE ' + DB])
            except Exception as exc:
                CHECKS.append({'name': storage + ':roundtrip', 'pass': False, 'detail': type(exc).__name__ + ':' + str(exc)[:160]})
                status = 1
                if SITE.exists():
                    shutil.rmtree(SITE)
                command(['mariadb', '--socket=/scratch/mariadb.sock', '--user=root', '-e',
                         'DROP DATABASE IF EXISTS ' + DB])
        # Exercise the exact operator-side entrypoint too, with only our freshly generated archive.
        if status == 0:
            e2e.command(['mariadb-admin', '--socket=/scratch/mariadb.sock', '--user=root', 'shutdown'], check=False)
            process.wait(timeout=30)
            process = None
            Path('/input').mkdir(exist_ok=True)
            shutil.copyfile('/scratch/fixture-classic.wpress', '/input/source.wpress')
            request = {'target_url': 'https://fixture.synthetic.test', 'production_url': 'https://source.invalid',
                       'password': secrets.token_urlsafe(32),
                       'decisions': {'wp_yoast_primary_term': {'action': 'garder'}}}
            p = command(['python3', '/opt/court/inside.py'], data=json.dumps(request).encode(), check=False)
            exact = json.loads(Path('/report/court.json').read_text())
            check('exact_operator_entrypoint_reports_block_instead_of_false_verified',
                  p.returncode == 78 and exact['data_verified'] and exact['status'] == 'imported'
                  and exact['verification_state'] == 'DATA_VERIFIED_PUBLICATION_BLOCKED',
                  {'exit': p.returncode, 'status': exact['status'], 'archive_generated_here': True})
            check('exact_operator_stops_database', not Path('/scratch/court.pid').exists())
    finally:
        if process:
            e2e.command(['mariadb-admin', '--socket=/scratch/mariadb.sock', '--user=root', 'shutdown'], check=False)
            process.wait(timeout=30)
        output = {'status': 'PASS' if not status else 'FAIL', 'checks': CHECKS, 'runs': runs,
                  'passed': sum(c['pass'] for c in CHECKS), 'failed': sum(not c['pass'] for c in CHECKS),
                  'full_staging_ready': False, 'reason': 'PUBLICATION_AND_UPDATE_EGRESS_NOT_IMPLEMENTED',
                  'no_real_archive': True, 'no_sites_accessed': True}
        Path('/report/court.json').write_text(json.dumps(output, ensure_ascii=False, indent=2))
    print(json.dumps({'status': output['status'], 'passed': output['passed'], 'failed': output['failed']}))
    return status


if __name__ == '__main__':
    raise SystemExit(main())
