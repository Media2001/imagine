"""Actual whole-tour classic/HPOS exercise. Doubles are limited and named."""
import datetime
import importlib.util
import time
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys

sys.dont_write_bytecode = True


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


b = load('fixture', '/opt/a02/inside.py')
m = load('tournee', '/subject/wp/outils/bascule/tournee/tournee.py')
OUT = Path('/report')
BASE = Path('/subject/wp/outils/bascule')
ORIGINAL = b.check
PROCESS_EVENTS = []
TRACK_PROCESS = False


def process_audit(event, args):
    if TRACK_PROCESS and event == 'subprocess.Popen':
        PROCESS_EVENTS.append(list(args[1]))


sys.addaudithook(process_audit)


def check(name, ok, detail=None):
    if name.endswith(':commercial_fixture'):
        detail = {k: detail[k] for k in ('versions', 'hpos', 'subscriptions', 'rules', 'restriction_real')}
    return ORIGINAL(name, ok, detail)


b.check = check
b.audit = lambda site, out: b.cmd(['php', str(BASE / 'audit'), '--wp-path=' + str(site), '--output=' + str(out)], check=False)


def tour(site, audit, mapping, out):
    line = next(x for x in (BASE / 'tournee/README.md').read_text(encoding='utf-8').splitlines()
                if x.startswith('python3 wp/outils/bascule/tournee/tournee.py '))
    args = shlex.split(line)
    replacements = {'wp/outils/bascule/tournee/tournee.py': str(BASE / 'tournee/tournee.py'),
                    '--wp-path=/copie-verifiee': '--wp-path=' + str(site),
                    '--audit=/hors-web/audit-date/audit.json': '--audit=' + str(audit),
                    '--correspondance=/hors-web/correspondance.json': '--correspondance=' + str(mapping),
                    '--output=/hors-web/tournee-date': '--output=' + str(out)}
    args = [replacements.get(x, x) for x in args]
    p = subprocess.run(args, capture_output=True, timeout=1200,
                       env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONIOENCODING': 'utf-8'})
    return p, args


def run_storage(storage):
    global TRACK_PROCESS
    site, db, _ = b.install(storage)
    (OUT / (storage + '-seed.json')).unlink()
    cfg = (site / 'wp-config.php').read_text()
    writable = cfg.replace("define('DB_USER', 'a02_" + storage + "')", "define('DB_USER', 'root')").split("\nfile_put_contents('/scratch/a02-bootstrap-trap'")[0]
    (site / 'wp-config.php').write_text(writable)
    try:
        seeded = b.wp(site, ['eval-file', '/opt/a32/seed16.php', '--use-include'])
        check(storage + ':native_editorial_seed', 'A16_JSON=' in seeded.stdout)
        normalized = b.wp(site, ['eval', "foreach (get_posts(['post_type'=>'attachment','post_status'=>'inherit','numberposts'=>-1]) as $post) { $value=get_post_meta($post->ID,'_wp_attached_file',true); if (str_starts_with($value,'/scratch/a16-private/')) { update_post_meta($post->ID,'_wp_attached_file','a32-private-'.$post->ID.'.pdf'); } }"])
        if normalized.returncode != 0:
            raise RuntimeError('A32_FIXTURE_NORMALIZE')
        clock = b.wp(site, ['eval-file', '/opt/a32/clock_seed.php', '--use-include'], check=False)
        if clock.returncode:
            raise RuntimeError('A32_CLOCK_SETUP:' + clock.stderr[:900])
        clock_oracle = json.loads(next(line[len('A32_CLOCK='):] for line in clock.stdout.splitlines() if line.startswith('A32_CLOCK=')))
        check(storage + ':fixture_absolute_attachments_normalized_before_freeze', normalized.returncode == 0)
    finally:
        (site / 'wp-config.php').write_text(cfg)
    registry = site / 'wp-content/mu-plugins/a32-registry.php'
    registry.write_text("<?php register_post_type('a16_numero',['public'=>false]); register_post_type('a16_article',['public'=>false]); register_taxonomy('a16_theme','a16_article'); register_taxonomy('a16_issue','a16_article');")
    audit = OUT / (storage + '-audit')
    check(storage + ':audit_ready', b.audit(site, audit).returncode == 0)
    mapping = BASE / 'a16/correspondance.exemple.json'
    marker = site / '.imagine-staging-verified.json'
    marker.write_text(json.dumps({'status': 'verified', 'offline_verified': True, 'runtime_probe_passed': True}), encoding='utf-8')
    marker_bytes = marker.read_bytes()
    before, files_before = b.fingerprint(db), b.files(site)
    private_before = b.files(Path('/scratch/a16-private'))
    dest = OUT / (storage + '-complete')
    p, args = tour(site, audit / 'audit.json', mapping, dest)
    doc = json.loads((dest / 'bilan.json').read_text())
    check(storage + ':documented_command_exact_complete', p.returncode == 0 and p.stdout == b'A32_COMPLETE bilan.json bilan.md\n' and not p.stderr
          and doc['tournee'] == 'complète' and [r['outil'] for r in doc['outils']] == [e['lot'] for e in m.entries()]
          and all(r['statut'] == 'réussi' for r in doc['outils']), {'exit': p.returncode, 'rows': doc['outils']})
    (OUT / (storage + '-command.json')).write_text(json.dumps({'command': args, 'exit_code': p.returncode,
                                                              'per_tool_commands': [m.command(e, site, audit / 'audit.json', mapping, Path(r['rapport'])) for e, r in zip(m.entries(), doc['outils'])]}, indent=2))
    default16 = json.loads((OUT / (storage + '-complete-a16/numeros.json')).read_text())
    check(storage + ':a16_omitted_limit_still_default_ten', default16.get('limit') == 10
          and not any(arg.startswith('--limit=') for arg in m.command(next(e for e in m.entries() if e['lot'] == 'A16'), site, audit / 'audit.json', mapping, Path('/report/unused'))))
    check(storage + ':whole_nominal_db_files_immutable', before == b.fingerprint(db) and files_before == b.files(site)
          and private_before == b.files(Path('/scratch/a16-private')))
    # Deliberately named boundary doubles: A10 refusal / A11 exit 255 only.
    guard = load('a32_native_guard', BASE / 'stream_guard.py')
    calls = []
    mixed = OUT / (storage + '-named-doubles')
    def double_executor(command):
        index = len(calls)
        calls.append(command)
        if index == 0:
            return 1, b'', b'A10_AUDIT_GUARD\n'
        if index == 1:
            return 255, b'A32_DOUBLE_PRIVATE_CANARY', b'A32_DOUBLE_PRIVATE_CANARY'
        return guard.supervise(command, {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}, OUT, None, timeout=180)
    code = m.run(site, audit / 'audit.json', mapping, mixed, double_executor)
    mixed_doc = json.loads((mixed / 'bilan.json').read_text())
    check(storage + ':named_doubles_continue_every_remaining_real_tool', code == 1 and len(calls) == len(m.entries())
          and [r['statut'] for r in mixed_doc['outils']] == ['refusé', 'en échec'] + ['réussi'] * (len(m.entries()) - 2)
          and mixed_doc['outils'][0]['code'] == 'A10_AUDIT_GUARD' and mixed_doc['outils'][1]['sortie'] == 255)
    (OUT / (storage + '-doubles.json')).write_text(json.dumps({'declared_doubles': {'A10': 'refusal', 'A11': 'exit255'},
                                                             'exit_code': code, 'commands': calls}, indent=2))
    # C02: real A22 supervisor, named PHP boundary doubles for two outcomes.
    probe15 = Path('/scratch/a32-timeout.php')
    probe15.write_text('<?php usleep(5000000);')
    probe19 = Path('/scratch/a32-incomplete.php')
    probe19.write_text("<?php foreach($argv as $a){if(str_starts_with($a,'--output=')){$o=substr($a,9);mkdir($o);file_put_contents($o.'/coherence.json','{}');file_put_contents($o.'/coherence.md','incomplete');}} echo \"A19_OK coherence.json coherence.md\\n\";")
    supervision_codes = {}
    supervised_calls = []
    def supervision_executor(args):
        index = len(supervised_calls)
        supervised_calls.append(args)
        entry = m.entries()[index]
        lot = entry['lot']
        if lot not in ('A15', 'A19'):
            return guard.supervise(args, {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}, OUT, None, timeout=180)
        options = dict(arg.split('=', 1) for arg in args[2:])
        original_supervise = guard.supervise
        if lot == 'A15':
            def shortened(command, env, parent, fence, **kwargs):
                return original_supervise(command, env, parent, fence, **{**kwargs, 'timeout': 0.2})
            guard.supervise = shortened
        try:
            guard.inventory(lot, probe15 if lot == 'A15' else probe19, options)
            return 0, entry['success'].encode(), b''
        except RuntimeError as error:
            message = guard.public_error(error, lot)
            supervision_codes[lot] = message
            return 1, b'', (message + '\n').encode('ascii')
        finally:
            guard.supervise = original_supervise
    supervision_target = OUT / (storage + '-supervision-doubles')
    supervision_exit = m.run(site, audit / 'audit.json', mapping, supervision_target, supervision_executor)
    supervision_doc = json.loads((supervision_target / 'bilan.json').read_text())
    expected_codes = {'A15': 'A15_PROCESS_TIMEOUT', 'A19': 'A19_SUCCESS_INCOMPLETE'}
    check(storage + ':supervision_codes_preserved', supervision_exit == 1 and supervision_codes == expected_codes
          and len(supervised_calls) == len(m.entries()) and all(
              r['statut'] == 'refusé' and r.get('code') == expected_codes[r['outil']]
              if r['outil'] in expected_codes else r['statut'] == 'réussi' for r in supervision_doc['outils']))
    (OUT / (storage + '-supervision.json')).write_text(json.dumps({'declared_doubles': {'A15': 'PHP sleep; actual A22 timeout=0.2s', 'A19': 'PHP bound files with incomplete schema; actual A22 inventory'}, 'emitted_codes': supervision_codes, 'exit_code': supervision_exit, 'commands': supervised_calls}, indent=2) + '\n')
    # C03: actual native getters and A19 CLI, no clock mocked or tool changed.
    a19 = next(e for e in m.entries() if e['lot'] == 'A19')
    clock_rows = []
    for label, reference in [('current', None), ('later', None),
                             ('year_before', '2026-12-31T23:59:59Z'),
                             ('equality', '2027-01-01T00:00:00Z'),
                             ('year_after', '2027-01-01T00:00:01Z')]:
        if label == 'later':
            time.sleep(1.1)
        target = OUT / (storage + '-clock-' + label)
        argv = m.command(a19, site, audit / 'audit.json', mapping, target)
        if reference is not None:
            argv.append('--as-of=' + reference)  # explicit fixture boundary, never production default
        start = int(time.time())
        rc, stdout, stderr = guard.supervise(argv, {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}, OUT, None, timeout=180)
        stop = int(time.time())
        report = json.loads((target / 'coherence.json').read_text()) if target.exists() else {}
        instant = report.get('as_of_utc', '')
        stamp = int(datetime.datetime.fromisoformat(instant.replace('Z', '+00:00')).timestamp()) if instant else -1
        expected_count = sum(0 < date < stamp for date in clock_oracle['active_next_native'])
        actual_count = report.get('counts', {}).get('active_past_next_payment')
        good = (rc == 0 and stdout == a19['success'].encode() and stderr == b'' and actual_count == expected_count
                and (instant == reference if reference else start <= stamp <= stop)
                and (reference is not None or not any(arg.startswith('--as-of=') for arg in argv)))
        check(storage + ':a19_clock:' + label, good)
        clock_rows.append({'case': label, 'command': argv, 'exit_code': rc, 'as_of_utc': instant,
                           'start_utc': start, 'end_utc': stop, 'expected_count': expected_count, 'actual_count': actual_count})
    check(storage + ':a19_later_replay_advances_utc', clock_rows[1]['as_of_utc'] > clock_rows[0]['as_of_utc'])
    check(storage + ':a19_equality_and_year_change',
          clock_rows[3]['actual_count'] == clock_rows[2]['actual_count'] + 1
          and clock_rows[4]['actual_count'] == clock_rows[3]['actual_count'] + 1)
    (OUT / (storage + '-clock.json')).write_text(json.dumps({'oracle': clock_oracle, 'rows': clock_rows}, indent=2) + '\n')
    # Each channel is real site code. A10 is SQL-only and never loads these callbacks.
    cases = {
        'stdout': "fwrite(STDOUT,'A32_STREAM_PRIVATE_CANARY');",
        'stderr': "fwrite(STDERR,'A32_STREAM_PRIVATE_CANARY');",
        'early_exit': "echo 'A32_STREAM_PRIVATE_CANARY'; exit(0);",
        'silent_exit': 'exit(0);',
        'shutdown_stdout': "register_shutdown_function(static function(){fwrite(STDOUT,'A32_STREAM_PRIVATE_CANARY');});",
        'shutdown_stderr': "register_shutdown_function(static function(){fwrite(STDERR,'A32_STREAM_PRIVATE_CANARY');});",
        'report': "register_shutdown_function(static function(){foreach($GLOBALS['argv'] as $a){if(str_starts_with($a,'--output=')){foreach(glob(substr($a,9).'/*.json') as $f){$v=json_decode(file_get_contents($f),true);$v['private']='A32_REPORT_PRIVATE_CANARY';file_put_contents($f,json_encode($v));}}}});",
    }
    hostile = site / 'wp-content/mu-plugins/000-a32-hostile.php'
    channel_rows = []
    try:
        for label, statement in cases.items():
            hostile.write_text('<?php ' + statement)
            channel_before, channel_files = b.fingerprint(db), b.files(site)
            target = OUT / (storage + '-channel-' + label)
            q, _ = tour(site, audit / 'audit.json', mapping, target)
            data = json.loads((target / 'bilan.json').read_text())
            good = (q.returncode == 1 and q.stdout == b'A32_PARTIAL bilan.json bilan.md\n' and not q.stderr
                    and data['tournee'] == 'partielle' and data['outils'][0]['statut'] == 'réussi'
                    and all(r['statut'] != 'réussi' for r in data['outils'][1:]))
            clean = not any(b'A32_' + suffix in f.read_bytes() for suffix in (b'STREAM_PRIVATE_CANARY', b'REPORT_PRIVATE_CANARY', b'DOUBLE_PRIVATE_CANARY')
                            for f in OUT.rglob('*') if f.is_file())
            immutable = channel_before == b.fingerprint(db) and channel_files == b.files(site)
            check(storage + ':whole_tour_channel:' + label, good and clean and immutable,
                  {'closed': good, 'no_canary_retained': clean, 'db_files_immutable': immutable})
            channel_rows.append({'channel': label, 'per_tool': data['outils'], 'exit_code': q.returncode, 'clean': clean, 'immutable': immutable})
    finally:
        hostile.unlink(missing_ok=True)
    # Amended AFAIRE: one tour-side refusal before ANY child, no consumer edits.
    negatives = [('absent', None, cfg), ('invalid', b'[]', cfg),
                 ('fields', b'{"status":"verified","offline_verified":true,"runtime_probe_passed":false}', cfg),
                 ('production', marker_bytes, cfg.replace("'staging'", "'production'")),
                 ('environment_absent', marker_bytes, cfg.replace("define('WP_ENVIRONMENT_TYPE', 'staging');", '')),
                 ('define_in_string', marker_bytes, cfg.replace("define('WP_ENVIRONMENT_TYPE', 'staging');", '''$note = "define('WP_ENVIRONMENT_TYPE', 'staging');";''')),
                 ('define_in_comment', marker_bytes, cfg.replace("define('WP_ENVIRONMENT_TYPE', 'staging');", "/* define('WP_ENVIRONMENT_TYPE', 'staging'); */"))]
    for label, payload, config in negatives:
        try:
            marker.unlink(missing_ok=True)
            if payload is not None:
                marker.write_bytes(payload)
            (site / 'wp-config.php').write_text(config)
            unverified_before, unverified_files = b.fingerprint(db), b.files(site)
            target = OUT / (storage + '-unverified-' + label)
            PROCESS_EVENTS.clear()
            TRACK_PROCESS = True
            try:
                # Real default executor; Python audits every actual subprocess.
                m.run(site, audit / 'audit.json', mapping, target)
                refused = False
            except RuntimeError as error:
                refused = str(error) == 'A32_NOT_VERIFIED'
            finally:
                TRACK_PROCESS = False
            calls = list(PROCESS_EVENTS)
            q, argv = tour(site, audit / 'audit.json', mapping, target)
            negative = {'case': label, 'marker_exists': marker.exists(), 'exit_code': q.returncode,
                        'measurement': 'real_default_executor_python_audit_subprocess.Popen',
                        'stdout_empty': q.stdout == b'', 'stderr': q.stderr.decode('ascii'),
                        'command': argv, 'tools_launched': len(calls), 'commands': calls,
                        'output_absent': not target.exists() and not list(OUT.glob(target.name + '-*')),
                        'database_before': unverified_before, 'database_after': b.fingerprint(db),
                        'files_before': unverified_files, 'files_after': b.files(site)}
            (OUT / (storage + '-unverified-' + label + '-proof.json')).write_text(json.dumps(negative, indent=2) + '\n')
            check(storage + ':tour_guard_zero_tools:' + label, refused and not calls and q.returncode == 1
                  and q.stdout == b'' and q.stderr == b'A32_NOT_VERIFIED\n' and negative['output_absent']
                  and unverified_before == negative['database_after'] and unverified_files == negative['files_after'])
        finally:
            marker.write_bytes(marker_bytes)
            (site / 'wp-config.php').write_text(cfg)
    after, files_after = b.fingerprint(db), b.files(site)
    check(storage + ':whole_tour_all_tables_scheduler_files_immutable', before == after and files_before == files_after
          and private_before == b.files(Path('/scratch/a16-private')))
    check(storage + ':config_never_executed', not Path('/scratch/a02-bootstrap-trap').exists())
    for filename, value in [(storage + '-fingerprints.json', {'before': before, 'after': after, 'files_before': files_before, 'files_after': files_after}),
                            (storage + '-channels.json', channel_rows)]:
        (OUT / filename).write_text(json.dumps(value, indent=2) + '\n')


b.run_storage = run_storage
if __name__ == '__main__':
    sys.exit(b.main())
