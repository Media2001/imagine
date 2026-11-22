"""Read official public references, preserving bounded exact excerpts only."""
import concurrent.futures
import datetime
import hashlib
import html
from html.parser import HTMLParser
import json
import pathlib
import re
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[3]
REFERENCES = [
    ('https://woocommerce.com/document/subscriptions/develop/functions/', 'can_date_be_updated'),
    ('https://woocommerce.com/document/subscriptions/renewal-process/', 'Manual renewal'),
    ('https://woocommerce.com/document/subscriptions/creating-subscription-products/', 'billing interval'),
    ('https://woocommerce.com/document/subscriptions/develop/action-reference/', 'woocommerce_scheduled_subscription_payment'),
    ('https://woocommerce.com/document/subscriptions/billing-date-alignment/creating-an-aligned-subscription-product/', 'regardless of the billing interval'),
    ('https://woocommerce.com/document/subscriptions/failed-payment-retry/', 'manual renewals'),
    ('https://developer.wordpress.org/plugins/settings/settings-api/', 'options.php'),
    ('https://developer.wordpress.org/reference/functions/register_setting/', 'sanitize_callback'),
]

class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.ignore = 0
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.ignore += 1
    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.ignore -= 1
    def handle_data(self, data):
        if not self.ignore:
            self.parts.append(data)

def fetch(pair):
    url, term = pair
    with urllib.request.urlopen(url, timeout=90) as response:
        data, status, final = response.read(), response.status, response.url
    parser = Text()
    parser.feed(data.decode('utf-8'))
    text = re.sub(r'\s+', ' ', html.unescape(' '.join(parser.parts)))
    index = text.lower().index(term.lower())
    # Bounded short literal quotation, not a page archive.
    quote = ' '.join(text[index:].split()[:23])
    return {'url': final, 'status': status, 'consulted_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'page_sha256': hashlib.sha256(data).hexdigest(), 'term': term, 'quote': quote}

if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(fetch, REFERENCES))
    path = ROOT / 'production/C-05/sources/review-2026-11-22.json'
    path.write_text(json.dumps(results, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(results, indent=2, ensure_ascii=False))
