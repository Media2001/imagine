"""A28 full synthetic .wpress import, using the actual A01 three phases."""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import secrets
import shutil
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, '/opt/court')
import inside as subject
from diagnostics import CommandFailure
spec = importlib.util.spec_from_file_location('a01_e2e', '/opt/e2e/inside.py')
e2e = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e2e)
from roundtrip import write_archive

TABLES = ['fluentform_submissions', 'fluentform_entry_details', 'fluentform_submission_meta',
          'fluentform_logs', 'fluentform_draft_submissions', 'ff_scheduled_actions']
TYPES = ['flamingo_inbound', 'flamingo_contact']
checks = []


def check(name, ok):
    checks.append({'name': name, 'pass': bool(ok)})
    if not ok:
        raise AssertionError(name)


def query(sql):
    return subject.command(['mariadb', '--socket=/scratch/mariadb.sock', '--user=root', '--batch',
                            '--skip-column-names', subject.DB], data=sql.encode()).stdout.decode().strip()


def oracle():
    counts = {t: int(query('SELECT COUNT(*) FROM `wp_' + t + '`')) for t in TABLES + ['fiction_messages']}
    counts.update({t: int(query("SELECT COUNT(*) FROM wp_posts WHERE post_type='" + t + "'"))
                   for t in TYPES + ['fiction_magazine']})
    counts['known_meta'] = int(query("SELECT COUNT(*) FROM wp_postmeta WHERE meta_value LIKE 'A28_FICTIVE%flamingo%';"))
    counts['known_revisions'] = int(query("SELECT COUNT(*) FROM wp_posts WHERE post_type='revision' AND post_content LIKE 'A28_FICTIVE%flamingo%';"))
    # Inspect real restored values, but never put canaries into the receipt.
    counts['canary_rows'] = {t: int(query("SELECT COUNT(*) FROM `wp_" + t + "` WHERE payload LIKE 'A28_FICTIVE%';"))
                             for t in TABLES + ['fiction_messages']}
    counts['post_canary_rows'] = {t: int(query("SELECT COUNT(*) FROM wp_posts WHERE post_type='" + t
        + "' AND post_content LIKE 'A28_FICTIVE%';")) for t in TYPES + ['fiction_magazine']}
    return counts


def protected(database):
    condition = "post_type IN ('fiction_magazine','wpcf7_contact_form') OR (post_type='revision' AND post_parent IN (SELECT ID FROM wp_posts WHERE post_type='fiction_magazine'))"
    sql = 'SELECT * FROM wp_posts WHERE ' + condition + ' ORDER BY ID;'
    sql += 'SELECT m.* FROM wp_postmeta m JOIN wp_posts p ON p.ID=m.post_id WHERE p.ID IN (SELECT ID FROM wp_posts WHERE ' + condition + ') ORDER BY m.meta_id;'
    raw = subject.command(['mariadb', '--socket=/scratch/mariadb.sock', '--user=root', '--batch',
                           '--skip-column-names', database], data=sql.encode()).stdout
    return hashlib.sha256(raw).hexdigest()


def reset():
    if subject.SITE.exists():
        shutil.rmtree(subject.SITE)
    query('DROP DATABASE ' + subject.DB)


def native(phase):
    p = subject.command(['php', '/subject/' + phase, '--worker-bridge', '/opt/court/bridge.php'],
        env={'A01_CONTEXT': '/scratch/a01-context.json', 'WP_ENVIRONMENT_TYPE': 'staging'}, check=False)
    report = json.loads(p.stdout)
    return {'exit': p.returncode, 'report': report, 'stderr_empty': not p.stderr}


def verifier():
    return native('verifier')


def database_digest():
    raw = subject.command(['mariadb-dump', '--socket=/scratch/mariadb.sock', '--user=root',
                           '--skip-comments', '--skip-dump-date', '--compact', subject.DB]).stdout
    return hashlib.sha256(raw).hexdigest()


