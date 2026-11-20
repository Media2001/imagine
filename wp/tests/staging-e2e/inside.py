#!/usr/bin/env python3
"""Runs only in the newly owned network-none container, never on the host."""
import hashlib
import json
import os
import pathlib
import secrets
import shutil
import subprocess
import sys
import time

ROOT = pathlib.Path('/opt/e2e')
SCRATCH = pathlib.Path('/scratch')
REPORT = pathlib.Path('/report')
SOCKET = '/scratch/mariadb.sock'
CHECKS = []
SUBJECT = pathlib.Path('/subject')
FIDELITY = {}


def record(name, status, detail):
    CHECKS.append({'check': name, 'status': status, 'detail': detail})
    print(json.dumps(CHECKS[-1], ensure_ascii=False), flush=True)


def command(argv, *, env=None, input_text=None, check=True, timeout=180):
    merged = os.environ.copy()
    if env:
        merged.update(env)
    result = subprocess.run(argv, env=merged, input=input_text, capture_output=True,
                            text=True, timeout=timeout)
    if check and result.returncode:
        # Command arguments are intentionally not logged: a prompt/env may contain an ephemeral password.
        raise RuntimeError('Command failed (' + pathlib.Path(argv[0]).name + '): ' + result.stderr[-3000:] + result.stdout[-1500:])
    return result


def wp(site, args, **kwargs):
    if args and args[0] == 'eval-file':
        args = args + ['--use-include']  # Preserve strict_types/namespace, unlike eval().
    return command(['wp', '--allow-root', '--no-color', '--path=' + str(site)] + args, **kwargs)


def wp_json(site, filename, **kwargs):
    result = wp(site, ['eval-file', str(ROOT / filename)], **kwargs)
    lines = [line[len('E2E_JSON='):] for line in result.stdout.splitlines() if line.startswith('E2E_JSON=')]
    if len(lines) != 1:
        raise RuntimeError('Missing or ambiguous real WordPress JSON result: ' + filename)
    return json.loads(lines[0])


def raw_db(database, storage, mode='oracle', extra=None):
    env = {'E2E_DATABASE': database, 'E2E_STORAGE': storage, 'E2E_DB_MODE': mode}
    if extra:
        env.update(extra)
    result = command(['php', str(ROOT / 'db-probe.php')], env=env)
    lines = [line[len('E2E_JSON='):] for line in result.stdout.splitlines() if line.startswith('E2E_JSON=')]
    if len(lines) != 1:
        raise RuntimeError('Missing independent PDO oracle result')
    return json.loads(lines[0])


def assert_true(condition, label, detail):
    if not condition:
        record(label, 'FAIL', detail)
        raise RuntimeError(label)
    record(label, 'PASS', detail)


def isolation():
    assert_true(sorted(p.name for p in pathlib.Path('/sys/class/net').iterdir()) == ['lo'],
                'inside_network_interfaces', 'Only loopback exists')
    for file in ('/proc/net/tcp', '/proc/net/tcp6'):
        rows = pathlib.Path(file).read_text().splitlines()[1:]
        assert_true(not any(line.split()[3] == '0A' for line in rows),
                    'no_tcp_listener:' + pathlib.Path(file).name, 'No TCP socket listening, including MariaDB')


