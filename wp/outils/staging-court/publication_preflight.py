"""Read-only A-01 publication diagnosis; no lifecycle, archive or secret I/O.

Inspect deployed source and boolean prerequisites without importing API modules.
A changed contract requires review, never implicit publication permission.
"""
import argparse
import ast
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
EXPECTED_FIELDS = {'name', 'template_slug', 'php_version', 'client_name', 'target_domain'}


def calls(source):
    try:
        return {n.func.id for n in ast.walk(ast.parse(source))
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    except SyntaxError:
        return set()


def assess(snapshot):
    functions = snapshot.get('functions', {})
    provision = functions.get('_provision_site', '')
    create_calls = calls(functions.get('create_site', ''))
    provision_calls = calls(provision)
    mcp_calls = calls(functions.get('provision_mcp', ''))
    issues = []
    mandatory_template = ('get_template' in create_calls
                          and 'template_slug' in snapshot.get('create_required', []))
    platform_added = ('_MCP_PLATFORM_ZIPS' in provision
                      and set(snapshot.get('platform_zips', [])) == {'novamira.zip', 'novamira-pro.zip'})
    license_risk = (mandatory_template and platform_added
                    and 'activate_novamira_pro_license' in provision_calls
                    and 'config.NOVAMIRA_PRO_LICENSE' in provision
                    and snapshot.get('novamira_license_configured') is True
                    and snapshot.get('novamira_zip_present') is True
                    and snapshot.get('novamira_pro_zip_present') is True)
    if license_risk:
        issues.append('NORMAL_CREATE_ACTIVATES_CONFIGURED_NOVAMIRA_LICENSE')
    if (mandatory_template and 'provision_mcp' in provision_calls
            and {'enable_novamira_abilities', 'create_mcp_credentials', 'validate_mcp_connection'} <= mcp_calls):
        issues.append('NORMAL_CREATE_PROVISIONS_NOVAMIRA_MCP')
    if mandatory_template and set(snapshot.get('create_fields', [])) == EXPECTED_FIELDS:
        issues.append('CREATE_API_HAS_NO_EMPTY_WITHOUT_MCP_BYPASS')
    return {'status': 'BLOCKED' if license_risk else 'REVIEW_REQUIRED', 'issues': issues,
            'full_staging_ready': False, 'publication_executed': False,
            'system_egress_after_verification_required': False,
            'accepted_post_verification_policy': 'WP_HTTP_BLOCK_EXTERNAL=true; '
                'WP_ACCESSIBLE_HOSTS=*.wordpress.org,*.woocommerce.com; unchanged safety MU filter',
            'minimum_seam_for_Ced': 'Normal API option for a genuinely empty site: '
                'skip platform premium ZIPs, configured license activation and MCP provisioning; '
                'must not change defaults for other sites. Not implemented or authorized here.'}


# Runs in the EXISTING dashboard container. No API import, .env read, package
# contents or environment value dump. Source code contains variable names only.
LIVE_SOURCE_PROBE = r'''
import ast, hashlib, json, os
from pathlib import Path
root = Path('/app/api')
p = root / 'orchestrator.py'
text = p.read_text()
tree = ast.parse(text)
names = {'create_site', '_provision_site', 'activate_novamira_pro_license', 'provision_mcp'}
functions = {n.name: ast.get_source_segment(text, n) for n in tree.body
             if isinstance(n, ast.FunctionDef) and n.name in names}
locations = {n.name: {'file': str(p), 'start': n.lineno, 'end': n.end_lineno}
             for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names}
zips = None
for n in tree.body:
    if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == '_MCP_PLATFORM_ZIPS' for t in n.targets):
        zips = list(ast.literal_eval(n.value))
files = ['orchestrator.py', 'main.py', 'models.py', 'templates/docker-compose.wp.yml.j2', 'templates/templates.json']
manifest = {str(root / f): hashlib.sha256((root / f).read_bytes()).hexdigest() for f in files}
plugins = Path(os.getenv('PLUGINS_DIR', '/app/plugins'))
print(json.dumps({'functions': functions, 'locations': locations, 'platform_zips': zips,
                  'tool_source_manifest': manifest,
                  'novamira_license_configured': bool(os.environ.get('NOVAMIRA_PRO_LICENSE')),
                  'novamira_zip_present': (plugins / 'novamira.zip').is_file(),
                  'novamira_pro_zip_present': (plugins / 'novamira-pro.zip').is_file()}))
'''


def collect():
    prefix = ['wsl.exe', '-d', 'Ubuntu', '--'] if os.name == 'nt' else []
    def metadata(path):
        code = ('import urllib.request,sys; '
                'sys.stdout.buffer.write(urllib.request.urlopen(sys.argv[1],timeout=20).read())')
        p = subprocess.run(prefix + ['python3', '-c', code, 'http://127.0.0.1:7000' + path],
                           capture_output=True, check=True, timeout=30)
        return json.loads(p.stdout)
    spec = metadata('/openapi.json')
    schema = spec['components']['schemas']['CreateSiteRequest']
    metadata('/api/health')
    templates = metadata('/api/templates')
    p = subprocess.run(prefix + ['docker', 'exec', 'staging-wp-dashboard', 'python', '-c', LIVE_SOURCE_PROBE],
                       capture_output=True, check=True, timeout=30)
    snapshot = json.loads(p.stdout)
    snapshot['create_fields'] = sorted(schema['properties'])
    snapshot['create_required'] = schema['required']
    snapshot['minimal_template'] = next(t for t in templates['templates'] if t['slug'] == 'sandbox-wp-minimal')
    p = subprocess.run(prefix + ['docker', 'version', '--format', '{{.Server.Version}}'],
                       capture_output=True, check=True, timeout=30)
    snapshot['docker_server_version'] = p.stdout.decode().strip()
    return snapshot


def main():
    parser = argparse.ArgumentParser(description='Diagnostic A-01 en lecture seule, sans import ni création.')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    output = Path(args.output).resolve()
    if not output.is_relative_to((ROOT / 'production/A-01').resolve()) or output.exists():
        parser.error('Nouveau reçu uniquement sous production/A-01; aucun écrasement.')
    start = datetime.datetime.now(datetime.timezone.utc)
    try:
        snapshot = collect()
        result = assess(snapshot)
        result['observations'] = snapshot
        again = collect()
        result['tool_sources_unchanged_during_probe'] = (snapshot['tool_source_manifest'] == again['tool_source_manifest'])
        if not result['tool_sources_unchanged_during_probe']:
            result.update(status='REVIEW_REQUIRED', issues=['DASHBOARD_SOURCE_DRIFT'])
    except Exception as exc:
        result = {'status': 'BLOCKED', 'issues': ['READ_ONLY_DIAGNOSIS_FAILED'],
                  'error_class': type(exc).__name__, 'full_staging_ready': False}
    result.update(recorded_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  started_utc=start.isoformat(), created_sites=[], lifecycle_mutations=0,
                  archives_read=0, shared_tool_modified=False, pret=False)
    paths = [Path(__file__), ROOT / 'wp/tests/a01-court/test_publication_preflight.py']
    result['diagnostic_sources'] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': result['status'], 'report': str(output), 'full_staging_ready': False}))
    return 78


if __name__ == '__main__':
    raise SystemExit(main())
