"""Transport Docker local : aucun pull/build ni bootstrap WordPress importé."""
import json
import os
import re
import secrets
import subprocess

from . import config

IMAGE_RE = re.compile(r'^sha256:[a-f0-9]{64}$')


class Engine:
    def _execute(self, cmd, *, request=None, timeout=900):
        from .subscriptions import QuarantineError
        try:
            result = subprocess.run(cmd, input=json.dumps(request) if request is not None else None,
                                    capture_output=True, text=True, timeout=timeout,
                                    env={k: os.environ[k] for k in ('PATH', 'HOME', 'DOCKER_HOST',
                                         'DOCKER_CONTEXT', 'DOCKER_CONFIG') if k in os.environ})
        except (OSError, subprocess.TimeoutExpired):
            raise QuarantineError('Commande hors-ligne indisponible ou délai dépassé') from None
        if result.returncode:
            raise QuarantineError('Étape hors-ligne échouée ; copie maintenue en quarantaine')
        return result.stdout

    def local_image(self, value):
        from .subscriptions import QuarantineError
        if not IMAGE_RE.fullmatch(value):
            raise QuarantineError('Image locale épinglée par identifiant sha256 requise')
        actual = self._execute(['docker', 'image', 'inspect', '--format', '{{.Id}}', value], timeout=30)
        if actual.strip() != value:
            raise QuarantineError('Image locale non vérifiée ; aucun téléchargement autorisé')

    def compose(self, path, *args):
        self._execute(['docker', 'compose', '-f', str(path), '-p',
                       'site-' + path.parent.name, *args])

    def worker(self, image, mounts, executable, request):
        from .subscriptions import QuarantineError
        cidfile = config.SITES_DIR / request['slug'] / ('worker-' + secrets.token_hex(8) + '.cid')
        cmd = ['docker', 'run', '--rm', '-i', '--pull=never', '--network=none',
               '--read-only', '--cap-drop=ALL', '--security-opt=no-new-privileges',
               '--pids-limit=128', '--memory=1g', '--cpus=2', '--user=33:33',
               '--cidfile', str(cidfile), '--tmpfs', '/tmp:rw,noexec,nosuid,size=64m',
               '--entrypoint', executable]
        for source, target, readonly in mounts:
            if any(c in str(source) for c in (',', '\n', '\r')):
                raise QuarantineError('Chemin de montage invalide')
            cmd += ['--mount', f'type=bind,src={source},dst={target}' + (',readonly' if readonly else '')]
        cmd += [image, '--request-stdin']
        try:
            output = self._execute(cmd, request=request)
            if len(output) > 16384:
                raise QuarantineError('Rapport hors-ligne trop volumineux')
            report = json.loads(output)
            if not isinstance(report, dict):
                raise ValueError()
            return report
        except (ValueError, TypeError):
            raise QuarantineError('Rapport hors-ligne invalide') from None
        finally:
            if cidfile.exists():
                cid = cidfile.read_text().strip()
                if re.fullmatch(r'[a-f0-9]{64}', cid):
                    # Docker run timeouts do not stop their container. Stop only its CID.
                    try:
                        self._execute(['docker', 'stop', '--time', '5', cid], timeout=15)
                    except QuarantineError:
                        pass


def documents(site, image, db_image, nginx_image, host):
    db = {'image': db_image, 'pull_policy': 'never', 'container_name': 'db-' + site['slug'],
          'network_mode': 'none', 'restart': 'no',
          'command': ['--skip-networking', '--socket=/run/mysqld/mysqld.sock'],
          'environment': {'MARIADB_DATABASE': 'wordpress', 'MARIADB_USER': 'wp',
                          'MARIADB_PASSWORD': site['db_password'],
                          'MARIADB_ROOT_PASSWORD': site['db_root_password']},
          'volumes': [str(host / 'db') + ':/var/lib/mysql',
                      str(host / 'mysql-socket') + ':/run/mysqld'],
          'healthcheck': {'test': ['CMD', 'healthcheck.sh', '--connect', '--innodb_initialized'],
                          'interval': '2s', 'timeout': '3s', 'retries': 60}}
    offline = {'services': {'db': db}}
    runtime = {'services': {'db': db,
               'wp': {'image': image, 'pull_policy': 'never', 'container_name': 'wp-' + site['slug'],
                      'network_mode': 'none', 'restart': 'no', 'read_only': True, 'user': '33:33',
                      'cap_drop': ['ALL'], 'security_opt': ['no-new-privileges:true'],
                      'entrypoint': ['/opt/staging/serve'],
                      'volumes': [str(host / 'html') + ':/var/www/html',
                                  str(host / 'mysql-socket') + ':/run/mysqld',
                                  str(host / 'fpm-socket') + ':/run/staging-fpm'],
                      'tmpfs': ['/tmp:rw,noexec,nosuid,size=64m']},
               'nginx': {'image': nginx_image, 'pull_policy': 'never',
                         'container_name': 'nginx-' + site['slug'], 'restart': 'no',
                         'ports': [f"{site['port']}:80"],
                         'volumes': [str(host / 'html') + ':/var/www/html:ro',
                                     str(host / 'fpm-socket') + ':/run/staging-fpm:ro',
                                     str(host / 'subscription-nginx.conf') + ':/etc/nginx/conf.d/default.conf:ro'],
                         'networks': ['verified-web']}},
               'networks': {'verified-web': {'internal': True}}}
    return offline, runtime
