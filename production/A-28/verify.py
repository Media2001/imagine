"""Read-only A28 verification. No arguments: exactly the current final packet."""
import hashlib
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
PACKET = Path('production/A-28/preuves/final')
TABLES = ['fluentform_submissions', 'fluentform_entry_details', 'fluentform_submission_meta',
          'fluentform_logs', 'fluentform_draft_submissions', 'ff_scheduled_actions']
TYPES = ['flamingo_inbound', 'flamingo_contact']


def need(ok, code):
    if not ok:
        raise ValueError(code)


def load(path):
    return json.loads(path.read_bytes())


def readme_contract(raw, lines, commands):
    for line in lines:
        need(raw.splitlines(keepends=True).count(line.encode('utf-8')) == 1, 'README_LINES')
    previous = -1
    for block in commands:
        value = block.encode('utf-8')
        need(raw.count(value) == 1, 'CED_COMMAND_CHANGED')
        at = raw.index(value)
        need(at > previous, 'CED_COMMAND_ORDER')
        previous = at


def orphan_contract(probe, result):
    need(probe['mutation'] == 'omit_only_postmeta_purge' and probe['source_restored'] is True
         and probe['known_parent_posts'] == probe['known_revision_posts'] == 0
         and probe['known_orphan_meta'] == probe['provenance_ids_count'] == 4, 'ORPHAN_PROVENANCE')
    need(result['data_verified'] is False and [s['phase'] for s in result['steps']] == ['neutraliser', 'anonymiser', 'verifier']
         and [s['exit'] for s in result['steps']] == [0, 0, 1], 'ORPHAN_IMPORT')
    for key in ('refused', 'restored'):
        row = probe[key]
        need(row['exit'] == 1 and row['stderr_empty'] is True and row['report']['ok'] is False
             and row['report']['form_message_residues'] == 4
             and 'FORM_MESSAGES_REMAIN' in row['report']['issues']
             and 'SONDE_NON_EXECUTEE_DONNEES_REFUSEES' in row['report']['warnings'], 'ORPHAN_REFUSAL')
    row = probe['mutant']
    need(row['exit'] == 0 and row['stderr_empty'] is True and row['report']['ok'] is True
         and row['report']['form_message_residues'] == 4, 'ORPHAN_MUTATION')
    oracle = probe['oracle']
    need(oracle['known_meta'] == 4 and oracle['known_revisions'] == 0
         and all(oracle[t] == 0 for t in TYPES + TABLES)
         and oracle['fiction_magazine'] == 1, 'ORPHAN_ORACLE')


