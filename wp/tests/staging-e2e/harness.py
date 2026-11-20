#!/usr/bin/env python
"""Disposable, offline WordPress/Woo acceptance harness; Python stdlib only."""
import argparse
import datetime
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import urllib.request
import uuid

ROOT = pathlib.Path(__file__).resolve().parent
LABEL = 'org.imagine.synthetic-e2e'
ARTIFACTS = {
    'wordpress.zip': 'https://wordpress.org/wordpress-6.9.zip',
    'woocommerce.zip': 'https://downloads.wordpress.org/plugin/woocommerce.10.4.3.zip',
    'wp-cli.phar': 'https://github.com/wp-cli/wp-cli/releases/download/v2.12.0/wp-cli-2.12.0.phar',
    'contact-form-7.zip': 'https://downloads.wordpress.org/plugin/contact-form-7.6.1.4.zip',
    'wordpress-seo.zip': 'https://downloads.wordpress.org/plugin/wordpress-seo.26.5.zip',
    'meta-box.zip': 'https://downloads.wordpress.org/plugin/meta-box.5.10.7.zip',
}
LOCK = ROOT / 'dependencies.lock.json'
SUBJECT_FILES = ('neutraliser', 'anonymiser', 'verifier', 'command.php', 'lib.php', 'schema.php',
                 'files.php', 'pdo-store.php', 'runtime-probe.php', 'mu-plugins/000-imagine-staging-safety.php')
EXECUTION_FILES = ('harness.py', 'inside.py', 'fixture.php', 'snapshot.php', 'oracle.php', 'mutate.php',
                   'db-probe.php', 'mail-probe.php', 'worker-bridge.php', 'subject-preflight.php',
                   'subject-adapter.json', 'public-dependencies.json', 'Dockerfile', 'fidelity.php', 'fidelity-mu.php')


class SafetyError(RuntimeError):
    pass


def wsl_path(value):
    value = str(value).replace('\\', '/')
    if re.match(r'^[A-Za-z]:/', value):
        return '/mnt/' + value[0].lower() + value[2:]
    return value


def validate_inspection(info):
    host = info.get('HostConfig', {})
    config = info.get('Config', {})
    name = info.get('Name', '').lstrip('/')
    if not re.fullmatch(r'imagine-staging-e2e-[a-f0-9]{12}', name):
        raise SafetyError('Container name is not explicitly synthetic/disposable')
    if config.get('Labels', {}).get(LABEL) != 'true':
        raise SafetyError('Missing synthetic ownership label')
    if host.get('NetworkMode') != 'none':
        raise SafetyError('Network must be none before any import')
    if host.get('Privileged'):
        raise SafetyError('Privileged container forbidden')
    if info.get('Mounts') or host.get('Binds'):
        raise SafetyError('All host mounts and Docker volumes are forbidden')
    if host.get('PortBindings') or config.get('ExposedPorts'):
        raise SafetyError('All published or declared ports are forbidden')
    if info.get('NetworkSettings', {}).get('Ports'):
        raise SafetyError('Network ports are forbidden')
    networks = info.get('NetworkSettings', {}).get('Networks', {})
    if set(networks) - {'none'}:
        raise SafetyError('Secondary network attachment forbidden')
    if 'ALL' not in host.get('CapDrop', []):
        raise SafetyError('All Linux capabilities must be dropped')
    if not any(v.startswith('no-new-privileges') for v in host.get('SecurityOpt', [])):
        raise SafetyError('no-new-privileges is mandatory')


