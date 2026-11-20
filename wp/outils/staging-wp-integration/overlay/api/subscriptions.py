"""Offline subscription import. No imported PHP is bootstrapped by this module."""
from __future__ import annotations

import json
import os
import re
import secrets
from pathlib import Path
from urllib.parse import urlsplit

from . import config, models

PROFILE = 'subscriptions'
PROTOCOL = 'staging-offline-v1'


class QuarantineError(ValueError):
    """Fixed, non-sensitive failure safe to expose to the dashboard."""


def require_verified(site: dict | None) -> None:
    if site and site.get('profile') == PROFILE and site.get('verification_state') != 'verified':
        raise QuarantineError('Copie non vérifiée : accès web/agent et opérations historiques interdits')


def guard_slug(slug: str) -> None:
    require_verified(models.get_site(slug))


SCRIPTS = {
    'neutraliser': 'wp/outils/staging/neutraliser',
    'anonymiser': 'wp/outils/staging/anonymiser',
    'verifier': 'wp/outils/staging/verifier',
    'bascule': 'wp/outils/bascule/lancer',
}
REQUIRED_CHECKS = ('emails', 'service_keys', 'payment_ids', 'mail_blocked',
                   'subscriptions_staging', 'unknown_tables_resolved',
                   'production_refused', 'imported_code_not_loaded')
from .subscription_runtime import Engine, IMAGE_RE, documents


def is_subscription(site):
    return bool(site and site.get('profile') == PROFILE)


def _private_json(path, payload):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as handle:
        json.dump(payload, handle)


def _valid_report(report, stage):
    if (report.get('protocol') != PROTOCOL or report.get('stage') != stage
            or report.get('ok') is not True):
        raise QuarantineError('Rapport non conforme ; copie maintenue en quarantaine')
    if stage == 'verifier':
        checks = report.get('checks')
        if not isinstance(checks, dict) or any(checks.get(k) is not True for k in REQUIRED_CHECKS):
            raise QuarantineError('Vérification incomplète ; copie maintenue en quarantaine')
        version = report.get('wordpress_version', '')
        if not isinstance(version, str) or not re.fullmatch(r'\d+\.\d+(?:\.\d+)?', version):
            raise QuarantineError('Version WordPress non vérifiée')
        if tuple(map(int, version.split('.')[:2])) < (6, 9):
            raise QuarantineError('WordPress inférieur à 6.9 : Novamira et publication refusés')
    if stage == 'novamira' and (report.get('fresh') is not True or report.get('active') is not True):
        raise QuarantineError('Installation neuve et activation Novamira non vérifiées')


def safe_diagnostics(report):
    """Metadata only: never forward arbitrary nesting, row values or messages."""
    out = {}
    for key in ('issues', 'warnings'):
        values = report.get(key, [])
        out[key] = [v for v in values[:200] if isinstance(v, str) and re.fullmatch(r'[A-Z_]{1,100}', v)] if isinstance(values, list) else []
    tables = report.get('unknown_tables', [])
    out['unknown_tables'] = []
    for table in tables[:200] if isinstance(tables, list) else []:
        if not isinstance(table, dict) or not re.fullmatch(r'[A-Za-z0-9_]{1,128}', table.get('name', '')):
            continue
        columns = table.get('columns', [])
        if not isinstance(columns, list) or any(not isinstance(c, str) or not re.fullmatch(r'[A-Za-z0-9_]{1,128}', c) for c in columns):
            continue
        rows = table.get('rows')
        if type(rows) is not int or rows < 0:
            continue
        personal = table.get('personal_columns', [])
        safe = dict(name=table['name'], columns=columns, rows=rows,
                    personal_columns=[c for c in personal if c in columns] if isinstance(personal, list) else [])
        decision = table.get('decision')
        if isinstance(decision, dict) and decision.get('action') in ('garder', 'vider', 'anonymiser'):
            safe['decision'] = dict(action=decision['action'])
            if isinstance(decision.get('columns'), list):
                safe['decision']['columns'] = [c for c in decision['columns'] if c in columns]
        out['unknown_tables'].append(safe)
    for key in ('unknown_post_types', 'disabled_plugins'):
        values = report.get(key, [])
        out[key] = [v for v in values[:500] if isinstance(v, str) and re.fullmatch(r'[A-Za-z0-9_./-]{1,200}', v)] if isinstance(values, list) else []
    return out


