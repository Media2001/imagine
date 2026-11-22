"""Preserve the two distinct missing official citations, without page archives."""
import datetime
import hashlib
import importlib.util
import json
import pathlib
import re
import sys
import urllib.request

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location('c05_official_parser', HERE / 'official-review.py')
parser_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser_module)
REFERENCES = [
    {'source': '[5]', 'issue': 'M3',
     'url': 'https://woocommerce.com/document/subscriptions/billing-date-alignment/creating-an-aligned-subscription-product/',
     'quotes': ['Customer signs up: April 6', 'First renewal date: May 1 (not July 1)'],
     'context_fr': 'Exemple officiel : abonnement tous les trois mois, aligné au premier du mois ; inscription le 6 avril, premier renouvellement le 1er mai, non le 1er juillet.'},
    {'source': '[4]', 'issue': 'C05-02',
     'url': 'https://woocommerce.com/document/subscriptions/develop/action-reference/',
     'quotes': ['woocommerce_subscription_payment_complete',
                'subscription date changes related to early renewals are processed differently than other renewals'],
     'context_fr': 'La section de ce hook avertit de ne pas se fier à cette action pour capturer la prochaine date de paiement : le traitement des dates diffère lors des renouvellements anticipés.'},
]


def main():
    out = ROOT / 'production/C-05/sources/review-fusion-22nov-1458.json'
    assert not out.exists(), 'Preserve previous citation receipts'
    results = []
    for reference in REFERENCES:
        with urllib.request.urlopen(reference['url'], timeout=90) as response:
            data, status, url = response.read(), response.status, response.url
        parser = parser_module.Text()
        parser.feed(data.decode('utf-8'))
        text = re.sub(r'\s+', ' ', ' '.join(parser.parts)).strip()
        assert status == 200
        assert sum(len(q.split()) for q in reference['quotes']) <= 25
        assert all(quote in text for quote in reference['quotes'])
        if reference['source'] == '[4]':
            first = text.index("Action: 'woocommerce_subscription_payment_complete'")
            end = text.index("Action: 'woocommerce_subscription_renewal_payment_complete'", first)
            assert reference['quotes'][1] in text[first:end], 'Quote must refer to the exact requested hook'
        results.append({**reference, 'final_url': url, 'status': status,
                        'consulted_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                        'page_sha256': hashlib.sha256(data).hexdigest(),
                        'literal_quotes_verified': True})
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
