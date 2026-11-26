"""C23 : commande visiteur GET, sessions préparées en mémoire hors commande."""
import html
import json
import re
import unicodedata
import sys
from pathlib import Path
from datetime import datetime, timezone
import hashlib
from urllib.parse import urlencode, urlsplit, urljoin
from urllib.error import HTTPError
from urllib.request import Request, build_opener, HTTPRedirectHandler
sys.dont_write_bytecode = True
BASE = 'http://192.168.129.32:8085'
PROOF = Path(__file__).resolve().parents[3] / 'production/C-23'
PUBLICS = ['anonyme', 'connecte-sans-abonnement', 'decouverte-epuisee', 'acheteur-autre-numero', 'faux-robot']

def canonical(text):
    if isinstance(text, bytes):
        text = text.decode('utf-8', 'replace')
    try:
        text = json.dumps(json.loads(text), ensure_ascii=False)
    except (ValueError, TypeError):
        pass
    text = html.unescape(re.sub(r'<[^>]*>', '', text))
    return ' '.join(unicodedata.normalize('NFC', text).split())

def assess(status, body, witnesses, present=None, expected=(200,), positive=False):
    text = canonical(body)
    found = [w for w in witnesses if canonical(w) in text]
    exists = present is None or canonical(present) in text
    errors = any(x in text for x in ('Fatal error', 'Uncaught Error', 'critical error', 'Warning:'))
    return {'ok': status in expected and exists and not errors and (bool(found) if positive else not found),
            'leak': bool(found) and not positive, 'witnesses_found': len(found), 'surface_present': exists}
