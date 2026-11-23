"""Bounded read-only A-01 evidence validation. Never opens an archive or WordPress."""
import argparse
import datetime
import hashlib
import json
import pathlib
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[3]
TOOLS = ROOT / 'wp/outils/staging-court'
sys.path.insert(0, str(TOOLS))


def verify(report, live=False):
    report = report.resolve()
    assert any(report.is_relative_to(ROOT / 'production/A-01' / folder)
               for folder in ('publication-22nov', 'publication-23nov'))
    raw = report.read_bytes()
    value = json.loads(raw)
    assert value['status'] == 'PASS' and len(value['cases']) == 4
    assert not value.get('cleanup_errors')
    assert value['no_real_archive'] is True and value['no_agent_access_used'] is True
    assert value['tool_sources_unchanged'] is True and value['tool_or_templates_modified'] is False
    public69 = value['expected_core_version'] == '6.9.1'
    if public69:
        assert all(key in value for key in ('public_core', 'public_fixture_woocommerce', 'subscriptions_691_limit'))
        core = value['public_core']
        assert core['version'] == '6.9.1' and core['url'] == 'https://wordpress.org/wordpress-6.9.1.zip'
        assert core['sha256'] == '1c6ba9fc3ca6d5eb847666d82c0958c15878552387143ed61724ee81350fb120'
        assert core['bundled_wp_content_excluded'] is core['download_before_injection'] is True
        woo = value['public_fixture_woocommerce']
        assert woo['version'] == '11.0.1'
        assert woo['sha256'] == 'da189b6616c610d15a2106f93151dab81b78f83e075bcefce221ac0d00b4fa21'
        assert woo['only_for_synthetic_fixture_not_import'] is True
        assert len(woo['checked_newest_first']) >= 2
        assert all(v['compatible'] is False for v in woo['checked_newest_first'][:-1])
        assert woo['checked_newest_first'][-1]['compatible'] is True
        assert woo['checked_newest_first'][-1]['version'] == woo['version']
        assert value['subscriptions_691_limit']
    current = {}
    for rel, digest in value['command_sources'].items():
        path = (ROOT / rel).resolve()
        assert path.is_relative_to(TOOLS)
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, 'COMMAND_SOURCE_DRIFT:' + rel
        current[rel] = digest
    assert [(c['storage'], c['trap_kind']) for c in value['cases']] == [('classic', None), ('hpos', None), ('classic', 'secret'), ('classic', 'personal')]
    summaries = []
    for case in value['cases']:
        assert case['status'] == 'PASS'
        for rel, digest in case['source_manifest'].items():
            path = (ROOT / rel).resolve()
            assert path.is_relative_to(ROOT / 'wp')
            assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, 'PAYLOAD_SOURCE_DRIFT:' + rel
        assert case['new_php_lint']['exit'] == 0
        for phase in ('offline_isolation_before', 'offline_isolation_after'):
            proof = case[phase]
            assert proof['network'] == 'none' and proof['mounts'] == proof['ports'] == []
            assert proof['no_new_privileges'] is True and proof['privileged'] is False
        assert case['archive_fidelity']['all_restored_hashes_equal_source'] is True
        assert case['archive_fidelity']['retained_files_unchanged'] is True
        assert case['offline']['restored_files_before_cleanup'] == case['fixture']['source_files']
        if public69:
            metadata = case['archive_core_preflight']
            assert metadata['metadata_only'] is metadata['ok'] is True
            assert metadata['source'] == metadata['expected'] == '6.9.1'
            assert case['offline']['import_installed_or_updated_plugins'] is False
            warnings = [w for w in case['offline']['warnings'] if w['code'].startswith('PLUGIN_REQUIRES_NEWER_')]
            assert {w['code'] for w in warnings} == {'PLUGIN_REQUIRES_NEWER_WORDPRESS', 'PLUGIN_REQUIRES_NEWER_PHP'}
            assert all(w['blocking'] is False and w['plugin'] == 'plugins/a01-warning/a01-warning.php' for w in warnings)
            for rel, digest in woo['files'].items():
                assert case['fixture']['source_files']['plugins/woocommerce/' + rel] == digest
        versions = case['offline']['core_versions']
        assert versions['source'] == versions['pinned'] == versions['expected'] == value['expected_core_version']
        runtime_core = case['runtime_core_preflight']
        assert runtime_core['ok'] is True and runtime_core['code'] == 'CORE_MATCH'
        assert runtime_core['pinned'] == runtime_core['expected'] == value['expected_core_version']
        assert case['offline']['table_engines']['wp_a01_engine_probe'] == 'MYISAM'
        assert {'code': 'NON_INNODB_TABLE', 'table': 'wp_a01_engine_probe', 'engine': 'MYISAM'} in case['offline']['warnings']
        if case['trapped']:
            kind = case['trap_kind']
            expected = {'secret': 'SECRET_OU_IDENTIFIANT', 'personal': 'TABLE_PERSONNELLE_A_TRANCHER'}[kind]
            if kind == 'secret': assert case['fixture']['persistent_service_key_canary_in_archived_php'] is True
            else: assert case['fixture']['unresolved_personal_table_canary'] is True
            assert case['offline']['data_verified'] is False
            last = case['offline']['steps'][-1]
            assert last['phase'] == 'verifier' and last['exit'] == 1
            assert expected in last['report']['issues']
            assert case['publication']['status'] == 'REFUSED_OFFLINE' and case['injection'] == {}
            assert case['refusal_stop_readback']['all_three_containers_stopped'] is True
            assert case['refused_http_readback']['reachable'] is False
            assert 'verified_marker_readback' not in case
        else:
            assert case['offline']['data_verified'] is True
            assert [s['phase'] for s in case['offline']['steps']] == ['neutraliser', 'anonymiser', 'verifier']
            assert all(s['exit'] == 0 and s['report']['ok'] is True for s in case['offline']['steps'])
            publication = case['publication']; probe = publication['probe']
            assert publication['status'] == 'verified' and publication['full_staging_ready'] is True
            assert probe['ok'] is True
            for key in ('mail_blocked', 'http_blocked', 'environment_staging', 'cron_disabled',
                        'as_async_disabled', 'as_runner_disabled', 'gateways_disabled'):
                assert probe['runtime'][key] is True
            assert probe['http']['code'] == probe['assigned_url_http']['code'] == 200
            assert probe['assigned_url_http']['fiction_theme_marker'] is True
            assert probe['assigned_url_http']['redirected'] is False
            assert probe['update_filter_allow_deny'] is True and probe['constants_exact'] is True
            capacity = case['script_update_capacity']
            assert capacity['ok'] is True and capacity['policy'] == 'deployment_scripts_only'
            for key in ('file_mods_locked', 'admin_updates_denied', 'auto_updates_disabled',
                        'script_deploy_readback', 'script_replay_idempotent', 'rollback_readback',
                        'owned_probe_files_absent', 'downloaded_plugin_never_activated_or_executed',
                        'commercial_download_not_tested'):
                assert capacity[key] is True, 'CAPACITY:' + key
            assert capacity['wordpress_download_http'] == capacity['woocommerce_egress_http'] == 200
            assert capacity['wordpress_download_sha256'] == '73847b0868f335d597c77a95aaa8c18eb1656c4b646e492ed1d65752d3236427'
            if public69:
                assert probe['versions']['subscriptions'] is None
                assert probe['runtime']['subscriptions_present'] is False
                assert probe['runtime']['subscriptions_staging'] is None
                assert probe['scheduler']['tested'] is False and probe['scheduler']['reason']
                assert probe['versions']['memberships'] == '1.30.3'
                assert probe['versions']['woocommerce'] == woo['version']
                assert len(case['fixture']['orders']) == 30
                assert probe['fidelity']['orders'] == case['fixture']['orders']
                assert probe['fidelity']['membership_shortcodes'] == case['fixture']['rights']['shortcodes']
                assert probe['fidelity']['public_post_unrestricted'] is True
                assert set(probe['fidelity']['rights']) == {'active', 'expired', 'cancelled', 'paused', 'none', 'guest'}
                assert all(v is (key == 'active') for key, v in probe['fidelity']['rights'].items())
                assert all(v is (key == 'active') for key, v in probe['fidelity']['membership_shortcodes'].items())
                empty = case['injection']['empty_target_core_before_archive_injection']
                assert empty == {'version': '6.9.1', 'archive_content_absent': True}
            else:
                assert probe['runtime']['subscriptions_present'] is probe['runtime']['subscriptions_staging'] is True
                assert probe['scheduler']['tested'] is True and probe['scheduler']['callback_calls'] == 0
                assert probe['scheduler']['renewals_before'] == probe['scheduler']['renewals_after']
                assert probe['scheduler']['status'] == 'failed'
            assert probe['novamira_residuals']['plugin_present'] is False
            assert probe['novamira_residuals']['nonempty_application_password_records'] == 0
            assert probe['novamira_residuals']['created_agent_credentials_valid'] is False
            assert case['injection']['all_wp_content_hashes_equal'] is True
            assert probe['versions']['hpos'] is (case['storage'] == 'hpos')
            assert probe['versions']['wordpress'] == case['offline']['core_versions']['source']
            assert probe['fidelity']['setting_intact'] is True
            for key in ('business', 'membership', 'rules_sha256', 'plugins', 'theme'):
                assert probe['fidelity'][key] == case['fixture'][key]
            assert probe['fidelity']['rights'] == {k: v['private'] for k, v in case['fixture']['rights']['rights'].items()}
            marker = case['verified_marker_readback']
            assert marker['status'] == 'verified' and marker['site'] == case['name']
            assert marker['expected_core_version'] == value['expected_core_version']
            assert marker['update_policy'] == value['update_policy']
            assert marker['run_id'] == value['run_id'] and marker['offline_verified'] is marker['runtime_probe_passed'] is True
        summaries.append({'name': case['name'], 'storage': case['storage'], 'trapped': case['trapped'],
                          'publication': case['publication']['status'], 'status': 'PASS'})
    deleted = [c for c in value['cleanup'] if 'site' in c]
    assert len(deleted) == 4 and {c['site'] for c in deleted} == {c['name'] for c in value['cases']}
    for check in deleted:
        assert check['api_absent'] and all(check['containers_absent'].values())
        assert check['html_volume_absent'] and check['network_absent'] and check['directory_absent']
    live_receipts = []
    if live:
        import publish
        names = set()
        for path in report.parent.parent.glob('*/result.json'):
            historical = json.loads(path.read_text(encoding='utf-8'))
            for case in historical.get('cases', []):
                if 'name' in case: names.add(case['name'])
        recovery = report.parent.parent / '4fde653a20f2/cleanup-recovery.json'
        if recovery.is_file(): names.add(json.loads(recovery.read_text())['name'])
        for name in sorted(names):
            live_receipts.append(publish.deleted_readback(name))
        runner_names = {c['name'] for path in report.parent.parent.glob('*/result.json')
                        for c in json.loads(path.read_text(encoding='utf-8')).get('cleanup', []) if 'absent' in c}
        for name in sorted(runner_names):
            absent = publish.call(['inspect', name], check=False)
            assert absent.returncode != 0 and b'no such object' in absent.stderr.lower(), 'OWNED_RUNNER_RESIDUE'
        for path, digest in value['tool_source_manifest'].items():
            code = 'from pathlib import Path\nimport hashlib,json\nprint(json.dumps({"sha256":hashlib.sha256(Path(' + repr(path) + ').read_bytes()).hexdigest()}))'
            actual = json.loads(publish.call(['exec', '-i', 'staging-wp-dashboard', 'python', '-'], code.encode()).stdout)
            assert actual['sha256'] == digest, 'LIVE_TOOL_SOURCE_DRIFT'
    return {'status': 'PASS', 'recorded_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'report': str(report), 'report_sha256': hashlib.sha256(raw).hexdigest(),
            'cases_verified': len(summaries), 'cases': summaries, 'command_sources': current,
            'source_payloads_match_current_files': True, 'live_cleanup': live_receipts,
            'live_cleanup_count': len(live_receipts), 'no_agent_authentication': True,
            'shared_tool_source_hashes_match_live': live}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', required=True)
    parser.add_argument('--live-cleanup', action='store_true')
    parser.add_argument('--output')
    args = parser.parse_args()
    result = verify(pathlib.Path(args.report), args.live_cleanup)
    if args.output:
        output = pathlib.Path(args.output).resolve()
        assert output.is_relative_to(ROOT / 'production/A-01') and not output.exists()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k not in ('command_sources', 'live_cleanup')}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
