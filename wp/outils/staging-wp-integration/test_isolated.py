#!/usr/bin/env python3
"""Source-only reproduction. No Docker calls, network, installs, Git or real data.
Never run unittest discovery against the original tool: it contains live-site tests.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SOURCE_FILES = (
    'api/__init__.py', 'api/config.py', 'api/models.py', 'api/orchestrator.py',
    'api/main.py', 'api/mcp_client.py', 'api/mcp_proxy.py', 'api/site_management.py',
    'api/unlimited_extension.py', 'api/templates/templates.json',
    'api/templates/php_versions.json', 'api/templates/docker-compose.wp.yml.j2',
    'api/templates/nginx.conf.j2',
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tool-source', type=Path, required=True)
    parser.add_argument('--scratch', type=Path, required=True)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    args.scratch.mkdir(parents=True, exist_ok=True)
    isolated = Path(tempfile.mkdtemp(prefix='subscription-orchestration-', dir=args.scratch))
    before = {}
    for relative in SOURCE_FILES:
        source = args.tool_source / relative
        if source.is_symlink() or not source.is_file():
            raise SystemExit('Source whitelist incomplete or symlinked')
        payload = source.read_bytes()  # explicit source whitelist, never sites/data/plugins/logs
        before[relative] = hashlib.sha256(payload).hexdigest()
        target = isolated / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
    artifact = Path(__file__).resolve().parent
    env = {k: os.environ[k] for k in ('PATH', 'HOME') if k in os.environ}
    env.update(DB_PATH=str(isolated / 'synthetic' / 'dashboard.db'),
               SITES_DIR=str(isolated / 'synthetic' / 'sites'),
               HOST_PROJECT_DIR=str(isolated / 'synthetic'),
               PLUGINS_DIR=str(isolated / 'synthetic' / 'plugins'), NAS_HOST='staging.invalid',
               ACF_PRO_LICENSE='', NOVAMIRA_PRO_LICENSE='', PYTHONDONTWRITEBYTECODE='1')
    apply = subprocess.run([sys.executable, str(artifact / 'apply.py'), str(isolated), '--apply'],
                           capture_output=True, text=True, env=env)
    if apply.returncode:
        print(apply.stderr)
        return apply.returncode
    runner = '''import json, unittest
suite=unittest.defaultTestLoader.loadTestsFromName("api.test_subscriptions")
result=unittest.TextTestRunner(verbosity=2).run(suite)
print(json.dumps({"tests_run":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped)}))
raise SystemExit(not result.wasSuccessful())'''
    result = subprocess.run([sys.executable, '-c', runner], cwd=isolated,
                            capture_output=True, text=True, env=env)
    print(result.stderr)
    summary = json.loads(result.stdout.strip().splitlines()[-1])
    unchanged = all(hashlib.sha256((args.tool_source / p).read_bytes()).hexdigest() == digest
                    for p, digest in before.items())
    summary.update(source_files_unchanged=unchanged, real_docker_exercised=False,
                   real_wordpress_exercised=False, host_installations=False,
                   shared_restart=False, source_only_patch_applied=True)
    print(json.dumps(summary, indent=2))
    print('Isolated source copy: ' + str(isolated))
    if args.report:
        args.report.write_text(json.dumps(summary, indent=2) + '\n')
    return result.returncode if unchanged else 2


if __name__ == '__main__':
    raise SystemExit(main())