def orphan_postmeta_witness(archive, request, storage):
    """Omit only the meta purge, not posts/revisions or either transformation phase."""
    path = Path('/subject/engine.php')
    original = path.read_bytes()
    purge = b" || ($kind === 'postmeta' && isset($formPosts[(int) ($row['post_id'] ?? 0)]))"
    gate = b"$issues[] = 'FORM_MESSAGES_REMAIN';"
    check(storage + ':orphan:seams', original.count(purge) == 1 and original.count(gate) == 1)
    try:
        path.write_bytes(original.replace(purge, b''))
        result = subject.execute_offline_request(archive, request, False)
    finally:
        path.write_bytes(original)
    check(storage + ':orphan:import_refused', result.get('data_verified') is False
          and [p['exit'] for p in result.get('steps', [])] == [0, 0, 1])
    counts = oracle()
    check(storage + ':orphan:parents_revisions_absent', all(counts[t] == 0 for t in TYPES)
          and counts['known_revisions'] == 0)
    check(storage + ':orphan:four_meta_canaries_remain', counts['known_meta'] == 4)
    context = json.loads(Path('/scratch/a01-context.json').read_bytes())
    known_ids = context['form_post_ids']
    check(storage + ':orphan:trusted_snapshot_four_ids', len(known_ids) == len(set(known_ids)) == 4)
    orphan_count = int(query('SELECT COUNT(*) FROM wp_postmeta m LEFT JOIN wp_posts p ON p.ID=m.post_id '
        + 'WHERE p.ID IS NULL AND m.post_id IN (' + ','.join(map(str, known_ids)) + ");"))
    check(storage + ':orphan:known_orphans_verified_by_sql', orphan_count == 4)
    refused = verifier()
    check(storage + ':orphan:refused', refused['exit'] == 1 and refused['stderr_empty']
          and refused['report']['form_message_residues'] == 4
          and 'FORM_MESSAGES_REMAIN' in refused['report']['issues']
          and 'SONDE_NON_EXECUTEE_DONNEES_REFUSEES' in refused['report']['warnings'])
    try:
        path.write_bytes(original.replace(gate, b'/* A28 witness: removed residue refusal */'))
        mutant = verifier()
    finally:
        path.write_bytes(original)
    restored = verifier()
    check(storage + ':orphan:control_removed_accepts', mutant['exit'] == 0 and mutant['report']['ok']
          and mutant['report']['form_message_residues'] == 4 and mutant['stderr_empty'])
    check(storage + ':orphan:control_restored_refuses', restored['exit'] == 1
          and restored['report']['form_message_residues'] == 4
          and 'FORM_MESSAGES_REMAIN' in restored['report']['issues'])
    return result, {'refused': refused, 'mutant': mutant, 'restored': restored,
                    'known_parent_posts': 0, 'known_revision_posts': 0, 'known_orphan_meta': orphan_count,
                    'provenance_ids_count': len(known_ids), 'source_restored': path.read_bytes() == original,
                    'mutation': 'omit_only_postmeta_purge', 'oracle': counts}


