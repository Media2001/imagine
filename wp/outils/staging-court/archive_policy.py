"""A-01 file policy: closed uploads and site-specific secret candidates."""
import pathlib
import re

DEFAULT_MAX_BYTES = 50 * 1024**3
DEFAULT_MAX_ENTRIES = 2000000
DEFAULT_MAX_SQL_BYTES = 8 * 1024**3
CHUNK = 1024 * 1024
EXCLUDE_UPLOADS = frozenset('wpallexport wpallimport memberships_csv_exports memberships_csv_imports wc-logs wpdesk-logs ur-logs matomo wpdm-cache woocommerce-logs gravity_forms_logs wpforms-logs fluentform-logs'.split())
KEEP_UPLOADS = frozenset('woocommerce_uploads simple-file-list'.split())
MEDIA = frozenset('pdf jpg jpeg png gif webp avif svg ico tif tiff bmp'.split())


def unknown_upload(relative):
    parts = relative.split('/')
    return (parts[0] == 'uploads' and len(parts) > 2 and not re.fullmatch(r'[12][0-9]{3}', parts[1])
            and parts[1] not in KEEP_UPLOADS | EXCLUDE_UPLOADS)


def excluded(relative):
    parts = relative.split('/')
    low = relative.lower()
    suffix = pathlib.PurePosixPath(low).suffix
    dated = len(parts) > 2 and parts[0] == 'uploads' and bool(re.fullmatch(r'[12][0-9]{3}', parts[1]))
    if parts[0] in ('ai1wm-backups', 'cache', 'upgrade', 'updraft', 'backups', 'backup-db', 'wp-clone') or low.endswith(('.log', '.log.gz')):
        return True
    if relative != 'database.sql' and suffix in ('.zip', '.sql', '.wpress', '.gz', '.tgz', '.7z', '.tar') and not dated:
        return True
    if len(parts) > 2 and parts[0] == 'uploads':
        if parts[1] in EXCLUDE_UPLOADS:
            return True
        if parts[1] in KEEP_UPLOADS:
            return suffix.lstrip('.') not in MEDIA
    return False


def secret_candidate(relative):
    if excluded(relative) or relative in ('package.json', 'database.sql'):
        return False
    parts = relative.split('/')
    if parts[0] in ('plugins', 'themes'):
        return False
    suffix = pathlib.PurePosixPath(relative.lower()).suffix
    return suffix in ('.php', '.json', '.env', '.ini') or parts[-1] in ('.env', 'wp-config', '.htaccess', 'web.config')