def native_contract(data, baseline=False):
    need(data['status'] == 'PASS' and data['synthetic_only'] is True and data['baseline'] is baseline, 'NATIVE_STATUS')
    checks = data['checks']
    need(checks and all(c['pass'] is True for c in checks) and data['failed'] == 0 and data['passed'] == len(checks), 'NATIVE_CHECKS')
    modes = ['default', 'keep-unknown', 'keep-known'] if baseline else ['default', 'keep-unknown', 'keep-known', 'anonymise-known', 'omit-meta-purge']
    expected = {(storage, mode) for storage in ('classic', 'hpos') for mode in modes}
    cases = data['cases']
    need(len(cases) == len(expected) and {(c['storage'], c['mode']) for c in cases} == expected, 'NATIVE_MATRIX')
    for case in cases:
        need(re.fullmatch('[0-9a-f]{64}', case['archive_sha256']) is not None, 'NATIVE_ARCHIVE')
        mode = case['mode']
        result = case['result']
        if mode == 'omit-meta-purge':
            orphan_contract(case['postmeta_purge_witness'], result)
            continue
        if baseline or mode in ('default', 'keep-unknown'):
            need(result['data_verified'] is True and [s['phase'] for s in result['steps']] == ['neutraliser', 'anonymiser', 'verifier']
                 and all(s['exit'] == 0 and s['report']['ok'] is True for s in result['steps']), 'NATIVE_PHASES')
            oracle = case['oracle']
            for table in TABLES:
                retained = int(baseline and mode == 'keep-known' and table == TABLES[0])
                need(oracle[table] == retained and oracle['canary_rows'][table] == retained, 'NATIVE_KNOWN_TABLE')
            need(oracle['fiction_messages'] == int(mode == 'keep-unknown'), 'NATIVE_UNKNOWN_TABLE')
            need(all(oracle[t] == int(baseline) for t in TYPES), 'NATIVE_KNOWN_TYPE')
            need(oracle['fiction_magazine'] == 1 and oracle['known_meta'] == (4 if baseline else 0)
                 and oracle['known_revisions'] == (2 if baseline else 0), 'NATIVE_POST_STORAGE')
            need(case['protected_before'] == case['protected_after'], 'NATIVE_IMMUTABILITY')
            if not baseline:
                need(all(oracle['post_canary_rows'][t] == 0 for t in TYPES)
                     and oracle['post_canary_rows']['fiction_magazine'] == 1, 'NATIVE_POST_CANARIES')
            if not baseline and mode == 'default':
                keeps = case['native_keep_probes']
                need(len(keeps) == len(TABLES) and {p['kind'] for p in keeps} == set(TABLES), 'NATIVE_KEEP_COVERAGE')
                for probe in keeps:
                    exact = {'ok': False, 'issues': ['STAGING_REFUSE', 'FORM_MESSAGES_DECISION_REFUSED'],
                             'failure': {'stage': 'native_neutraliser', 'code': 'FORM_MESSAGES_DECISION_REFUSED', 'table': probe['kind']}}
                    need(probe['refused'] == {'exit': 78, 'report': exact, 'stderr_empty': True}
                         and probe['database_unchanged'] is True and probe['files_unchanged'] is True, 'NATIVE_KEEP_REFUSAL')
                probes = case['residue_probes']
                need(len(probes) == len(TABLES + TYPES) and {p['kind'] for p in probes} == set(TABLES + TYPES), 'NATIVE_MUTATION_COVERAGE')
                for probe in probes:
                    need(probe['source_restored'] is True, 'NATIVE_MUTATION_RESTORE')
                    for key in ('refused', 'restored'):
                        row = probe[key]
                        need(row['exit'] == 1 and row['stderr_empty'] is True and row['report']['ok'] is False
                             and 'FORM_MESSAGES_REMAIN' in row['report']['issues']
                             and row['report']['form_message_residues'] == 1, 'NATIVE_RESIDUE_REFUSAL')
                    need(probe['mutant']['exit'] == 0 and probe['mutant']['report']['ok'] is True
                         and probe['mutant']['report']['form_message_residues'] == 1, 'NATIVE_MUTATION_WITNESS')
        else:
            need(result == {'status': 'refused', 'data_verified': False, 'issues': ['FORM_MESSAGES_DECISION_REFUSED'],
                            'failure': {'stage': 'sql_preflight', 'code': 'FORM_MESSAGES_DECISION_REFUSED',
                                        'detail': {'table': TABLES[0]}}}, 'NATIVE_PREFLIGHT_REFUSAL')


