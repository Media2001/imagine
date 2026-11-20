"""Run only staging-data synthetic fixtures and write reproducible local evidence."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=Path(__file__).with_name('results.json'))
    args = parser.parse_args()
    tests = Path(__file__).resolve().parent
    tools = tests.parents[1] / 'outils' / 'staging'
    php = os.environ['PHP_BIN']
    scratch = Path(os.environ['IMAGINE_TEST_SCRATCH']).resolve(strict=True)
    if not scratch.is_dir() or scratch == tests or tests in scratch.parents:
        raise RuntimeError('An authorized, isolated synthetic scratch directory is required')
    env = dict(os.environ)
    for key in list(env):
        if key.startswith('IMAGINE_SYNTHETIC_'):
            env.pop(key)
    cases = [
        ('data-classic-hpos-memory', [php, '-n', str(tests / 'run.php')], {}),
        ('reprise-preservation-traps-decisions', [php, '-n', str(tests / 'reprise.php')], {}),
        ('mu-quarantine', [php, '-n', str(tests / 'mu-plugin.php')], {}),
        ('mu-verified-allowlist', [php, '-n', str(tests / 'mu-plugin.php')], {'IMAGINE_SYNTHETIC_VERIFIED': 'yes'}),
        ('runtime-absent-contract', [php, '-n', str(tests / 'runtime.php')], {}),
        ('runtime-present-contract', [php, '-n', str(tests / 'runtime.php')], {'IMAGINE_SYNTHETIC_SUBSCRIPTIONS': 'yes'}),
        ('runtime-installed-class-missing-contract', [php, '-n', str(tests / 'runtime.php')], {'IMAGINE_SYNTHETIC_PACKAGE': 'yes'}),
        ('pdo-inventory-contract', [php, '-n', str(tests / 'pdo-contract.php')], {}),
        ('commands-persistent-memory', [sys.executable, str(tests / 'commands.py')], {}),
    ]
    results = []
    for name, command, extra in cases:
        result = subprocess.run(command, capture_output=True, text=True, env={**env, **extra}, timeout=180)
        assertions = sum(map(int, re.findall(r'OK (\d+) assertions', result.stdout)))
        ok = result.returncode == 0 and assertions > 0 and not result.stderr and not re.search(r'Warning:|Notice:|Fatal error:', result.stdout)
        results.append({'name': name, 'ok': ok, 'exit_code': result.returncode, 'assertions': assertions,
                        'stdout': result.stdout.strip(), 'stderr': result.stderr.strip()})
        print(f'{name}: {"PASS" if ok else "FAIL"} ({assertions} assertions)', flush=True)
    php_files = sorted([*tools.rglob('*.php'), *tests.glob('*.php')])
    lint = []
    for file in php_files:
        result = subprocess.run([php, '-n', '-l', str(file)], capture_output=True, text=True, env=env, timeout=30)
        lint.append({'file': file.relative_to(tests.parents[2]).as_posix(), 'ok': result.returncode == 0})
    files = sorted([*tools.rglob('*'), *tests.glob('*')])
    manifest = {file.relative_to(tests.parents[2]).as_posix(): hashlib.sha256(file.read_bytes()).hexdigest()
                for file in files if file.is_file() and file.suffix in {'.php', '.py', '.md'}
                and '__pycache__' not in file.parts}
    output = {'generated_utc': datetime.now(timezone.utc).isoformat(), 'synthetic_only': True,
              'ok': all(item['ok'] for item in results + lint),
              'cases': len(results), 'assertions': sum(item['assertions'] for item in results),
              'results': results, 'php_lint': lint, 'sha256': manifest,
              'limits': ['Memory store and PDO transport double; no live SQL server here.',
                         'Hook/API doubles are not proof of actual WordPress mail execution.',
                         'Real WordPress, free plugins and operator-confirmed Subscriptions/Memberships E2E belong to the peer harness.',
                         'No real archives, sites, credentials, shared services, Git or deployments used.']}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({key: output[key] for key in ('ok', 'cases', 'assertions')}))
    return 0 if output['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
