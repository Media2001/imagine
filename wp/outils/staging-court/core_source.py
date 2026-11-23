"""Data-only archive core selection; public core preparation, never plugin install."""
import hashlib
import io
import json
from pathlib import PurePosixPath
import re
import tarfile
import urllib.request
import zipfile
from archive import Refusal

VERSION = r'[0-9]+\.[0-9]+(?:\.[0-9]+)?'


def select_version(package, expected=None):
    try:
        version = json.loads(package)['WordPress']['Version']
        if not isinstance(version, str) or not re.fullmatch(VERSION, version):
            raise ValueError
    except (TypeError, ValueError, KeyError):
        raise Refusal('SOURCE_CORE_METADATA_REFUSED') from None
    if expected is not None:
        if not isinstance(expected, str) or not re.fullmatch(VERSION, expected):
            raise Refusal('EXPECTED_CORE_VERSION_REFUSED')
        if version != expected:
            error = Refusal('SOURCE_EXPECTED_CORE_VERSION_MISMATCH')
            error.core_versions = {'source': version, 'expected': expected}
            raise error
    return version


class OfficialRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        from urllib.parse import urlsplit
        parsed = urlsplit(newurl)
        if parsed.scheme != 'https' or parsed.hostname not in ('wordpress.org', 'downloads.wordpress.org', 'api.wordpress.org', 'plugins.svn.wordpress.org'):
            raise Refusal('PUBLIC_DOWNLOAD_REDIRECT_REFUSED')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def download(url, limit=128 * 1024 * 1024):
    # Every caller constructs the URL itself from a validated version, never archive text.
    opener = urllib.request.build_opener(OfficialRedirect())
    try:
        with opener.open(url, timeout=60) as response:
            data = response.read(limit + 1)
            if response.status != 200 or len(data) > limit:
                raise Refusal('PUBLIC_DOWNLOAD_LIMIT')
            return data
    except Refusal:
        raise
    except Exception:
        raise Refusal('PUBLIC_DOWNLOAD_REFUSED') from None


def zip_payload(raw, root, destination, exclude_content=False):
    """Checked regular files only. Core packages never contribute bundled plugins/themes."""
    stream = io.BytesIO()
    manifest = {}
    with zipfile.ZipFile(io.BytesIO(raw)) as archive, tarfile.open(fileobj=stream, mode='w') as tar:
        entries = archive.infolist()
        if len(entries) > 40000 or sum(e.file_size for e in entries) > 512 * 1024 * 1024:
            raise Refusal('PUBLIC_PACKAGE_LIMIT')
        seen = set()
        for entry in entries:
            parts = entry.filename.rstrip('/').split('/')
            if (not parts or parts[0] != root or any(p in ('', '.', '..') for p in parts)
                    or any(c in entry.filename for c in '\\:')
                    or entry.external_attr >> 16 & 0o170000 not in (0, 0o040000, 0o100000)
                    or entry.filename.casefold() in seen):
                raise Refusal('PUBLIC_PACKAGE_PATH_REFUSED')
            seen.add(entry.filename.casefold())
            if entry.is_dir() or len(parts) == 1 or (exclude_content and parts[1] == 'wp-content'):
                continue
            relative = '/'.join(parts[1:])
            data = archive.read(entry)
            manifest[relative] = hashlib.sha256(data).hexdigest()
            item = tarfile.TarInfo(destination + '/' + relative)
            item.size = len(data)
            item.mode = 0o644
            tar.addfile(item, io.BytesIO(data))
    return stream.getvalue(), manifest


def prepare_core(version):
    select_version(json.dumps({'WordPress': {'Version': version}}))
    url = 'https://wordpress.org/wordpress-' + version + '.zip'
    raw = download(url)
    expected_md5 = download(url + '.md5', 1024).decode('ascii').strip().split()[0]
    if not re.fullmatch(r'[a-f0-9]{32}', expected_md5) or hashlib.md5(raw).hexdigest() != expected_md5:
        raise Refusal('PUBLIC_CORE_CHECKSUM_REFUSED')
    payload, files = zip_payload(raw, 'wordpress', 'opt/wordpress/wordpress', True)
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        text = archive.read('wordpress/wp-includes/version.php').decode()
    found = re.findall(r"^\s*\$wp_version\s*=\s*'(" + VERSION + r")';", text, re.M)
    if found != [version]:
        raise Refusal('PUBLIC_CORE_VERSION_REFUSED')
    return payload, {'url': url, 'version': version, 'sha256': hashlib.sha256(raw).hexdigest(),
                     'md5_official': expected_md5, 'core_files': files,
                     'bundled_wp_content_excluded': True, 'download_before_injection': True}


def numeric(version):
    parts = [int(p) for p in version.split('.')]
    return tuple(parts + [0] * (3 - len(parts)))


def plugin_warnings(content, wordpress, php):
    """WordPress-style header scan as inert text; requirements are warnings, never gates."""
    warnings = []
    for path in sorted(content.glob('plugins/*/*.php')) + sorted(content.glob('plugins/*.php')):
        header = path.read_bytes()[:8192].decode('utf-8', 'replace').replace('\r', '\n')
        prefix = r'^(?:[ \t]*<\?php)?[ \t\/*#@]*'
        if not re.search(prefix + r'Plugin Name:', header, re.M | re.I):
            continue
        for field, current, code in [('Requires at least', wordpress, 'PLUGIN_REQUIRES_NEWER_WORDPRESS'),
                                     ('Requires PHP', php, 'PLUGIN_REQUIRES_NEWER_PHP')]:
            match = re.search(prefix + field + r':[ \t]*(' + VERSION + r')[ \t]*(?:\*/)?[ \t]*$', header, re.M | re.I)
            if match and numeric(match[1]) > numeric(current):
                warnings.append({'code': code, 'plugin': path.relative_to(content).as_posix(),
                                 'required': match[1], 'current': current, 'blocking': False})
    return warnings
