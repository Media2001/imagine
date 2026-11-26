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
    return counts


def reset():
    if subject.SITE.exists():
        shutil.rmtree(subject.SITE)
    query('DROP DATABASE ' + subject.DB)


def verifier():
    p = subject.command(['php', '/subject/verifier', '--worker-bridge', '/opt/court/bridge.php'],
        env={'A01_CONTEXT': '/scratch/a01-context.json', 'WP_ENVIRONMENT_TYPE': 'staging'}, check=False)
    report = json.loads(p.stdout)
    return {'exit': p.returncode, 'report': report, 'stderr_empty': not p.stderr}


def main():
    baseline = sys.argv[1:] == ['baseline']
    receipt = {'status': 'FAIL', 'baseline': baseline, 'synthetic_only': True, 'cases': [], 'checks': checks}
    process = None
    try:
        process = e2e.database_start()
        for storage in ('classic', 'hpos'):
            with contextlib.redirect_stdout(io.StringIO()):
                source, database, _ = e2e.install(storage)
            e2e.wp(source, ['eval-file', '/opt/a28/seed.php'])
            # A01's current archive gate requires operator review for CF7 temporary uploads.
            # This synthetic fixture has no attachments; remove only its generated empty/temp directory.
            shutil.rmtree(source / 'wp-content/uploads/wpcf7_uploads', ignore_errors=True)
            sql = subject.command(['php', '/opt/court/export.php'], env={'E2E_DATABASE': database}).stdout
            archive = Path('/scratch/a28-' + storage + '.wpress')
            write_archive(archive, source, sql)
            modes = ['default', 'keep-unknown', 'keep-known'] if baseline else ['default', 'keep-unknown', 'keep-known', 'anonymise-known']
            for mode in modes:
                decisions = {}
                if mode == 'keep-unknown':
                    decisions['wp_fiction_messages'] = {'action': 'garder'}
                if mode in ('keep-known', 'anonymise-known'):
                    decisions['wp_fluentform_submissions'] = ({'action': 'garder'} if mode == 'keep-known'
                        else {'action': 'anonymiser', 'columns': ['payload']})
                request = {'target_url': 'https://fixture.synthetic.test', 'production_url': 'https://source.invalid',
                           'password': secrets.token_urlsafe(32), 'decisions': decisions}
                result = subject.execute_offline_request(archive, request, False)
                case = {'storage': storage, 'mode': mode, 'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
                        'result': result}
                receipt['cases'].append(case)
                if baseline or mode in ('default', 'keep-unknown'):
                    check(storage + ':' + mode + ':three_native_phases', result.get('data_verified') is True)
                    counts = oracle()
                    case['oracle'] = counts
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
                        residue_cases = TABLES + TYPES
                        for item in residue_cases:
                            if item in TABLES:
                                query("INSERT INTO `wp_" + item + "` VALUES (42,'A28_RESIDUE_FICTIVE');")
                            else:
                                query("INSERT INTO wp_posts (ID,post_type,post_title,post_content) VALUES (424242,'" + item + "','A28_RESIDUE_FICTIVE','A28_RESIDUE_FICTIVE');")
                            refused = verifier()
                            check(storage + ':residue_refused:' + item,
                                  refused['exit'] == 1 and 'FORM_MESSAGES_REMAIN' in refused['report']['issues']
                                  and refused['report']['form_message_residues'] == 1 and refused['stderr_empty'])
                            original = Path('/subject/lib.php').read_bytes()
                            old = b"$issues[] = 'FORM_MESSAGES_REMAIN';"
                            check(storage + ':mutation_seam:' + item, original.count(old) == 1)
                            try:
                                Path('/subject/lib.php').write_bytes(original.replace(old, b"/* A28 disposable witness: removed residue gate */"))
                                mutant = verifier()
                                check(storage + ':mutation_allows_residue:' + item, mutant['exit'] == 0 and mutant['report']['ok'])
                            finally:
                                Path('/subject/lib.php').write_bytes(original)
                            restored = verifier()
                            check(storage + ':restored_refuses:' + item, restored['exit'] == 1)
                            case.setdefault('residue_probes', []).append({'kind': item, 'refused': refused, 'mutant': mutant,
                                                                         'restored': restored, 'source_restored': Path('/subject/lib.php').read_bytes() == original})
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
