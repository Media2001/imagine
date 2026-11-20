"""Operator-only command. Import is OFFLINE and never starts web by default."""
import argparse
import getpass
import json
import os
import sys
from pathlib import Path

from . import config, models, subscriptions


def read_password(fd):
    if fd is not None:
        if fd < 0:
            raise subscriptions.QuarantineError('Descripteur de mot de passe invalide')
        with os.fdopen(os.dup(fd), 'r') as stream:
            value = stream.readline(4097).rstrip('\r\n')
        if not value or len(value) > 4096:
            raise subscriptions.QuarantineError('Mot de passe absent ou trop long')
        return value
    if not sys.stdin.isatty():
        raise subscriptions.QuarantineError('Terminal privé requis, ou --password-fd explicite')
    return getpass.getpass('Mot de passe administrateur de test (non enregistré) : ')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--name', required=True)
    parser.add_argument('--archive', required=True, type=Path)
    parser.add_argument('--workflow', required=True, type=Path,
                        help='approved repository snapshot, path visible to both CLI and Docker host')
    parser.add_argument('--production-url', required=True)
    parser.add_argument('--port', required=True, type=int)
    parser.add_argument('--worker-image', required=True)
    parser.add_argument('--db-image', required=True)
    parser.add_argument('--nginx-image', required=True)
    parser.add_argument('--password-fd', type=int, help='read one line from a private file descriptor')
    parser.add_argument('--table-decisions', type=Path, help='Ced-approved JSON: table names, action, optional column names only')
    parser.add_argument('--start', action='store_true', help='publish web ONLY after successful verification')
    args = parser.parse_args(argv)
    try:
        decisions = None
        if args.table_decisions:
            if args.table_decisions.is_symlink() or args.table_decisions.stat().st_size > 4096:
                raise subscriptions.QuarantineError('Fichier de décisions invalide')
            decisions = json.loads(args.table_decisions.read_text(encoding='utf-8'))
        password = read_password(args.password_fd)
        models.init_db()
        site = subscriptions.create_offline(
            name=args.name, archive=args.archive, workflow=args.workflow,
            production_url=args.production_url, staging_url=f'http://{config.NAS_HOST}:{args.port}',
            port=args.port, worker_image=args.worker_image, db_image=args.db_image,
            nginx_image=args.nginx_image, admin_password=password, table_decisions=decisions)
        del password
        if args.start:
            try:
                subscriptions.runtime_compose(site['slug'], 'up', '-d')
            except subscriptions.QuarantineError:
                # Stop only the newly verified site if a partial publication failed.
                try:
                    subscriptions.runtime_compose(site['slug'], 'stop')
                except subscriptions.QuarantineError:
                    pass
                raise subscriptions.QuarantineError('Copie vérifiée ; publication échouée, arrêt ciblé demandé') from None
        print(json.dumps({**{key: site[key] for key in ('slug', 'status', 'verification_state')},
                          'verification_report': subscriptions.public_report(site)}, ensure_ascii=False))
        return 0
    except subscriptions.QuarantineError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except Exception:
        # Never let a traceback reveal private paths, credentials or imported output.
        print('Erreur opérateur ; aucun traitement historique de secours', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
