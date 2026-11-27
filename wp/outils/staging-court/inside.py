"""Offline archive -> faithful files -> native cleanup -> report. No web publication."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import sys
import time
from urllib.parse import urlsplit

from archive import Refusal, restore, audit, check_space, ARCHIVE_REFUSALS
from core_source import plugin_warnings, manifest_settings_values
from legacy_importer import sql_plan, CREATE_WORDS
from diagnostics import execute, CommandFailure, php_error

# Narrow grammar additions required by SHOW CREATE from the existing synthetic baseline.
# No new statement type, trigger, procedure, executable comment or general SQL fallback.
CREATE_WORDS.update({'ON', 'UPDATE', 'UTF8MB3_GENERAL_CI'})

BASE = Path('/opt/court')
CORE = Path('/opt/wordpress/wordpress')
SITE = Path('/scratch/a01-site')
DB = 'imagine_a01_staging'
SOCKET = '/scratch/mariadb.sock'


def command(args, *, data=None, env=None, check=True, stage=None, timeout=300):
    stage = stage or {'mariadb-install-db':'database_initialize', 'mariadb-admin':'database_control',
                      'mariadb':'database_query', 'php':'native_phase'}.get(args[0], 'offline_command')
    return execute(args, input=data, capture_output=True, env={**os.environ, **(env or {})},
                   timeout=timeout, stage=stage, check=check,
                   database=args[0] == 'mariadb', php=args[0] == 'php')


def database_start():
    Path('/scratch').mkdir(exist_ok=True)
    data = Path('/scratch/court-db')
    command(['mariadb-install-db', '--datadir=' + str(data), '--auth-root-authentication-method=normal',
             '--skip-test-db', '--user=root'])
    process = subprocess.Popen(['mariadbd', '--user=root', '--datadir=' + str(data), '--socket=' + SOCKET,
                                '--skip-networking', '--skip-log-bin', '--pid-file=/scratch/court.pid',
                                '--log-error=/scratch/court-db.log', '--max-allowed-packet=256M',
                                '--sql-mode=NO_AUTO_VALUE_ON_ZERO'], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    for _ in range(100):
        if process.poll() is not None:
            raise CommandFailure('DATABASE_START_REFUSED', 'database_start', exit=process.returncode)
        if command(['mariadb-admin', '--socket=' + SOCKET, '--user=root', 'ping'], check=False).returncode == 0:
            return process
        time.sleep(.1)
    raise CommandFailure('DATABASE_START_TIMEOUT', 'database_start', timeout_seconds=10)


def isolation():
    if {p.name for p in Path('/sys/class/net').iterdir()} != {'lo'}:
        raise Refusal('NETWORK_REFUSED')
    for name in ('tcp', 'tcp6'):
        if any(row.split()[3] == '0A' for row in Path('/proc/net/' + name).read_text().splitlines()[1:]):
            raise Refusal('LISTENER_REFUSED')


def manifest(root):
    result = {}
    for p in sorted(root.rglob('*')):
        if p.is_symlink() or (not p.is_dir() and not p.is_file()):
            raise Refusal('FILE_TYPE_REFUSED')
        if p.is_file():
            with p.open('rb') as source:
                result[p.relative_to(root).as_posix()] = hashlib.file_digest(source, 'sha256').hexdigest()
    return result


def validate_core_version(package, version_file, expected=None):
    """Read metadata/PHP as data only. No source-core substitution or upgrade."""
    try:
        metadata = json.loads(package)
        source = metadata['WordPress']['Version']
        if not isinstance(source, str) or not re.fullmatch(r'[0-9]+\.[0-9]+(?:\.[0-9]+)?', source):
            raise ValueError
    except (TypeError, ValueError, KeyError):
        raise Refusal('SOURCE_CORE_METADATA_REFUSED') from None
    try:
        matches = re.findall(r"^\s*\$wp_version\s*=\s*'([0-9]+\.[0-9]+(?:\.[0-9]+)?)';", version_file.read_text(), re.M)
        if len(matches) != 1:
            raise ValueError
    except (OSError, ValueError):
        raise Refusal('PINNED_CORE_VERSION_REFUSED') from None
    versions = {'source': source, 'pinned': matches[0]}
    if expected is not None:
        if not isinstance(expected, str) or not re.fullmatch(r'[0-9]+\.[0-9]+(?:\.[0-9]+)?', expected):
            raise Refusal('EXPECTED_CORE_VERSION_REFUSED')
        versions['expected'] = expected
        if matches[0] != expected:
            error = Refusal('PINNED_CORE_EXPECTED_VERSION_MISMATCH')
            error.core_versions = versions
            raise error
    if source != matches[0]:
        error = Refusal('SOURCE_CORE_VERSION_MISMATCH')
        error.core_versions = versions
        raise error
    return versions


def archive_capacity_preflight(archive, request):
    with Path(archive).open('rb') as source:
        report = audit(source, **request.get('archive_limits', {}))['report']
    for rule in report['rules']:
        if rule['blocking']:
            raise Refusal(rule['code'], rule)
    check_space(SITE, report['total_bytes'] + 3 * report['database_bytes'])
    return report


def restore_and_verify(archive, request):
    isolation()
    if SITE.exists():
        raise Refusal('FRESH_SITE_REQUIRED')
    target = request['target_url']
    production = urlsplit(request['production_url'])
    url = urlsplit(target)
    if (url.scheme not in ('http', 'https') or not re.fullmatch(r'localhost|[a-z0-9.-]+\.(?:test|localhost|invalid)', url.hostname or '')
            or url.username or url.password or url.path or url.query or url.fragment
            or not production.hostname or production.hostname == url.hostname):
        raise Refusal('TARGET_REFUSED')
    if not isinstance(request.get('decisions', {}), dict):
        raise Refusal('DECISIONS_REFUSED')
    password = request['password']
    if not isinstance(password, str) or not 20 <= len(password.encode()) <= 72 or any(c in password for c in '\r\n\0'):
        raise Refusal('ADMIN_PASSWORD_REFUSED')
    # Pinned core is usable only after an exact package/core comparison below.
    # No PHP or database import executes before that gate.
    limits = request.get('archive_limits', {})
    archive_capacity_preflight(archive, request)
    shutil.copytree(CORE, SITE)
    shutil.rmtree(SITE / 'wp-content')
    archive_report = {}
    with Path(archive).open('rb') as stream:
        sql, package, count = restore(stream, SITE / 'wp-content', report=archive_report,
                                      sql_path=SITE.parent / 'a01-source.sql', **limits)
    core_versions = validate_core_version(package, CORE / 'wp-includes/version.php', request.get('expected_core_version'))
    manifest_settings = manifest_settings_values(package, SITE / 'wp-content')
    before = manifest(SITE / 'wp-content')
    # SQL stays on disk; validate every bounded statement before any import.
    from sql_stream import validate_file
    import legacy_importer
    normalized = SITE.parent / 'a01-validated.sql'
    if normalized.exists():
        normalized.unlink()
    plan = validate_file(sql, legacy_importer, normalized, decisions=request.get('decisions', {}))
    prefix = plan['prefix']
    import_report = import_database(normalized)
    sql.unlink(); normalized.unlink()
    # Independent engine readback: the import must preserve, not convert, engines.
    engine_rows = command(['mariadb', '--socket=' + SOCKET, '--user=root', '--skip-column-names', '-e',
                           "SELECT TABLE_NAME,ENGINE FROM information_schema.TABLES WHERE TABLE_SCHEMA='" + DB + "'"], stage='database_engine_readback').stdout.decode().splitlines()
    engines = {row.split('\t')[0]: row.split('\t')[1].upper() for row in engine_rows}
    if engines != plan['table_engines']:
        raise Refusal('TABLE_ENGINE_READBACK_REFUSED')
    for option, value in manifest_settings.items():
        encoded = value.encode().hex()
        sql = "UPDATE `" + prefix + "options` SET option_value=0x" + encoded + " WHERE option_name='" + option + "';"
        command(['mariadb', '--socket=' + SOCKET, '--user=root', DB], data=sql.encode(), stage='manifest_settings_restore')
        readback = command(['mariadb', '--socket=' + SOCKET, '--user=root', '--skip-column-names', DB,
            '-e', "SELECT HEX(option_value) FROM `" + prefix + "options` WHERE option_name='" + option + "'"], stage='manifest_settings_readback').stdout.decode().strip().lower()
        if readback != encoded:
            raise Refusal('SOURCE_SETTINGS_METADATA_REFUSED')
    # Only target home/siteurl are rewritten before the native context guard. No WP bootstrap yet.
    update = "UPDATE `" + prefix + "options` SET option_value='" + target.replace("'", "''") + "' WHERE option_name IN ('home','siteurl');"
    command(['mariadb', '--socket=' + SOCKET, '--user=root', DB], data=update.encode(), stage='target_url_rewrite')
    config = """<?php
    define('DB_NAME','imagine_a01_staging'); define('DB_USER','root'); define('DB_PASSWORD','');
    define('DB_HOST','localhost:/scratch/mariadb.sock'); define('DB_CHARSET','utf8mb4'); define('DB_COLLATE','');
    define('WP_ENVIRONMENT_TYPE','staging'); define('WP_HTTP_BLOCK_EXTERNAL',true);
    define('DISABLE_WP_CRON',true); define('AUTOMATIC_UPDATER_DISABLED',true); define('WP_AUTO_UPDATE_CORE',false);
    define('DISALLOW_FILE_MODS',true); define('DISALLOW_FILE_EDIT',true); define('WP_DEBUG',false);
    $table_prefix=PREFIX;
    define('ABSPATH',__DIR__.'/'); require_once ABSPATH.'wp-settings.php';
    """.replace('PREFIX', repr(prefix))
    (SITE / 'wp-config.php').write_text(config)
    os.chmod(SITE / 'wp-config.php', 0o600)
    (SITE / '.imagine-staging-offline').write_text('OFFLINE_COPY\n')
    context = {'environment': 'staging', 'isolated': True, 'restored': True, 'database': DB,
               'wp_path': str(SITE), 'target_url': target, 'production_hosts': [production.hostname],
               'prefix': prefix, 'table_decisions': plan['table_decisions'], 'table_policy_version':plan['table_policy_version']}
    # Private worker context is created before any PHP/plugin bootstrap, outside the site.
    # IDs are never exported in the public report and never reconstructed after purge.
    context['form_post_ids'] = form_post_provenance(prefix)
    Path('/scratch/a01-context.json').write_text(json.dumps(context))
    os.chmod('/scratch/a01-context.json', 0o600)
    steps = []
    report = {'ok': False, 'issues': ['NOT_VERIFIED']}
    for phase in ('neutraliser', 'anonymiser', 'verifier'):
        p = command(['php', '/subject/' + phase, '--worker-bridge', str(BASE / 'bridge.php')],
                    data=(password + '\n').encode() if phase == 'anonymiser' else b'',
                    env={'A01_CONTEXT': '/scratch/a01-context.json', 'WP_ENVIRONMENT_TYPE': 'staging'}, check=False, stage='native_' + phase)
        try:
            report = json.loads(p.stdout)
        except ValueError:
            report = {'ok': False, 'issues': ['REPORT_INVALID'], 'failure': {
                'stage': 'native_' + phase, 'code': 'PHP_REPORT_INVALID', 'php': php_error(p.stderr), 'exit': p.returncode}}
        if p.returncode and 'failure' not in report:
            report['failure'] = {'stage':'native_' + phase, 'code':'NATIVE_PHASE_REFUSED', 'exit':p.returncode,
                                 'php':php_error(p.stderr)}
        steps.append({'phase': phase, 'exit': p.returncode, 'report': report})
        if p.returncode or report.get('ok') is not True:
            break
    verified = len(steps) == 3 and all(step['exit'] == 0 for step in steps)
    result = {'status': 'verified-offline' if verified else 'imported', 'data_verified': verified,
              'core_versions': core_versions, 'archive_report': archive_report,
              'manifest_settings_restored_readback': sorted(manifest_settings),
              'table_engines': engines,
              'sql_policy': plan,
              'database_import': import_report,
              'warnings': ([{'code': 'NON_INNODB_TABLE', 'table': table, 'engine': engine}
                           for table, engine in sorted(engines.items()) if engine != 'INNODB']
                           + plugin_warnings(SITE / 'wp-content', core_versions['source'], request.get('php_version', '8.2'))),
              'import_installed_or_updated_plugins': False,
              'steps': steps, 'archive_entries': count, 'restored_files_before_cleanup': before,
              'files_after_cleanup': manifest(SITE / 'wp-content'),
              'publication': 'NOT_IMPLEMENTED: no port or egress is opened; site remains stopped',
              'shared_tool_modified': False, 'no_Novamira': True}
    return result


def form_post_provenance(prefix):
    """Read only IDs before native deletion; never infer provenance from orphan meta."""
    forms = json.loads((BASE.parent / 'staging/form-policy.json').read_bytes())
    types = forms['post_types']
    if (not types or not all(isinstance(t, str) and t.isascii() and t.replace('_', '').isalnum()
                             for t in types)):
        raise Refusal('TABLE_POLICY_REFUSED')
    sql = ("SELECT ID FROM `" + prefix + "posts` WHERE post_type IN ("
           + ','.join("'" + t + "'" for t in types) + ");"
           + "SELECT ID,post_parent FROM `" + prefix + "posts` WHERE post_type='revision';")
    raw = command(['mariadb', '--socket=' + SOCKET, '--user=root', '--batch', '--skip-column-names', DB],
                  data=sql.encode(), stage='form_provenance').stdout
    ids, revisions = set(), []
    for line in raw.splitlines():
        parts = line.split(b'\t')
        if len(parts) not in (1, 2) or not all(p.isdigit() for p in parts):
            raise Refusal('TABLE_POLICY_REFUSED')
        numbers = [int(p) for p in parts]
        if len(numbers) == 1:
            ids.add(numbers[0])
        else:
            revisions.append(numbers)
    while True:
        additions = {child for child, parent in revisions if parent in ids} - ids
        if not additions:
            return sorted(ids)
        ids.update(additions)


def import_database(normalized):
    """One bounded import contract shared by publication and base-only diagnosis."""
    command(['mariadb', '--socket=' + SOCKET, '--user=root', '-e', 'CREATE DATABASE ' + DB], stage='database_create')
    started = time.monotonic()
    with normalized.open('rb') as source:
        execute(['mariadb', '--socket=' + SOCKET, '--user=root', '--binary-mode',
                 '--max-allowed-packet=256M', '--init-command=SET SESSION sql_mode=\'NO_AUTO_VALUE_ON_ZERO\'', DB],
                stdin=source, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=3600,
                stage='database_import', database=True, sql_path=normalized)
    return {'elapsed_seconds':round(time.monotonic()-started, 3), 'timeout_seconds':3600,
            'max_allowed_packet_bytes':268435456, 'fallback_sql_mode':'NO_AUTO_VALUE_ON_ZERO',
            'source_mode_policy':'explicit supported SET SQL_MODE retained; exporter without mode uses non-strict fallback'}


# Closed diagnostics: imported text, SQL identifiers and exception messages are
# never copied to the publication report, even if they look like uppercase tags.
FAILURE_STAGES = {
    **{code: 'archive_restore' for code in ARCHIVE_REFUSALS},
    **{code: 'archive_restore' for code in (
        'ARCHIVE_TRUNCATED', 'ARCHIVE_INVALID', 'ARCHIVE_HEADER', 'ARCHIVE_PATH',
        'ARCHIVE_LIMIT', 'ARCHIVE_LAYOUT_UNSUPPORTED', 'MULTISITE_UNSUPPORTED',
        'FRESH_CONTENT_REQUIRED', 'FILE_TYPE_REFUSED')},
    **{code: 'core_preflight' for code in (
        'SOURCE_CORE_METADATA_REFUSED', 'PINNED_CORE_VERSION_REFUSED', 'SOURCE_CORE_VERSION_MISMATCH',
        'EXPECTED_CORE_VERSION_REFUSED', 'PINNED_CORE_EXPECTED_VERSION_MISMATCH', 'SOURCE_SETTINGS_METADATA_REFUSED')},
    **{code: 'sql_preflight' for code in (
        'SQL_ENCODING', 'SQL_GRAMMAR', 'SQL_TERMINATOR', 'SQL_IDENTIFIER', 'SQL_TABLE',
        'SQL_DDL', 'SQL_DDL_UNSUPPORTED', 'SQL_INSERT', 'SQL_INSERT_LITERAL',
        'SQL_STATEMENT', 'SQL_PREFIX', 'SQL_STATEMENT_LIMIT', 'SQL_INSERT_COLUMN_COUNT', 'SQL_TRANSACTION',
        'SQL_INSERT_FRAMING', 'TABLE_POLICY_REFUSED', 'DECISION_INVALIDE', 'TABLE_PERSONNELLE_A_TRANCHER', 'FORM_MESSAGES_DECISION_REFUSED',
        'SQL_COLLATION_UNSUPPORTED', 'SQL_MODE_UNSUPPORTED', 'SQL_EXECUTABLE_OBJECT_REFUSED')},
    **{code: 'request_validation' for code in (
        'FRESH_SITE_REQUIRED', 'TARGET_REFUSED', 'DECISIONS_REFUSED', 'ADMIN_PASSWORD_REFUSED', 'REQUEST_LIMIT')},
    **{code: 'isolation' for code in ('NETWORK_REFUSED', 'LISTENER_REFUSED')},
    **{code: 'database' for code in ('DATABASE_START_REFUSED', 'DATABASE_START_TIMEOUT', 'COMMAND_REFUSED', 'TABLE_ENGINE_READBACK_REFUSED')},
}


def execute_offline_request(archive, request, start_database):
    """Always return a safe receipt, including failures before native cleanup."""
    try:
        if start_database:
            archive_capacity_preflight(archive, request)
            database_start()
        return restore_and_verify(archive, request)
    except Exception as exc:
        return failure_receipt(exc)


def failure_receipt(exc):
        if isinstance(exc, CommandFailure):
            return {'status':'refused', 'data_verified':False, 'issues':[str(exc)], 'failure':exc.failure}
        from legacy_importer import Refusal as SQLRefusal
        code = str(exc) if isinstance(exc, (Refusal, SQLRefusal)) else 'IMPORT_REFUSED'
        if code.startswith('SQL_DDL_UNSUPPORTED_'):
            code = 'SQL_DDL_UNSUPPORTED'
        if code not in FAILURE_STAGES:
            code = 'IMPORT_REFUSED'
        receipt = {'status': 'refused', 'data_verified': False, 'issues': [code],
                   'failure': {'stage': FAILURE_STAGES.get(code, 'offline_restore'), 'code': code}}
        if isinstance(exc, Refusal) and exc.detail is not None and code != 'IMPORT_REFUSED':
            receipt['failure']['detail'] = exc.detail
        if code in ('SOURCE_CORE_VERSION_MISMATCH', 'PINNED_CORE_EXPECTED_VERSION_MISMATCH'):
            receipt['core_versions'] = exc.core_versions
        return receipt


def main():
    process = None
    output = {'status': 'refused', 'data_verified': False}
    try:
        isolation()
        request = json.loads(sys.stdin.buffer.read(16385))
        if len(json.dumps(request)) > 16384:
            raise Refusal('REQUEST_LIMIT')
        archive_capacity_preflight('/input/source.wpress', request)
        process = database_start()
        output = restore_and_verify('/input/source.wpress', request)
        if output['data_verified']:
            # Native data verification is not a fully exposed/usable staging.
            output['status'] = 'imported'
            output['verification_state'] = 'DATA_VERIFIED_PUBLICATION_BLOCKED'
            output['issues'] = ['PUBLICATION_AND_UPDATE_EGRESS_NOT_IMPLEMENTED']
            output['full_staging_ready'] = False
    except Exception as exc:
        output = failure_receipt(exc)
    finally:
        if process:
            command(['mariadb-admin', '--socket=' + SOCKET, '--user=root', 'shutdown'], check=False)
            process.wait(timeout=30)
        Path('/report').mkdir(exist_ok=True)
        Path('/report/court.json').write_text(json.dumps(output, indent=2))
    print(json.dumps({'status': output['status'], 'data_verified': output['data_verified'], 'runtime': 'stopped'}))
    return 78 if output['data_verified'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