def validate_result(result, mode):
    if result.get('mode') != mode or result.get('exit_code') != 0:
        raise SafetyError('Inner result does not confirm this exact successful run mode')
    checks = result.get('checks')
    if not isinstance(checks, list) or not checks or not any(c.get('status') == 'PASS' for c in checks):
        raise SafetyError('No executed assertions in inner receipt')
    if any(c.get('status') not in ('PASS', 'NOT_TESTED') for c in checks):
        raise SafetyError('Inner receipt contains failure, blocked or unknown status')
    if mode == 'acceptance':
        passed = {c.get('check') for c in checks if c.get('status') == 'PASS'}
        required = {storage + ':' + stage for storage in ('classic', 'hpos')
                    for stage in ('subject_positive:neutraliser', 'subject_positive:anonymiser',
                                  'subject_positive:verifier', 'post_clean_fidelity',
                                  'preserved_business_fields', 'rerun:verifier')}
        if not required <= passed:
            raise SafetyError('Acceptance is incomplete: both stores and post-clean fidelity are mandatory')


class Harness:
    def __init__(self):
        self.use_wsl = False
        if shutil.which('docker'):
            self.docker = ['docker']
        elif os.name == 'nt' and shutil.which('wsl.exe'):
            self.docker = ['wsl.exe', '-d', 'Ubuntu', '--', 'docker']
            self.use_wsl = True
        else:
            raise SafetyError('DEPENDENCY_NOT_READY: existing Docker engine/CLI required; no host install attempted')
        self.checks = []
        self.run_id = uuid.uuid4().hex[:12]
        self.container = None
        self.container_created = False
        self.evidence = ROOT / 'evidence' / self.run_id
        self.evidence.mkdir(parents=True, exist_ok=False)

    def call(self, args, *, timeout=900, check=True, input_text=None):
        proc = subprocess.run(self.docker + args, input=input_text,
                              capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=timeout)
        if check and proc.returncode:
            raise SafetyError(f'Docker {args[0]} failed ({proc.returncode}): {proc.stderr[-4000:]}')
        return proc

    def local_path(self, path):
        return wsl_path(path) if self.use_wsl else str(path)

    def record(self, name, status, detail):
        entry = {'check': name, 'status': status, 'detail': detail}
        self.checks.append(entry)
        print(json.dumps(entry, ensure_ascii=False), flush=True)

    def write_journal(self):
        result = {'suite': 'synthetic-staging-e2e', 'run_id': self.run_id,
                  'recorded_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  'checks': self.checks}
        (self.evidence / 'journal.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    def prepare(self):
        self.call(['version', '--format', '{{.Server.Version}}'], timeout=30)
        public = ROOT / 'public'
        public.mkdir(exist_ok=True)
        pinned = json.loads((ROOT / 'public-dependencies.json').read_text(encoding='utf-8'))
        if {name: value['url'] for name, value in pinned['artifacts'].items()} != ARTIFACTS:
            raise SafetyError('Only the explicitly allowlisted public artifact URLs are allowed')
        artifacts = {}
        for name, url in ARTIFACTS.items():
            target = public / name
            if not target.exists():
                partial = target.with_suffix(target.suffix + '.partial')
                try:
                    request = urllib.request.Request(url, headers={'User-Agent': 'Imagine-Synthetic-E2E/1.0'})
                    with urllib.request.urlopen(request, timeout=120) as response, partial.open('wb') as out:
                        shutil.copyfileobj(response, out)
                    partial.replace(target)
                finally:
                    partial.unlink(missing_ok=True)
            digest = hashlib.sha256(target.read_bytes()).hexdigest()
            expected = pinned['artifacts'][name]['sha256']
            if digest != expected or target.stat().st_size != pinned['artifacts'][name]['bytes']:
                raise SafetyError('Public dependency checksum/size mismatch: ' + name)
            artifacts[name] = {'url': url, 'sha256': digest, 'bytes': target.stat().st_size}
        (public / 'SHA256SUMS').write_text(''.join(v['sha256'] + '  ' + k + '\n' for k, v in artifacts.items()), encoding='ascii')
        base = pinned['base_image']
        if not re.fullmatch(r'debian@sha256:[a-f0-9]{64}', base):
            raise SafetyError('The public base image must be explicitly pinned by digest')
        self.call(['pull', base], timeout=600)
        base_info = json.loads(self.call(['image', 'inspect', base]).stdout)[0]
        base_digest = base_info['RepoDigests'][0]
        image_tag = 'imagine-staging-e2e-public:' + self.run_id
        build = self.call(['build', '--build-arg', 'BASE_IMAGE=' + base_digest,
                           '--label', LABEL + '=true', '-t', image_tag,
                           '-f', self.local_path(ROOT / 'Dockerfile'), self.local_path(ROOT)], timeout=1800, check=False)
        (self.evidence / 'public-build.log').write_text(build.stdout + build.stderr, encoding='utf-8')
        if build.returncode:
            raise SafetyError('DEPENDENCY_NOT_READY: public image build failed; see public-build.log')
        image = json.loads(self.call(['image', 'inspect', image_tag]).stdout)[0]
        lock = {'base_image': base_digest, 'image_id': image['Id'], 'image_tag': image_tag,
                'artifacts': artifacts, 'notice': 'Public dependencies only. No site or import was started during prepare.'}
        LOCK.write_text(json.dumps(lock, indent=2) + '\n', encoding='utf-8')
        self.record('public_dependencies', 'PASS', {'image_tag': image_tag, 'image_id': image['Id'], 'artifacts': artifacts})

    def run(self, mode, subject_dir=None):
        if not LOCK.exists():
            raise SafetyError('DEPENDENCY_NOT_READY: run prepare first; run never pulls or downloads')
        lock = json.loads(LOCK.read_text(encoding='utf-8'))
        image = json.loads(self.call(['image', 'inspect', lock['image_id']], timeout=30).stdout)[0]
        if image.get('Config', {}).get('Labels', {}).get(LABEL) != 'true':
            raise SafetyError('Image ownership label mismatch')
        if image.get('Config', {}).get('Volumes') or image.get('Config', {}).get('ExposedPorts'):
            raise SafetyError('Image must declare neither VOLUME nor EXPOSE')
        expected_subject = (ROOT.parent.parent / 'outils' / 'staging').resolve()
        subject = pathlib.Path(subject_dir).resolve() if subject_dir else expected_subject
        if subject != expected_subject:
            raise SafetyError('Only this repository staging source is allowed; arbitrary site/archive paths forbidden')
        if mode == 'acceptance' and not all((subject / name).is_file() and not (subject / name).is_symlink() for name in SUBJECT_FILES):
            raise SafetyError('DEPENDENCY_NOT_READY: named staging source files not all available; fixture selftest is separate')
        source_manifest = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in EXECUTION_FILES}
        (self.evidence / 'harness-source.json').write_text(json.dumps(source_manifest, indent=2) + '\n', encoding='utf-8')
        self.container = 'imagine-staging-e2e-' + self.run_id
        self.call(['create', '--name', self.container, '--label', LABEL + '=true',
                   '--network', 'none', '--no-healthcheck', '--cap-drop', 'ALL',
                   '--security-opt', 'no-new-privileges', '--pids-limit', '256',
                   '--memory', '1536m', '--cpus', '2', '--log-driver', 'none',
                   '--pull', 'never', lock['image_id'], 'sleep', 'infinity'])
        self.container_created = True
        inspect = json.loads(self.call(['inspect', self.container]).stdout)[0]
        validate_inspection(inspect)
        self.record('isolation_before_import', 'PASS', {
            'container': self.container, 'network': 'none', 'ports': [], 'mounts': [],
            'cap_drop': inspect['HostConfig']['CapDrop'], 'image_id': image['Id']})
        for name in ('inside.py', 'fixture.php', 'snapshot.php', 'oracle.php', 'mutate.php', 'db-probe.php', 'mail-probe.php', 'worker-bridge.php', 'subject-preflight.php', 'fidelity.php', 'fidelity-mu.php'):
            self.call(['cp', self.local_path(ROOT / name), self.container + ':/opt/e2e/' + name])
        if (ROOT / 'subject-adapter.json').exists():
            self.call(['cp', self.local_path(ROOT / 'subject-adapter.json'), self.container + ':/opt/e2e/subject-adapter.json'])
        if mode == 'acceptance':
            # Explicit source allowlist only: no recursive site/archive copy, no mounts.
            stage = self.evidence / 'subject-source'
            stage.mkdir()
            manifest = {}
            for name in SUBJECT_FILES:
                original = subject / name
                destination = stage / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                before_hash = hashlib.sha256(original.read_bytes()).hexdigest()
                shutil.copy2(original, destination)
                copied_hash = hashlib.sha256(destination.read_bytes()).hexdigest()
                if before_hash != copied_hash or hashlib.sha256(original.read_bytes()).hexdigest() != copied_hash:
                    raise SafetyError('Subject source changed while copied; refuse an inconsistent test')
                manifest[name] = copied_hash
            (self.evidence / 'subject-source.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
            self.call(['cp', self.local_path(stage), self.container + ':/subject'])
        current_manifest = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in EXECUTION_FILES}
        if current_manifest != source_manifest:
            raise SafetyError('Harness source changed while copying; no import started')
        self.call(['start', self.container])
        result = self.call(['exec', self.container, 'python3', '/opt/e2e/inside.py', mode], timeout=1800, check=False)
        (self.evidence / 'execution.log').write_text(result.stdout + result.stderr, encoding='utf-8')
        print(result.stdout, end='')
        if result.stderr:
            print(result.stderr, file=sys.stderr, end='')
        self.call(['cp', self.container + ':/report/result.json', self.local_path(self.evidence / 'result.json')], check=False)
        self.call(['cp', self.container + ':/opt/public/packages.tsv', self.local_path(self.evidence / 'packages.tsv')], check=False)
        final_inspect = json.loads(self.call(['inspect', self.container]).stdout)[0]
        validate_inspection(final_inspect)
        self.record('isolation_after_execution', 'PASS', {'network': 'none', 'ports': [], 'mounts': []})
        if result.returncode:
            raise SafetyError(f'{mode} failed with exit code {result.returncode}; see execution.log/result.json; no success claim')
        result_file = self.evidence / 'result.json'
        if not result_file.is_file():
            raise SafetyError('Missing read-back receipt from the exact disposable container')
        validate_result(json.loads(result_file.read_text(encoding='utf-8')), mode)
        self.record(mode, 'PASS', 'See result.json for actual assertions; paid extensions are not installed or simulated as validated')

    def cleanup(self):
        if self.container and self.container_created:
            info = self.call(['inspect', self.container], check=False, timeout=30)
            if info.returncode == 0:
                validate_inspection(json.loads(info.stdout)[0])
                self.call(['rm', '-f', self.container], timeout=60)
                gone = self.call(['inspect', self.container], check=False, timeout=30)
                if gone.returncode == 0:
                    raise SafetyError('Disposable container still present after cleanup')
                self.record('container_cleanup', 'PASS', {'container': self.container, 'absent_after_removal': True})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('prepare', 'fixture-selftest', 'acceptance'))
    parser.add_argument('--subject-dir', help='Directory with the three existing subject launchers; copied read-only from the host point of view')
    args = parser.parse_args()
    harness = None
    status = 0
    try:
        harness = Harness()
        if args.mode == 'prepare':
            harness.prepare()
        else:
            harness.run(args.mode, args.subject_dir)
    except (SafetyError, subprocess.SubprocessError, OSError, ValueError) as exc:
        status = 2
        if harness:
            harness.record(args.mode, 'BLOCKED' if 'DEPENDENCY_NOT_READY' in str(exc) else 'FAIL', str(exc))
        else:
            print(str(exc), file=sys.stderr)
    finally:
        if harness:
            try:
                harness.cleanup()
            except Exception as exc:
                harness.record('cleanup', 'FAIL', str(exc))
                status = 2
            harness.write_journal()
    return status


if __name__ == '__main__':
    sys.exit(main())