def runner_contract(base, root, baseline=False):
    row = load(base / 'runner.json')
    need(row['status'] == 'PASS' and row['synthetic_only'] is True and row['sources_unchanged'] is True, 'RUNNER_STATUS')
    need(row['owner_label'] == 'org.imagine.a28-synthetic' and row['cleanup'] == {'name': row['runner'], 'absent': True}, 'RUNNER_CLEANUP')
    for key in ('isolation_before', 'isolation_after'):
        iso = row[key]
        need(iso['network'] == 'none' and iso['mounts'] == [] and iso['ports'] == [] and iso['privileged'] is False
             and iso['no_new_privileges'] is True and 'ALL' in iso['cap_drop'], 'RUNNER_ISOLATION')
    if baseline:
        need(len(row['commands']) == 1 and row['commands'][0]['key'] == 'native', 'RUNNER_COMMANDS')
    for command in row['commands']:
        need(command['exit'] == 0, 'RUNNER_EXIT')
        for stream in ('stdout', 'stderr'):
            need(hashlib.sha256((base / (command['key'] + '.' + stream + '.log')).read_bytes()).hexdigest() == command[stream + '_sha256'], 'RUNNER_LOG')
    if not baseline:
        need({c['key'] for c in row['commands']} == {'native', 'a01-python', 'a01-data', 'a01-test_database_policy',
             'a01-test_diagnostics', 'a01-test_native_file_policy', 'unit', 'lint', 'nonform-differential'}, 'RUNNER_COMMANDS')
        for rel, digest in row['source_manifest'].items():
            need(hashlib.sha256((root / rel).read_bytes()).hexdigest() == digest, 'RUNNER_SOURCE_DRIFT')
        pure = load(base / 'unit.json')
        need(pure['exit_code'] == 0 and pure['checks'] and all(c['status'] == 'PASS' for c in pure['checks']), 'PURE_TESTS')
        a01 = load(base / 'a01-data.json')
        need(a01['ok'] is True and a01['cases'] == 9 and a01['assertions'] > 0, 'A01_DATA')
        differential = load(base / 'nonform-differential.json')
        need(differential['status'] == 'PASS' and differential['exact_nonform_tables_and_report_and_historical_refusals'] is True
             and differential['only_report_addition'] == {'form_message_residues': 0}, 'NONFORM_DIFF')
    return row


def gates_contract(base, root):
    data = load(base / 'result.json')
    need(data['status'] == 'PASS' and data['exit'] == 0 and data['sources_stable'] is True, 'GATES_STATUS')
    commands = load(base / 'commands.json')
    names = {'environment-utf8', 'environment-cp1252', 'python-utf8', 'python-cp1252', 'a01-windows-utf8',
             'a01-windows-cp1252', 'prepare-image', 'global-utf8', 'global-cp1252'}
    need(len(commands) == len(names) == data['commands'] and {r['name'] for r in commands} == names, 'GATES_COVERAGE')
    for row in commands:
        need(row['exit'] == 0 and row['sources_stable'] is True, 'GATE_EXIT')
        for stream in ('stdout', 'stderr'):
            need(hashlib.sha256((base / (row['name'] + '.' + stream + '.log')).read_bytes()).hexdigest() == row[stream + '_sha256'], 'GATE_LOG')
        if row['name'].startswith(('python-', 'a01-windows-')):
            need(row['tests'] > 0, 'PYTHON_TEST_COUNT')
        if row['name'].startswith('global-'):
            text = (base / (row['name'] + '.stdout.log')).read_text(encoding='utf-8')
            matches = re.findall(r'^REJEU : (\d+) tests, (\d+) assertions, 0 .*?PASS\s*$', text, re.M)
            need(len(matches) == 1 and int(matches[0][0]) > 0, 'GLOBAL_RESULT')
    for suffix, encoding, mode in [('utf8', 'utf-8', 1), ('cp1252', 'cp1252', 0)]:
        env = load(base / ('environment-' + suffix + '.stdout.log'))
        need(env['stdout'].lower() == encoding and env['stderr'].lower() == encoding and env['utf8'] == mode
             and env['version'].startswith('3.14.6 '), 'WINDOWS_ENCODING')
    for rel, digest in load(base / 'freeze.json')['sources'].items():
        need(hashlib.sha256((root / rel).read_bytes()).hexdigest() == digest, 'FROZEN_SOURCE_DRIFT')