def main():
    baseline = sys.argv[1:] == ['baseline']
    receipt = {'status': 'FAIL', 'baseline': baseline, 'synthetic_only': True, 'cases': [], 'checks': checks}
    process = None
    try:
        process = e2e.database_start()
        for storage in ('classic', 'hpos'):
            with contextlib.redirect_stdout(io.StringIO()):
                source, database, business_before = e2e.install(storage)
            e2e.wp(source, ['eval-file', '/opt/a28/seed.php'])
            fidelity_before = e2e.wp_json(source, 'fidelity.php')
            protected_before = protected(database)
            # A01's current archive gate requires operator review for CF7 temporary uploads.
            # This synthetic fixture has no attachments; remove only its generated empty/temp directory.
            shutil.rmtree(source / 'wp-content/uploads/wpcf7_uploads', ignore_errors=True)
            sql = subject.command(['php', '/opt/court/export.php'], env={'E2E_DATABASE': database}).stdout
            archive = Path('/scratch/a28-' + storage + '.wpress')
            write_archive(archive, source, sql)
            modes = ['default', 'keep-unknown', 'keep-known'] if baseline else ['default', 'keep-unknown', 'keep-known', 'anonymise-known', 'omit-meta-purge']
            for mode in modes:
                decisions = {}
                if mode == 'keep-unknown':
                    decisions['wp_fiction_messages'] = {'action': 'garder'}
                if mode in ('keep-known', 'anonymise-known'):
                    decisions['wp_fluentform_submissions'] = ({'action': 'garder'} if mode == 'keep-known'
                        else {'action': 'anonymiser', 'columns': ['payload']})
                request = {'target_url': 'https://fixture.synthetic.test', 'production_url': 'https://source.invalid',
                           'password': secrets.token_urlsafe(32), 'decisions': decisions}
                if mode == 'omit-meta-purge':
                    result, witness = orphan_postmeta_witness(archive, request, storage)
                    receipt['cases'].append({'storage': storage, 'mode': mode,
                        'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
                        'result': result, 'postmeta_purge_witness': witness})
                    reset()
                    continue
                result = subject.execute_offline_request(archive, request, False)
                case = {'storage': storage, 'mode': mode, 'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
                        'result': result}
                receipt['cases'].append(case)
                if baseline or mode in ('default', 'keep-unknown'):
                    check(storage + ':' + mode + ':three_native_phases', result.get('data_verified') is True)
                    counts = oracle()
                    case['oracle'] = counts
                    case['protected_before'] = protected_before
                    case['protected_after'] = protected(subject.DB)
                    check(storage + ':' + mode + ':unknown_content_exact', case['protected_after'] == protected_before)
                    check(storage + ':' + mode + ':form_seo_fields_exact', e2e.wp_json(subject.SITE, 'fidelity.php') == fidelity_before)
                    check(storage + ':' + mode + ':business_orders_exact', e2e.wp_json(subject.SITE, 'snapshot.php')['orders'] == business_before['orders'])
                    source_files = subject.manifest(source / 'wp-content')
                    check(storage + ':' + mode + ':faithful_files', all(source_files[p] == digest for p, digest in result['restored_files_before_cleanup'].items()))
                    check(storage + ':' + mode + ':retained_files_exact', all(result['files_after_cleanup'][p] == digest
                        for p, digest in result['restored_files_before_cleanup'].items() if p in result['files_after_cleanup']))
                    for t in TABLES:
                        expected = 1 if baseline and mode == 'keep-known' and t == 'fluentform_submissions' else 0
                        check(storage + ':' + mode + ':dedicated:' + t, counts[t] == expected and counts['canary_rows'][t] == expected)
                    check(storage + ':' + mode + ':unknown_table_policy', counts['fiction_messages'] == (mode == 'keep-unknown'))
                    for t in TYPES:
                        check(storage + ':' + mode + ':post_type:' + t, counts[t] == (1 if baseline else 0))
                    check(storage + ':' + mode + ':unknown_post_type_untouched', counts['fiction_magazine'] == 1)
                    check(storage + ':' + mode + ':known_meta', counts['known_meta'] == (4 if baseline else 0))
                    check(storage + ':' + mode + ':known_revisions', counts['known_revisions'] == (2 if baseline else 0))
                    if not baseline and mode == 'default':
                        before = verifier()
                        check(storage + ':clean_verifier_exit_zero', before['exit'] == 0 and before['stderr_empty'])
                        context_file = Path('/scratch/a01-context.json')
                        context_original = context_file.read_bytes()
                        for item in TABLES:
                            context = json.loads(context_original)
                            context['table_decisions']['wp_' + item] = {'action': 'garder'}
                            context_file.write_text(json.dumps(context))
                            db_before = database_digest()
                            files_before = subject.manifest(subject.SITE)
                            try:
                                refused = native('neutraliser')
                            finally:
                                context_file.write_bytes(context_original)
                            expected = {'ok': False, 'issues': ['STAGING_REFUSE', 'FORM_MESSAGES_DECISION_REFUSED'],
                                'failure': {'stage': 'native_neutraliser', 'code': 'FORM_MESSAGES_DECISION_REFUSED', 'table': item}}
                            case.setdefault('native_keep_probes', []).append({'kind': item, 'refused': refused,
                                'database_unchanged': db_before == database_digest(), 'files_unchanged': files_before == subject.manifest(subject.SITE)})
                            check(storage + ':native_keep_closed:' + item, refused == {'exit': 78, 'report': expected, 'stderr_empty': True})
                            check(storage + ':native_keep_immutable:' + item,
                                  db_before == database_digest() and files_before == subject.manifest(subject.SITE))
                        residue_cases = TABLES + TYPES
                        for item in residue_cases:
                            if item in TABLES:
                                query("INSERT INTO `wp_" + item + "` VALUES (42,'A28_RESIDUE_FICTIVE');")
                            else:
                                query("SET SESSION sql_mode=''; INSERT INTO wp_posts (ID,post_type,post_title,post_content) VALUES (424242,'" + item + "','A28_RESIDUE_FICTIVE','A28_RESIDUE_FICTIVE');")
                            refused = verifier()
                            check(storage + ':residue_refused:' + item,
                                  refused['exit'] == 1 and 'FORM_MESSAGES_REMAIN' in refused['report']['issues']
                                  and refused['report']['form_message_residues'] == 1 and refused['stderr_empty'])
                            original = Path('/subject/engine.php').read_bytes()
                            old = b"$issues[] = 'FORM_MESSAGES_REMAIN';"
                            check(storage + ':mutation_seam:' + item, original.count(old) == 1)
                            try:
                                Path('/subject/engine.php').write_bytes(original.replace(old, b"/* A28 disposable witness: removed residue gate */"))
                                mutant = verifier()
                                check(storage + ':mutation_allows_residue:' + item, mutant['exit'] == 0 and mutant['report']['ok'])
                            finally:
                                Path('/subject/engine.php').write_bytes(original)
                            restored = verifier()
                            check(storage + ':restored_refuses:' + item, restored['exit'] == 1)
                            case.setdefault('residue_probes', []).append({'kind': item, 'refused': refused, 'mutant': mutant,
                                                                         'restored': restored, 'source_restored': Path('/subject/engine.php').read_bytes() == original})
                            if item in TABLES:
                                query('DELETE FROM `wp_' + item + '` WHERE id=42')
                            else:
                                query('DELETE FROM wp_posts WHERE ID=424242')
                        check(storage + ':post_mutations_clean', verifier()['exit'] == 0)
                else:
                    expected = {'stage': 'sql_preflight', 'code': 'FORM_MESSAGES_DECISION_REFUSED',
                                'detail': {'table': 'fluentform_submissions'}}
                    check(storage + ':' + mode + ':exact_closed_refusal', result.get('failure') == expected and not result['data_verified'])
                    check(storage + ':' + mode + ':no_database_import', not subject.command(
                        ['mariadb', '--socket=/scratch/mariadb.sock', '--user=root', '--skip-column-names'],
                        data=b"SHOW DATABASES LIKE 'imagine_a01_staging'", check=False).stdout.strip())
                if result.get('data_verified'):
                    reset()
                elif subject.SITE.exists():
                    shutil.rmtree(subject.SITE)
                    for f in ('/scratch/a01-source.sql', '/scratch/a01-validated.sql'):
                        Path(f).unlink(missing_ok=True)
            shutil.rmtree(source)
            subject.command(['mariadb', '--socket=/scratch/mariadb.sock', '--user=root'], data=('DROP DATABASE ' + database).encode())
        receipt['status'] = 'PASS'
    except Exception as error:
        import traceback
        receipt['failure'] = {'class': type(error).__name__, 'message': str(error), 'trace': traceback.format_exc()}
    finally:
        if process:
            e2e.command(['mariadb-admin', '--socket=/scratch/mariadb.sock', '--user=root', 'shutdown'], check=False)
            process.wait(timeout=30)
        receipt['passed'] = sum(c['pass'] for c in checks)
        receipt['failed'] = sum(not c['pass'] for c in checks)
        Path('/report/a28-native.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    print(json.dumps({k: receipt[k] for k in ('status', 'passed', 'failed')}))
    return 0 if receipt['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