def database_start():
    SCRATCH.mkdir(exist_ok=False)
    REPORT.mkdir(exist_ok=True)
    data = SCRATCH / 'mysql'
    command(['mariadb-install-db', '--datadir=' + str(data), '--auth-root-authentication-method=normal',
             '--skip-test-db', '--user=root'], timeout=180)
    process = subprocess.Popen(['mariadbd', '--user=root', '--datadir=' + str(data), '--socket=' + SOCKET,
                                '--skip-networking', '--skip-log-bin', '--pid-file=/scratch/mariadb.pid',
                                '--log-error=/scratch/mariadb.log'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(100):
        if process.poll() is not None:
            raise RuntimeError('Disposable MariaDB failed: ' + (SCRATCH / 'mariadb.log').read_text()[-4000:])
        ready = command(['mariadb-admin', '--socket=' + SOCKET, '--user=root', 'ping'], check=False, timeout=5)
        if ready.returncode == 0:
            isolation()
            return process
        time.sleep(.2)
    raise RuntimeError('Disposable MariaDB did not become available')


def install(storage):
    database = 'imagine_e2e_' + storage + '_test'
    command(['mariadb', '--socket=' + SOCKET, '--user=root', '-e', 'CREATE DATABASE ' + database])
    site = SCRATCH / ('site-' + storage)
    shutil.copytree('/opt/wordpress/wordpress', site)
    shutil.copytree('/opt/woocommerce/woocommerce', site / 'wp-content/plugins/woocommerce')
    config = """<?php
    define('DB_NAME', '%s');
    define('DB_USER', 'root');
    define('DB_PASSWORD', '');
    define('DB_HOST', 'localhost:/scratch/mariadb.sock');
    define('DB_CHARSET', 'utf8mb4');
    define('DB_COLLATE', '');
    define('WP_ENVIRONMENT_TYPE', 'staging');
    define('WP_HTTP_BLOCK_EXTERNAL', true);
    define('DISABLE_WP_CRON', true);
    define('AUTOMATIC_UPDATER_DISABLED', true);
    define('WP_AUTO_UPDATE_CORE', false);
    define('WP_DEBUG', false);
    $table_prefix = 'wp_';
    if (!defined('ABSPATH')) { define('ABSPATH', __DIR__ . '/'); }
    require_once ABSPATH . 'wp-settings.php';
    """ % database
    (site / 'wp-config.php').write_text(config)
    wp(site, ['core', 'install', '--url=https://fixture.synthetic.test', '--title=Site entièrement fictif E2E',
              '--admin_user=fictif-admin', '--admin_email=fictif-admin@example.org', '--skip-email', '--prompt=admin_password'],
       input_text=secrets.token_urlsafe(40) + '\n')
    wp(site, ['plugin', 'activate', 'woocommerce'], timeout=240)
    wp(site, ['option', 'update', 'woocommerce_custom_orders_table_data_sync_enabled', 'no'])
    wp(site, ['option', 'update', 'woocommerce_custom_orders_table_enabled', 'yes' if storage == 'hpos' else 'no'])
    wp(site, ['eval-file', str(ROOT / 'fixture.php')], timeout=240)
    for plugin in ('contact-form-7', 'wordpress-seo', 'meta-box'):
        shutil.copytree('/opt/free-plugins/' + plugin, site / 'wp-content/plugins' / plugin)
    (site / 'wp-content/mu-plugins').mkdir(exist_ok=True)
    shutil.copy2(ROOT / 'fidelity-mu.php', site / 'wp-content/mu-plugins/imagine-e2e-fields.php')
    wp(site, ['plugin', 'activate', 'contact-form-7', 'wordpress-seo', 'meta-box'], timeout=240)
    wp_json(site, 'fidelity.php', env={'E2E_FIDELITY_PHASE': 'seed'})
    fidelity = wp_json(site, 'fidelity.php')
    assert_true(all(fidelity['boot'].values()) and fidelity['form_renders'] and fidelity['field_reads'],
                storage + ':pristine_fidelity', fidelity)
    FIDELITY[storage] = fidelity
    snapshot = wp_json(site, 'snapshot.php')
    assert_true(len(snapshot['users']) == 30 and len(snapshot['orders']) == 30,
                storage + ':fixture_counts', {'accounts': len(snapshot['users']), 'orders': len(snapshot['orders'])})
    assert_true(snapshot['versions']['hpos'] == (storage == 'hpos'), storage + ':authoritative_storage', snapshot['versions'])
    return site, database, snapshot


def export(database, suffix):
    result = command(['mariadb-dump', '--socket=' + SOCKET, '--user=root', '--skip-comments',
                      '--skip-dump-date', '--single-transaction', database])
    target = SCRATCH / (database + '-' + suffix + '.sql')
    target.write_text(result.stdout)
    return target


def restore(database, target):
    # Only SQL just generated in this same new container is ever imported.
    if target.parent != SCRATCH or not target.name.startswith(database + '-'):
        raise RuntimeError('Refusing an import not generated by this exact fixture')
    command(['mariadb', '--socket=' + SOCKET, '--user=root', database], input_text=target.read_text())


def clean_oracle(value, *, after=False):
    good = (not value['residue_hits'] and value['bad_user_emails'] == 0 and value['bad_order_emails'] == 0
            and value['pending_outbound'] == 0 and value['cron_outbound'] == 0
            and value['active_webhooks'] == 0 and value['payment_tokens'] == 0)
    if after:
        good = (good and value.get('mail_dispatch_calls') == 0 and value['sessions'] == 0
                and str(value['blog_public']) == '0' and value['environment'] == 'staging'
                and value['home'] == 'https://fixture.synthetic.test' and value['siteurl'] == value['home'])
    return good


def mutate(site, case):
    wp(site, ['eval-file', str(ROOT / 'mutate.php')], env={'E2E_MUTATION': case})


def selftest(site, database, storage, before):
    pristine = export(database, 'pristine')
    restore(database, pristine)
    actual = wp_json(site, 'snapshot.php')
    assert_true(actual['orders'] == before['orders'], storage + ':offline_import_preserves_orders',
                {'generated_in_same_container': True, 'sql_sha256': hashlib.sha256(pristine.read_bytes()).hexdigest()})
    value = wp_json(site, 'oracle.php')
    assert_true(clean_oracle(value), storage + ':oracle_positive_pristine', value)
    # The spy must really see delivery without a subject blocker: no test-installed mail mask.
    mail = wp_json(site, 'oracle.php', env={'E2E_ORACLE_PHASE': 'mail'})
    assert_true(mail['mail_dispatch_calls'] == 1, storage + ':mail_probe_detects_unblocked_dispatch',
                {'dispatch_calls': mail['mail_dispatch_calls'], 'real_sends': 0})
    raw_before = raw_db(database, storage, 'snapshot')
    assert_true(len(raw_before['orders']) == 30 and len(raw_before['users']) == 30,
                storage + ':independent_snapshot_counts', {'orders': len(raw_before['orders']), 'users': len(raw_before['users'])})
    assert_true(clean_oracle(raw_db(database, storage)), storage + ':raw_oracle_positive_pristine', 'PDO oracle agrees without loading WordPress')
    for case in ('service-key', 'user-token', 'order-token', 'paypal', 'user-email', 'order-email',
                 'note-email', 'form-email', 'scheduled-outbound'):
        restore(database, pristine)
        mutate(site, case)
        value = wp_json(site, 'oracle.php')
        independent = raw_db(database, storage)
        assert_true(not clean_oracle(independent), storage + ':raw_oracle_rejects_api_mutation:' + case,
                    {'residue_columns': sorted(independent['residue_hits'])})
        assert_true(not clean_oracle(value), storage + ':oracle_rejects:' + case,
                    {'residue_columns': sorted(value['residue_hits']), 'bad_user_emails': value['bad_user_emails'],
                     'bad_order_emails': value['bad_order_emails'], 'pending_outbound': value['pending_outbound'],
                     'cron_outbound': value['cron_outbound'], 'active_webhooks': value['active_webhooks']})
    for case in ('service-key', 'user-token', 'order-token', 'paypal', 'user-email', 'order-email', 'note-email'):
        restore(database, pristine)
        raw_db(database, storage, 'mutate', {'E2E_RESIDUE_CASE': case})
        assert_true(not clean_oracle(raw_db(database, storage)), storage + ':raw_oracle_rejects_direct_residue:' + case,
                    'Independent residue insertion detected without WordPress/bootstrap side effects')
    restore(database, pristine)
    assert_true(raw_db(database, storage, 'snapshot') == raw_before, storage + ':raw_snapshot_reproducibility',
                'Same independent snapshot after repeat import')
    assert_true(clean_oracle(wp_json(site, 'oracle.php')), storage + ':oracle_positive_after_restore', 'Fresh synthetic copy is clean again')


def subject_command(site, name, password, context):
    adapter_path = ROOT / 'subject-adapter.json'
    if not adapter_path.exists():
        raise RuntimeError('DEPENDENCY_NOT_READY: subject-adapter.json must match the actual launcher interface; no guessed execution')
    adapter = json.loads(adapter_path.read_text())
    template = adapter['commands'][name]
    if not isinstance(template, list) or not all(isinstance(v, str) for v in template):
        raise RuntimeError('Subject command must be an explicit argv array')
    values = {'site': str(site), 'subject': '/subject', 'context': str(context)}
    argv = [arg.format_map(values) for arg in template]
    if not any(arg.startswith('/subject/') for arg in argv):
        raise RuntimeError('Subject command must target the copied /subject directory')
    return command(argv, env={'WP_ENVIRONMENT_TYPE': 'staging', 'E2E_CONTEXT': str(context),
                              'WP_CLI_ALLOW_ROOT': '1'},
                   input_text=password + '\n' if name == 'anonymiser' else None,
                   check=False, timeout=240)


def acceptance(site, database, storage, before):
    before_raw = raw_db(database, storage, 'snapshot')
    public_before = raw_db(database, storage, 'table-fixtures', {'E2E_TABLE_ACTION': 'public'})
    (site / '.imagine-staging-offline').write_text('OFFLINE_COPY\n')
    mutate(site, 'all')  # Unknown content types must survive the reprise, not cause a schema refusal.
    poisoned = export(database, 'poisoned')
    restore(database, poisoned)
    assert_true(not clean_oracle(raw_db(database, storage)), storage + ':poisoned_import_has_real_fixture_traps', 'Independent PDO database scan detected traps before subjects')
    context = SCRATCH / ('context-' + storage + '.json')
    context.write_text(json.dumps({'environment': 'staging', 'isolated': True, 'restored': True,
        'database': database, 'production_hosts': ['production.synthetic.invalid'],
        'target_url': 'https://fixture.synthetic.test', 'wp_path': str(site)}))
    password = secrets.token_urlsafe(40)
    preflight = command(['php', str(ROOT / 'subject-preflight.php')],
                        env={'E2E_CONTEXT': str(context), 'WP_ENVIRONMENT_TYPE': 'staging'})
    preflight_value = json.loads(next(line[len('E2E_JSON='):] for line in preflight.stdout.splitlines() if line.startswith('E2E_JSON=')))
    record(storage + ':subject_guard_preflight', 'PASS' if preflight_value['guard_ok'] else 'FAIL', preflight_value)
    for name in ('neutraliser', 'anonymiser', 'verifier'):
        result = subject_command(site, name, password, context)
        # Never persist subjects' raw output: report only hashes, status, non-sensitive error tags.
        detail = {'exit_code': result.returncode, 'stdout_sha256': hashlib.sha256(result.stdout.encode()).hexdigest(),
                  'stderr_sha256': hashlib.sha256(result.stderr.encode()).hexdigest()}
        if name == 'neutraliser' and result.returncode:
            diagnostic = command(['php', str(ROOT / 'subject-preflight.php')],
                env={'E2E_CONTEXT': str(context), 'WP_ENVIRONMENT_TYPE': 'staging',
                     'E2E_PREFLIGHT_PHASE': 'neutraliser-diagnostic'})
            detail['retry_diagnostic'] = json.loads(next(line[len('E2E_JSON='):] for line in diagnostic.stdout.splitlines() if line.startswith('E2E_JSON=')))
        if name == 'verifier':
            report = json.loads(result.stdout)
            detail['issues'] = [tag for tag in report.get('issues', []) if isinstance(tag, str) and tag.isupper() and tag.replace('_', '').isalpha()]
        assert_true(result.returncode == 0, storage + ':subject_positive:' + name, detail)
    listed = {table['name']: table for table in report.get('unknown_tables', [])}
    assert_true('wp_imagine_e2e_public' in listed and listed['wp_imagine_e2e_public']['rows'] == 1,
                storage + ':unknown_public_table_reported', listed.get('wp_imagine_e2e_public'))
    assert_true(raw_db(database, storage, 'table-fixtures', {'E2E_TABLE_ACTION': 'status'}) == public_before,
                storage + ':unknown_public_table_preserved', public_before)
    fidelity = wp_json(site, 'fidelity.php')
    assert_true(fidelity == FIDELITY[storage], storage + ':post_clean_fidelity',
                {'before': FIDELITY[storage], 'after': fidelity,
                 'proof': 'Fresh WP bootstrap; active plugin code, form rendering, field reads and exact setting digests'})
    after = raw_db(database, storage, 'snapshot')
    value = raw_db(database, storage, extra={'E2E_ORACLE_PHASE': 'after'})
    # Capture the DB state before any WordPress load. Bootstrapping is only for the controlled mail probe.
    mail = wp_json(site, 'mail-probe.php')
    value.update(mail)
    assert_true(clean_oracle(value, after=True), storage + ':independent_clean_and_mail_blocked', value)
    assert_true(after['orders'] == before_raw['orders'], storage + ':preserved_business_fields',
                'Statuses, dates, amounts, products, quantities, countries and payment methods unchanged')
    old_users = {int(u['id']): u for u in before_raw['users']}
    new_users = {int(u['id']): u for u in after['users']}
    assert_true(all(uid in new_users and old['pass_hash'] != new_users[uid]['pass_hash'] for uid, old in old_users.items()),
                storage + ':all_original_passwords_replaced', {'original_accounts': len(old_users)})
    assert_true(all(new_users[uid]['billing_country'] == old['billing_country']
                    and new_users[uid]['shipping_country'] == old['shipping_country'] for uid, old in old_users.items()),
                storage + ':account_countries_preserved', {'original_accounts': len(old_users)})
    sanitized = export(database, 'sanitized')
    for case in ('service-key', 'publishable-key', 'restricted-key', 'webhook-key', 'brevo-key',
                 'unknown-table-key', 'user-token', 'order-token', 'paypal', 'user-email', 'order-email'):
        restore(database, sanitized)
        raw_db(database, storage, 'mutate', {'E2E_RESIDUE_CASE': case})
        assert_true(not clean_oracle(raw_db(database, storage)), storage + ':residue_actually_inserted:' + case,
                    'Independent PDO oracle saw the residue before invoking the verifier')
        result = subject_command(site, 'verifier', password, context)
        assert_true(result.returncode != 0, storage + ':subject_rejects_residue:' + case,
                    {'exit_code': result.returncode, 'verification_only': True,
                     'start_gate': 'NOT_TESTED: no server is started by this harness'})
    restore(database, sanitized)
    raw_db(database, storage, 'mutate', {'E2E_RESIDUE_CASE': 'note-email'})
    result = subject_command(site, 'verifier', password, context)
    note_report = json.loads(result.stdout)
    assert_true(result.returncode == 0 and 'EMAIL_HORS_PERIMETRE_COMPTES_COMMANDES' in note_report.get('warnings', []),
                storage + ':note_email_is_warning_not_sixth_blocker', {'exit_code': result.returncode})
    restore(database, sanitized)
    safety = site / 'wp-content/mu-plugins/000-imagine-staging-safety.php'
    safety_bytes = safety.read_bytes()
    try:
        safety.unlink()
        mail = wp_json(site, 'mail-probe.php')
        assert_true(mail['mail_dispatch_calls'] == 1, storage + ':missing_mail_lock_reaches_memory_spy', mail)
        result = subject_command(site, 'verifier', password, context)
        assert_true(result.returncode != 0, storage + ':subject_rejects_missing_mail_lock', {'exit_code': result.returncode})
    finally:
        safety.write_bytes(safety_bytes)
    restore(database, sanitized)
    raw_db(database, storage, 'table-fixtures', {'E2E_TABLE_ACTION': 'personal'})
    result = subject_command(site, 'verifier', password, context)
    private_report = json.loads(result.stdout)
    assert_true(result.returncode != 0 and 'TABLE_PERSONNELLE_A_TRANCHER' in private_report.get('issues', []),
                storage + ':unknown_personal_table_requires_decision', {'issues': private_report.get('issues')})
    base_context = json.loads(context.read_text())
    try:
        for action in ('garder', 'vider', 'anonymiser'):
            raw_db(database, storage, 'table-fixtures', {'E2E_TABLE_ACTION': 'drop-personal'})
            restore(database, sanitized)
            raw_db(database, storage, 'table-fixtures', {'E2E_TABLE_ACTION': 'personal'})
            decision = {'action': action}
            if action == 'anonymiser':
                decision['columns'] = ['email']
            context.write_text(json.dumps(dict(base_context, table_decisions={'wp_imagine_e2e_personal': decision})))
            for phase in ('neutraliser', 'anonymiser', 'verifier'):
                result = subject_command(site, phase, password, context)
                assert_true(result.returncode == 0, storage + ':synthetic_decision:' + action + ':' + phase,
                            {'exit_code': result.returncode, 'decision_is_synthetic_not_Ced_approval': True})
            status = raw_db(database, storage, 'table-fixtures', {'E2E_TABLE_ACTION': 'status'})
            assert_true(status['personal_rows'] == (0 if action == 'vider' else 1) and status['personal_email_safe'],
                        storage + ':synthetic_decision_effect:' + action, status)
    finally:
        context.write_text(json.dumps(base_context))
        raw_db(database, storage, 'table-fixtures', {'E2E_TABLE_ACTION': 'drop-personal'})
    restore(database, sanitized)
    for name in ('neutraliser', 'anonymiser', 'verifier'):
        result = subject_command(site, name, password, context)
        assert_true(result.returncode == 0, storage + ':rerun:' + name, {'exit_code': result.returncode})
    assert_true(raw_db(database, storage, 'snapshot')['orders'] == before_raw['orders'],
                storage + ':rerun_preserves_business_fields', 'Same fixture invariants after a second pass')


def main():
    mode = sys.argv[1]
    status = 0
    process = None
    try:
        process = database_start()
        record('runtime_versions', 'PASS', {
            'php': command(['php', '-r', 'echo PHP_VERSION;']).stdout.strip(),
            'mariadb': command(['mariadb', '--socket=' + SOCKET, '--user=root', '--batch', '--skip-column-names', '-e', 'SELECT VERSION()']).stdout.strip(),
            'wp_cli': command(['wp', '--allow-root', 'cli', 'version']).stdout.strip()})
        for path in ROOT.glob('*.php'):
            command(['php', '-l', str(path)])
        record('php_fixture_syntax', 'PASS', 'All copied PHP fixtures passed php -l')
        for storage in ('classic', 'hpos'):
            try:
                site, database, before = install(storage)
                if mode == 'fixture-selftest':
                    selftest(site, database, storage, before)
                elif mode == 'acceptance':
                    acceptance(site, database, storage, before)
                else:
                    raise RuntimeError('Unknown mode')
            except Exception as exc:
                record(mode + ':' + storage, 'BLOCKED' if 'DEPENDENCY_NOT_READY' in str(exc) else 'FAIL', str(exc))
                status = 2
        record('paid_plugins', 'NOT_TESTED', {'subscriptions': 'Not installed; no licensed code available',
            'memberships': 'Not installed; no licensed code available', 'not_simulated_as_passed': True})
        record('real_staging_and_start_gate', 'NOT_TESTED', 'No real staging, HTTP start, orchestration tool, Novamira, bascule or third-party service used')
    except Exception as exc:
        record(mode, 'BLOCKED' if 'DEPENDENCY_NOT_READY' in str(exc) else 'FAIL', str(exc))
        status = 2
    finally:
        if process:
            command(['mariadb-admin', '--socket=' + SOCKET, '--user=root', 'shutdown'], check=False, timeout=30)
            process.wait(timeout=30)
        (REPORT / 'result.json').write_text(json.dumps({'mode': mode, 'exit_code': status, 'checks': CHECKS}, indent=2, ensure_ascii=False) + '\n')
    return status


if __name__ == '__main__':
    sys.exit(main())
