"""Optional public documentation check; never connects to a site or an account."""
import concurrent.futures
import hashlib
import html
import json
import pathlib
import re
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[3]
URLS = [
    ('https://developer.wordpress.org/reference/functions/get_plugins/', 'get_plugins'),
    ('https://developer.wordpress.org/reference/functions/wp_update_plugins/', 'update_plugins'),
    ('https://developer.woocommerce.com/docs/features/high-performance-order-storage/', 'authoritative'),
    ('https://woocommerce.com/document/woocommerce-memberships-restrict-content/', 'drip'),
    ('https://woocommerce.com/document/fix-outdated-templates-woocommerce/', 'version'),
]

def fetch(item):
    url, term = item
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Imagine-A02-documentation'}), timeout=60) as response:
        raw = response.read()
        final = response.url
        status = response.status
    text = raw.decode('utf8')
    text = re.sub(r'<(script|style)\b[^>]*>.*?</\1>', '', text, flags=re.S | re.I)
    text = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', text)))
    hits = [m.start() for m in re.finditer(re.escape(term), text, re.I)]
    excerpts = [text[max(0, p - 80):p + 700] for p in hits[-3:]]
    return {'url': url, 'final_url': final, 'status': status, 'sha256': hashlib.sha256(raw).hexdigest(), 'topic': term, 'excerpts': excerpts}

if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        results = list(pool.map(fetch, URLS))
    path = ROOT / 'production/A-02/sources-officielles.json'
    path.write_text(json.dumps(results, indent=2, ensure_ascii=False) + '\n', encoding='utf8')
    print(json.dumps(results, indent=2, ensure_ascii=False))