def create_offline(*, name, archive, workflow, production_url, staging_url, port,
                   worker_image, db_image, nginx_image, admin_password, engine=None, table_decisions=None):
    from . import orchestrator
    engine = engine or Engine()
    table_decisions = {} if table_decisions is None else table_decisions
    if not isinstance(table_decisions, dict) or len(json.dumps(table_decisions)) > 4096:
        raise QuarantineError('Fichier de décisions invalide ou trop volumineux')
    # Only metadata: the archive is never opened by the orchestrator.
    archive, workflow = Path(archive).resolve(), Path(workflow).resolve()
    if not archive.is_file() or not workflow.is_dir():
        raise QuarantineError('Archive ou dépôt de scripts manquant')
    for relative in SCRIPTS.values():
        item = workflow / relative
        if not item.is_file() or item.resolve() != item:
            raise QuarantineError('Script approuvé manquant ou lien symbolique interdit')
    prod, target = urlsplit(production_url), urlsplit(staging_url)
    if (prod.scheme not in ('http', 'https') or target.scheme not in ('http', 'https')
            or not prod.hostname or not target.hostname or prod.hostname == target.hostname
            or prod.username or prod.password or target.username or target.password):
        raise QuarantineError('Adresses production/staging distinctes requises, sans identifiants')
    if staging_url.rstrip('/') != f'http://{config.NAS_HOST}:{port}':
        raise QuarantineError('Adresse staging différente du point web configuré dans le tableau de bord')
    if not isinstance(port, int) or not 1024 <= port <= 65535 or port in models.used_ports():
        raise QuarantineError('Port opérateur indisponible ou invalide')
    if not admin_password or '\n' in admin_password:
        raise QuarantineError('Mot de passe administrateur de test requis sur entrée privée')
    for image in (worker_image, db_image, nginx_image):
        if not IMAGE_RE.fullmatch(image):
            raise QuarantineError('Image locale épinglée par identifiant sha256 requise')
        engine.local_image(image)
    slug = orchestrator.slugify(name)
    if models.get_site(slug):
        raise QuarantineError('Identifiant déjà utilisé : copie fraîche obligatoire')
    config.SITES_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    root = config.SITES_DIR / slug
    root.mkdir(mode=0o700, parents=False, exist_ok=False)
    for folder in ('html', 'db', 'mysql-socket', 'fpm-socket'):
        (root / folder).mkdir(mode=0o777)
        os.chmod(root / folder, 0o777)
    site = dict(slug=slug, name=name, profile=PROFILE, template_slug=None,
                client_name=None, target_domain=None, port=port, php_version='8.3',
                status='importing', notes='', wp_admin_user='imagine-test-admin', wp_admin_password='',
                db_password=secrets.token_urlsafe(24), db_root_password=secrets.token_urlsafe(32),
                created_at=models.now_iso())
    models.insert_site(site)
    models.set_verification(slug, 'quarantined')
    host = config.HOST_SITES_DIR / slug
    offline, runtime = documents(site, worker_image, db_image, nginx_image, host)
    _private_json(root / 'offline-compose.json', offline)
    request = dict(protocol=PROTOCOL, slug=slug, production_url=production_url,
                   production_hosts=[prod.hostname],
                   table_decisions=table_decisions,
                   staging_url=staging_url, environment='staging', wordpress_path='/var/www/html',
                   database={'host': 'localhost', 'socket': '/run/mysqld/mysqld.sock',
                             'name': 'wordpress_staging', 'user': 'wp', 'password': site['db_password']},
                   admin={'login': 'imagine-test-admin', 'password': admin_password},
                   archive='/input/source.wpress')
    base_mounts = [(host / 'html', '/var/www/html', False),
                   (host / 'mysql-socket', '/run/mysqld', False),
                   (workflow / 'wp/outils/staging', '/workflow/wp/outils/staging', True),
                   (workflow / 'wp/outils/bascule', '/workflow/wp/outils/bascule', True)]
    imported = False
    stage = 'database'
    report = {}
    try:
        engine.compose(root / 'offline-compose.json', 'up', '-d', '--wait', '--pull', 'never', 'db')
        for index, stage in enumerate(('importer', 'neutraliser', 'anonymiser', 'verifier',
                                       'bascule', 'verifier', 'novamira', 'verifier')):
            # Native PHP launchers take --worker-bridge, not --request-stdin.
            # The image-owned adapter translates stdin JSON without bootstrapping the copy.
            executable = '/opt/staging/' + stage
            mounts = base_mounts + ([(archive, '/input/source.wpress', True)] if stage == 'importer' else [])
            stage_request = dict(request, stage=stage)
            if stage != 'anonymiser':
                stage_request.pop('admin', None)
            report = engine.worker(worker_image, mounts, executable, stage_request)
            _valid_report(report, stage)
            safe = dict(protocol=PROTOCOL, stage=stage, ok=True)
            if stage == 'verifier':
                safe.update(wordpress_version=report['wordpress_version'],
                            checks={k: True for k in REQUIRED_CHECKS})
                safe.update(safe_diagnostics(report))
            if stage == 'novamira':
                safe.update(fresh=True, active=True)
            _private_json(root / f'report-{index:02d}-{stage}.json', safe)
            if stage == 'importer':
                imported = True
                models.set_verification(slug, 'imported')
                models.update_status(slug, 'imported')
        (root / 'subscription-nginx.conf').write_text(
            'server { listen 80; root /var/www/html; index index.php;\n'
            'location / { try_files $uri $uri/ /index.php?$args; }\n'
            'location ~ \\.php$ { try_files $uri =404; include fastcgi_params; '
            'fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name; '
            'fastcgi_pass unix:/run/staging-fpm/php.sock; }\n'
            'location ~ /\\. { deny all; } }\n')
        _private_json(root / 'verified-compose.json', runtime)
        models.set_verification(slug, 'verified')
        models.update_status(slug, 'verified')
        models.log_site(slug, 'info', 'Copie vérifiée hors-ligne ; publication autorisée, arrêtée par défaut')
    except Exception as exc:
        reason = str(exc) if isinstance(exc, QuarantineError) else 'Erreur interne du traitement hors-ligne'
        state = 'imported' if imported else 'quarantined'
        models.set_verification(slug, state)
        models.update_status(slug, state, reason)
        checks = report.get('checks', {}) if isinstance(report, dict) else {}
        safe_failure = dict(protocol=PROTOCOL, stage=stage, ok=False, reason=reason,
                            checks={k: checks[k] for k in REQUIRED_CHECKS
                                    if isinstance(checks, dict) and type(checks.get(k)) is bool})
        if isinstance(report, dict):
            safe_failure.update(safe_diagnostics(report))
        try:
            _private_json(root / 'failure.json', safe_failure)
        except OSError:
            pass
        models.log_site(slug, 'error', f'Échec {stage} : {reason}')
        raise QuarantineError(f'Échec {stage} : {reason}') from None
    return models.get_site(slug)


def public_report(site):
    if not is_subscription(site):
        return None
    filename = 'report-07-verifier.json' if site.get('verification_state') == 'verified' else 'failure.json'
    path = config.SITES_DIR / site['slug'] / filename
    if not path.is_file():
        return None
    try:
        report = json.loads(path.read_text())
        checks = report.get('checks', {})
        stage = report.get('stage')
        if stage not in set(SCRIPTS) | {'database', 'importer', 'novamira'}:
            return None
        return {'stage': stage, 'ok': report.get('ok') is True, **safe_diagnostics(report),
                'checks': {k: checks[k] for k in REQUIRED_CHECKS
                           if isinstance(checks, dict) and type(checks.get(k)) is bool}}
    except (OSError, ValueError, AttributeError):
        return None


def runtime_compose(slug, *args, engine=None):
    site = models.get_site(slug)
    require_verified(site)
    if not is_subscription(site) or args not in (('start',), ('stop',), ('up', '-d')):
        raise QuarantineError('Opération incompatible avec le profil abonnements')
    path = config.SITES_DIR / slug / 'verified-compose.json'
    if not path.is_file():
        raise QuarantineError('Manifeste vérifié manquant')
    return (engine or Engine()).compose(path, *args)

