"""Contrôleur pur C33 : en-têtes complets avant occultation, auteur XML exact."""
import json
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit

RSS = 'http://purl.org/dc/elements/1.1/'
ATOM = 'http://www.w3.org/2005/Atom'
SAFE_HEADERS = {'location', 'content-type', 'link'}


def pairs(headers):
    if isinstance(headers, dict):
        return list(headers.items())
    return [(row['name'], row['value']) for row in headers]


def archive_headers(headers):
    # Aucune valeur sensible, même pour un nom sûr : les trois valeurs sont
    # conservées seulement sur la démo où aucune authentification n'est envoyée.
    return {name.lower(): value for name, value in pairs(headers) if name.lower() in SAFE_HEADERS}


def feed_author(body, fixture_path):
    root = ET.fromstring(body)
    if root.tag == 'rss':
        matches = [item for item in root.findall('./channel/item')
                   if urlsplit(item.findtext('link', '')).path == fixture_path]
        field, uri_fields, kind = '{' + RSS + '}creator', ['{' + RSS + '}creator/{' + RSS + '}url', 'author/url', 'author/uri'], 'rss2'
    elif root.tag == '{' + ATOM + '}feed':
        matches = [entry for entry in root.findall('{' + ATOM + '}entry')
                   if any(urlsplit(link.get('href', '')).path == fixture_path
                          for link in entry.findall('{' + ATOM + '}link')
                          if link.get('rel', 'alternate') == 'alternate')]
        field, uri_fields, kind = '{' + ATOM + '}author/{' + ATOM + '}name', ['{' + ATOM + '}author/{' + ATOM + '}uri', '{' + ATOM + '}author/{' + ATOM + '}url'], 'atom'
    else:
        return {'present': False, 'author': None, 'author_fields': 0, 'account_uri_absent': False, 'format': None}
    if len(matches) != 1:
        return {'present': False, 'author': None, 'author_fields': 0, 'account_uri_absent': False, 'format': kind}
    item = matches[0]
    authors = item.findall(field)
    uri_values = [''.join(node.itertext()).strip() for path in uri_fields for node in item.findall(path)]
    # Les URI natives vides sont acceptées ; aucune URI de compte non vide.
    return {'present': True, 'author': ''.join(authors[0].itertext()) if len(authors) == 1 else None,
            'author_fields': len(authors), 'account_uri_absent': not any(uri_values), 'format': kind}


def control(kind, status, body, headers, fixture_path, login, display, expected_signature):
    all_pairs = pairs(headers)
    # Recherche des noms ET valeurs de tous les champs, doublons compris.
    header_text = '\n'.join(str(k) + ':' + str(v) for k, v in all_pairs)
    leak = any(t in body + '\n' + header_text for t in [login, display])
    metadata = {'headers_inspected': len(all_pairs), 'all_headers_inspected': True}
    lower = {k.lower(): v for k, v in all_pairs}
    if kind == 'author':
        present, ok = bool(body or lower.get('location')), status == 404
    elif kind == 'rest':
        try:
            data = json.loads(body)
            present = isinstance(data, dict) and isinstance(data.get('code'), str)
        except ValueError:
            present = False
        ok = status == 404
    elif kind == 'sitemap':
        try:
            root = ET.fromstring(body)
            locs = [e.text for e in root.iter() if e.tag.endswith('loc')]
            present = root.tag.endswith('sitemapindex') and bool(locs)
        except ET.ParseError:
            present, locs = False, []
        ok = status == 200 and not any('wp-sitemap-users-' in (loc or '') for loc in locs)
    elif kind == 'users-sitemap':
        present, ok = bool(body), status in [200, 404] and '<urlset' not in body
    elif kind == 'feed':
        try:
            details = feed_author(body, fixture_path)
        except ET.ParseError:
            details = {'present': False, 'author': None, 'author_fields': 0, 'account_uri_absent': False, 'format': None}
        present = details.pop('present')
        metadata.update(details)
        ok = status == 200 and details['author_fields'] == 1 and details['author'] == expected_signature and details['account_uri_absent']
    else:
        try:
            data = json.loads(body)
            present = data.get('type') == 'rich' and bool(data.get('html')) and data.get('title') == 'FICTIF C33 article public'
        except ValueError:
            present, data = False, {}
        ok = status == 200 and data.get('author_name') == expected_signature and 'author_url' not in data
    return {'ok': bool(present and ok and not leak), 'present': bool(present), 'leak': leak, **metadata}


def remove_feed_author(body, fixture_path):
    root = ET.fromstring(body)
    if root.tag == 'rss':
        candidates, field = root.findall('./channel/item'), '{' + RSS + '}creator'
        selected = [item for item in candidates if urlsplit(item.findtext('link', '')).path == fixture_path]
    else:
        candidates, field = root.findall('{' + ATOM + '}entry'), '{' + ATOM + '}author'
        selected = [item for item in candidates if any(urlsplit(link.get('href', '')).path == fixture_path for link in item.findall('{' + ATOM + '}link') if link.get('rel', 'alternate') == 'alternate')]
    assert len(selected) == 1 and selected[0].findall(field), 'Mutation exige un auteur témoin présent'
    for node in selected[0].findall(field):
        selected[0].remove(node)
    return ET.tostring(root, encoding='unicode')
