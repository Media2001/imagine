"""Read-only A09 redirect plan checker. No automatic redirect handling."""
import argparse
import csv
import html
import http.client
import importlib.util
import json
import pathlib
import re
import sys
import time
from urllib.parse import urlsplit, urljoin
sys.dont_write_bytecode = True

REPO = pathlib.Path(__file__).resolve().parents[4]
REDIRECTS = {301, 302, 303, 307, 308}


def need(ok, code):
    if not ok:
        raise ValueError(code)


def plain_file(path, code):
    path = pathlib.Path(path).absolute()
    need(not any(p.is_symlink() for p in [path, *path.parents]) and path.is_file(), code)
    need(path.stat().st_size <= 1048576, code)
    return path.resolve()


def relative(value):
    """Conservative ASCII URI paths; normalize percent-encoded unreserved."""
    need(isinstance(value, str) and 0 < len(value) <= 2048, 'A09_PLAN_URL')
    need(not re.search(r'[\\\x00-\x20\x7f-\uffff#]', value), 'A09_PLAN_URL')
    need(value.startswith('/') and not value.startswith('//'), 'A09_PLAN_URL')
    need(not re.search(r'%(?![a-fA-F0-9]{2})', value), 'A09_PLAN_URL')
    need(not re.search(r'%(?:0[0-9a-f]|1[0-9a-f]|20|2f|5c|7f)', value, re.I), 'A09_PLAN_URL')
    value = re.sub(r'%([a-fA-F0-9]{2})', lambda m: chr(int(m[1], 16)) if re.fullmatch(r'[A-Za-z0-9_.~-]', chr(int(m[1], 16))) else '%'+m[1].upper(), value)
    parts = urlsplit(value)
    need(not parts.scheme and not parts.netloc and not parts.fragment and not any(s in ['.', '..'] for s in parts.path.split('/')), 'A09_PLAN_URL')
    return value


def load_plan(path):
    path = plain_file(path, 'A09_PLAN_FILE')
    need(path.is_relative_to(REPO), 'A09_PLAN_NOT_IN_REPOSITORY')
    rows = []
    seen = set()
    try:
        with open(path, encoding='utf-8-sig', newline='') as stream:
            reader = csv.reader(stream, strict=True)
            need(next(reader, None) == ['ancienne', 'cible', 'code'], 'A09_PLAN_HEADER')
            for row in reader:
                need(len(row) == 3 and len(rows) < 1000, 'A09_PLAN_COLUMNS_OR_LIMIT')
                old, target, code = row
                canonical_old, canonical_target = relative(old), relative(target)
                need(code in [str(v) for v in REDIRECTS], 'A09_PLAN_CODE')
                need(canonical_old not in seen, 'A09_PLAN_DUPLICATE_OR_CONFLICT')
                need(canonical_old != canonical_target, 'A09_PLAN_SELF')
                seen.add(canonical_old)
                rows.append({'line': reader.line_num, 'ancienne': old, 'cible': target, 'code': int(code)})
    except (csv.Error, UnicodeError):
        raise ValueError('A09_PLAN_ENCODING_OR_CSV') from None
    need(bool(rows), 'A09_PLAN_EMPTY')
    return rows


def origin(value):
    need(isinstance(value, str) and not re.search(r'[\\\x00-\x20\x7f-\uffff]', value), 'A09_BASE_URL')
    parts = urlsplit(value)
    need(parts.scheme in ['http', 'https'] and parts.hostname and parts.username is None and parts.password is None
         and parts.path in ['', '/'] and not parts.query and not parts.fragment and '?' not in value and '#' not in value, 'A09_BASE_URL')
    host = parts.hostname
    need(bool(re.fullmatch(r'[A-Za-z0-9.:-]+', host)) and '%' not in host, 'A09_BASE_URL')
    port = parts.port if parts.port is not None else (443 if parts.scheme == 'https' else 80)
    need(0 < port <= 65535, 'A09_BASE_URL')
    host = '['+host+']' if ':' in host else host
    return parts.scheme+'://'+host.lower()+(':'+str(port) if port != (443 if parts.scheme == 'https' else 80) else '')