def matrix_contract(base, root, historical):
    matrix = load(base / 'matrix.json')
    need(matrix['status'] == 'PASS' and matrix['contexts'] == ['utf8', 'cp1252'] and len(matrix['commands']) == 2, 'MATRIX_STATUS')
    total_cases = total_mutations = 0
    for context, encoding, mode in [('utf8', 'utf-8', 1), ('cp1252', 'cp1252', 0)]:
        command = next(r for r in matrix['commands'] if r['context'] == context)
        need(command['exit'] == 0 and command['sources_stable'] is True, 'MATRIX_EXIT')
        for stream in ('stdout', 'stderr'):
            need(hashlib.sha256((base / (context + '.' + stream + '.log')).read_bytes()).hexdigest() == command[stream + '_sha256'], 'MATRIX_LOG')
        folder = base / context
        env = load(folder / 'environment.json')
        need(env['platform'] == 'win32' and env['version'].startswith('3.14.6 ') and env['stdout'] == encoding
             and env['stderr'] == encoding and env['utf8'] == mode, 'MATRIX_ENCODING')
        runner = runner_contract(folder, root)
        need(all(runner['reference_manifest'][name] == historical['wp/outils/staging/' + name]
                 for name in ('lib.php', 'command.php')), 'REFERENCE_SOURCE')
        data = load(folder / 'native.json')
        native_contract(data)
        total_cases += len(data['cases'])
        total_mutations += sum(len(c.get('residue_probes', [])) for c in data['cases'])
    for rel, digest in load(base / 'freeze.json').items():
        need(hashlib.sha256((root / rel).read_bytes()).hexdigest() == digest, 'MATRIX_SOURCE_DRIFT')
    return {'cases': total_cases, 'mutations': total_mutations}


def inventory(root):
    files = []
    for folder in ('wp/tests/a28', 'production/A-28'):
        files += [p for p in (root / folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts
                  and p.name not in ('PRET', 'manifest.json')]
    for folder in ('wp/outils/staging', 'wp/outils/staging-court'):
        files += [p for p in (root / folder).rglob('*') if p.is_file() and p.suffix in ('.py', '.php', '.json') and '__pycache__' not in p.parts]
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(files))}


def verify(root=ROOT):
    base = root / 'production/A-28'
    manifest = load(base / 'manifest.json')
    need(manifest['lot'] == 'A-28' and manifest['packet'] == PACKET.as_posix(), 'CURRENT_PACKET')
    need(manifest['files'] == inventory(root), 'PACKAGE_DRIFT')
    contract = load(base / 'readme-contract.json')
    readme_contract((root / 'wp/outils/staging-court/README.md').read_bytes(), contract['lines'], contract['commands'])
    packet = root / PACKET
    runner_contract(packet / 'before', root, baseline=True)
    native_contract(load(packet / 'before/native.json'), baseline=True)
    historical = load(packet / 'before/runner.json')['source_manifest']
    matrix = matrix_contract(packet / 'native', root, historical)
    gates_contract(packet / 'gates', root)
    scope = load(packet / 'scope.json')
    need(all((r.get('owner') == 'voie2' and r['file'].startswith(('wp/outils/demo/', 'wp/tests/demo/')))
             or (r.get('owner') == 'parent/A29' and r['file'] == 'wp/tests/a02-audit/README.md')
             for r in scope['concurrent_owner_changes']), 'CONCURRENT_OWNER_SCOPE')
    need(scope['out_of_scope_changed'] == [] and scope['out_of_scope_added'] == [] and scope['ced_commands_unchanged'] is True
         and scope['readme_exact_three_lines'] is True and scope['common_guardian_unchanged'] is True
         and scope['old_packets_A23_A27_preserved'] is True, 'SCOPE_DRIFT')
    return {'lot': 'A-28', 'status': 'PASS', 'exit': 0, 'packet': PACKET.as_posix(),
            'native_cases': matrix['cases'], 'baseline_cases': 6, 'residue_mutations': matrix['mutations'], 'pret_present': (base / 'PRET').is_file()}


def main():
    try:
        need(__debug__ and len(sys.argv) == 1, 'NO_ARGUMENTS')
        result = verify()
    except Exception as error:
        result = {'lot': 'A-28', 'status': 'FAIL', 'exit': 1,
                  'code': str(error) if isinstance(error, ValueError) and re.fullmatch('[A-Z_]+', str(error)) else 'PACKET_REFUSED'}
    print(json.dumps(result))
    return result['exit']


if __name__ == '__main__':
    raise SystemExit(main())
