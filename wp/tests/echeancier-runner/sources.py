"""Fetch public official documentation, keep bounded evidence, task-local ledger."""
import concurrent.futures
import datetime
import hashlib
import html
from html.parser import HTMLParser
import json
import pathlib
import re
import subprocess
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = ROOT / 'production/C-05/sources'
LEDGER = OUT / 'ledger.json'
TOOL = pathlib.Path('C:/Users/Ced/AppData/Local/hermes/skills/research/grounded-citations/scripts/sources.py')
URLS = [
    ('https://woocommerce.com/document/subscriptions/develop/functions/', ['update_dates', 'can_date_be_updated']),
    ('https://woocommerce.com/document/subscriptions/renewal-process/', ['manual', 'failed']),
    ('https://woocommerce.com/document/subscriptions/creating-subscription-products/', ['expire', 'billing']),
    ('https://woocommerce.com/document/subscriptions/develop/action-reference/', ['woocommerce_subscription_payment_complete', 'woocommerce_scheduled_subscription_payment']),
    ('https://woocommerce.com/document/subscriptions/billing-date-alignment/creating-an-aligned-subscription-product/', ['regardless of the billing interval']),
    ('https://woocommerce.com/document/subscriptions/failed-payment-retry/', ['manual', 'On-hold']),
]
QUOTES = [
    'Check if a given date type can be updated for this subscription.',
    'Manual renewal – recurring payments require that your customers log into the store and make the payment for each payment interval.',
    'Set the billing interval using a number input and a period dropdown (day, week, month, year).',
    'It can also be triggered off-schedule by 3rd party code or store manager actions,',
    'It always uses the next occurring alignment date, regardless of the billing interval.',
    'Subscription must require automatic payments, not manual renewals',
]


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.ignore = 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.ignore += 1
        if tag in ('p', 'h1', 'h2', 'h3', 'h4', 'li', 'tr', 'pre'):
            self.parts.append('\n')

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.ignore -= 1
        if tag in ('p', 'h1', 'h2', 'h3', 'h4', 'li', 'tr', 'pre'):
            self.parts.append('\n')

    def handle_data(self, data):
        if not self.ignore:
            self.parts.append(data)


def fetch(pair):
    url, needles = pair
    with urllib.request.urlopen(url, timeout=90) as r:
        raw = r.read()
        final = r.url
        status = r.status
    h = Text()
    h.feed(raw.decode('utf-8'))
    text = re.sub(r'[ \t\r\f\v]+', ' ', html.unescape(''.join(h.parts)))
    text = re.sub(r'\n\s*\n+', '\n', text)
    contexts = []
    for needle in needles:
        locations = [m.start() for m in re.finditer(re.escape(needle), text, re.I)]
        contexts += [text[max(0, i - 100):i + 1800] for i in locations[:3]]
    return {'requested_url': url, 'url': final, 'status': status,
            'consulted_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'sha256_html': hashlib.sha256(raw).hexdigest(), 'contexts': contexts}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(fetch, URLS))
    for index, result in enumerate(results):
        p = subprocess.run([sys.executable, str(TOOL), '--ledger', str(LEDGER), 'add', result['url']], capture_output=True, text=True)
        assert p.returncode == 0, p.stderr
        result['ledger_receipt'] = p.stdout.strip()
        quote = QUOTES[index]
        contexts = '\n'.join(result['contexts'])
        assert quote in contexts, 'Quote not present in retrieved text: ' + quote
        assert len(quote.split()) <= 25
        evidence = OUT / ('extrait-' + str(index + 1) + '.txt')
        evidence.write_text(quote + '\n', encoding='utf-8')
        q = subprocess.run([sys.executable, str(TOOL), '--ledger', str(LEDGER), 'quote', str(index + 1),
                            '--text', quote, '--from', str(evidence)], capture_output=True, text=True)
        assert q.returncode == 0, q.stderr
        result['quote'] = quote
        result.pop('contexts')
    print(json.dumps(results, indent=2, ensure_ascii=False))
    (OUT / 'retrieval.json').write_text(json.dumps(results, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