def authorize_site(site, base_url):
    """Same three marker predicates and exact safety bytes as A04/A05; no WP boot."""
    base = origin(base_url)
    site = pathlib.Path(site).absolute()
    need(site.is_dir() and site.resolve() == site and not any(p.is_symlink() for p in [site, *site.parents]), 'A09_SITE_PATH')
    spec = importlib.util.spec_from_file_location('a09_native_guard', pathlib.Path(__file__).resolve().parents[1]/'a04/update.py')
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    try:
        marker = guard.load_json(guard.safe_path(site, '.imagine-staging-verified.json'))
        need(isinstance(marker, dict) and marker.get('status') == 'verified' and marker.get('offline_verified') is True
             and marker.get('runtime_probe_passed') is True, 'A09_NOT_VERIFIED')
        declaration = guard.load_json(guard.safe_path(site, '.imagine-a09-http.json'))
        need(set(declaration) == {'schema', 'kind', 'base_url'} and declaration['schema'] == 'imagine-a09-http-v1'
             and declaration['kind'] in ['test', 'staging'] and origin(declaration['base_url']) == base, 'A09_DECLARATION')
        safety = guard.safe_path(site, 'wp-content/mu-plugins/000-imagine-staging-safety.php')
        reference = REPO/'wp/outils/staging/mu-plugins/000-imagine-staging-safety.php'
        need(safety.is_file() and reference.is_file() and guard.digest(safety) == guard.digest(reference), 'A09_SAFETY_BYTES')
    except guard.Refusal:
        raise ValueError('A09_SITE_MARKER_OR_PATH') from None
    return base


class Client:
    """Direct connections: no proxies, cookies, auth, retries or implicit redirects."""
    def __init__(self, base, interval, timeout):
        self.base, self.interval, self.timeout = base, interval, timeout
        self.last = None
        self.requests = 0

    def get(self, url):
        parts = urlsplit(url)
        need(origin(parts.scheme+'://'+parts.netloc) == self.base, 'A09_OTHER_ORIGIN')
        path = relative(parts.path or '/')+('?' + parts.query if parts.query else '')
        if self.last is not None:
            time.sleep(max(0, self.interval-(time.monotonic()-self.last)))
        self.last = time.monotonic()
        self.requests += 1
        connection_type = http.client.HTTPSConnection if parts.scheme == 'https' else http.client.HTTPConnection
        connection = connection_type(parts.hostname, parts.port, timeout=self.timeout)
        try:
            connection.request('GET', path, headers={'User-Agent': 'Imagine-A09/1', 'Connection': 'close'})
            response = connection.getresponse()
            return response.status, response.headers.get_all('Location', [])
        finally:
            connection.close()


def check_row(client, row):
    url = client.base+relative(row['ancienne'])
    result = {**row, 'observed_code': None, 'observed_target': None, 'final_status': None, 'hops': 0, 'issues': [], 'trace': []}
    issues, seen = result['issues'], set()
    try:
        for attempt in range(9):
            if url in seen:
                issues.append('boucle')
                break
            seen.add(url)
            status, locations = client.get(url)
            result['trace'].append({'url': url, 'status': status})
            if attempt == 0:
                result['observed_code'] = status
                if status != row['code']:
                    issues.append('mauvais_code')
            if status not in REDIRECTS:
                result['final_status'] = status
                if status != 200:
                    issues.append('cible_non_200')
                break
            result['hops'] += 1
            if result['hops'] == 2:
                issues.append('chaine')
            if len(locations) != 1 or not locations[0]:
                issues.append('redirection_invalide')
                break
            location = locations[0]
            if attempt == 0:
                result['observed_target'] = location
            need(len(location) <= 2048 and not re.search(r'[\\\x00-\x20\x7f-\uffff]', location), 'A09_LOCATION')
            target = urljoin(url, location)
            parts = urlsplit(target)
            if parts.scheme not in ['http', 'https'] or origin(parts.scheme+'://'+parts.netloc) != client.base:
                issues.append('cible_externe')
                break
            path = relative((parts.path or '/')+('?' + parts.query if parts.query else ''))
            if attempt == 0 and (path != relative(row['cible']) or parts.fragment):
                issues.append('mauvaise_cible')
            if attempt == 8:
                issues.append('limite_sauts')
                break
            url = client.base+path
    except TimeoutError:
        issues.append('delai_depasse')
    except (OSError, http.client.HTTPException):
        issues.append('erreur_http')
    except ValueError:
        issues.append('redirection_invalide')
    return result


def write_reports(output, rows, client):
    bad = [r for r in rows if r['issues']]
    report = {'schema': 'imagine-a09-report-v1', 'base_url': client.base, 'read_only': True,
              'requests': client.requests, 'total': len(rows), 'nonconformes': len(bad), 'rows': rows}
    (output/'rapport.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
    lines = ['# Test des redirections — lecture seule', '', str(len(rows)-len(bad))+' CONFORME ; '+str(len(bad))+' non conforme(s).', '',
             '| Ligne | Ancienne | Code attendu | Code observé | Cible attendue | Cible observée | HTTP final | Sauts | Résultat |',
             '|---|---|---|---|---|---|---|---|---|']
    for row in rows:
        cells = [row[k] for k in ['line', 'ancienne', 'code', 'observed_code', 'cible', 'observed_target', 'final_status', 'hops']]
        cells.append(', '.join(row['issues']) or 'CONFORME')
        lines.append('| '+' | '.join(html.escape(str(v) if v is not None else '—').replace('|', '&#124;').replace('\r', ' ').replace('\n', ' ') for v in cells)+' |')
    text = '\n'.join(lines)+'\n'
    (output/'rapport.md').write_text(text, encoding='utf8')
    with open(output/'nonconformes.csv', 'w', encoding='utf-8-sig', newline='') as stream:
        fields = ['line', 'ancienne', 'cible', 'code', 'observed_code', 'observed_target', 'final_status', 'hops', 'issues']
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        for row in bad:
            values = {**row, 'issues': ', '.join(row['issues'])}
            writer.writerow({k: "'"+v if isinstance(v, str) and v.startswith(('=', '+', '-', '@', '\t', '\r', '\n')) else v for k, v in values.items()})
    print(text, end='')
    return int(bool(bad))


def main(argv=None):
    parser = argparse.ArgumentParser(description='A09 : vérifier, jamais décider ni installer des redirections.')
    for key in ['wp-path', 'plan', 'output']:
        parser.add_argument('--'+key, type=pathlib.Path, required=True)
    parser.add_argument('--base-url', required=True)
    parser.add_argument('--interval', type=float, default=0.5)
    parser.add_argument('--timeout', type=float, default=5)
    args = parser.parse_args(argv)
    try:
        rows = load_plan(args.plan)
        need(0.1 <= args.interval <= 60 and 0.05 <= args.timeout <= 30, 'A09_RATE_OR_TIMEOUT')
        base = authorize_site(args.wp_path, args.base_url)
        output = args.output.absolute()
        need(not any(p.is_symlink() for p in [output, *output.parents]) and not output.exists()
             and output.parent.is_dir() and not output.resolve().is_relative_to(args.wp_path.resolve()), 'A09_OUTPUT')
        output.mkdir(mode=0o700)
        client = Client(base, args.interval, args.timeout)
        return write_reports(output, [check_row(client, row) for row in rows], client)
    except (ValueError, OSError, TypeError, KeyError, http.client.HTTPException) as error:
        code = str(error) if re.fullmatch(r'A09_[A-Z_]+', str(error)) else 'A09_CHECK_FAILED'
        print(code, file=sys.stderr)
        return 2
