"""Vérifier uniquement cinq sources officielles publiques ; aucun site démo.
Les extraits restent dans la seule section C32 du README, sans copie juridique.
"""
import sys
sys.dont_write_bytecode = True
import concurrent.futures
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unicodedata
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
    def handle_data(self, text):
        self.parts.append(text)


def normalized(text):
    return ' '.join(unicodedata.normalize('NFKC', text).replace('`', '').replace('’', "'").split())


def main(label):
    readme = (ROOT/'wp/plugins/imagine-site/README.md').read_text(encoding='utf-8').split('## C-32 — cookies observés sur la démonstration\n', 1)[1].split('\n## ', 1)[0]
    lines = {int(line[0]): line for line in readme.splitlines() if re.match(r'^[1-5]\. ', line)}
    urls = [
        ('https://developer.wordpress.org/advanced-administration/wordpress/cookies/', [1]),
        ('https://developer.wordpress.org/reference/functions/wp_set_comment_cookies/', [2]),
        ('https://woocommerce.com/document/woocommerce-cookies/', [3]),
        ('https://woocommerce.com/document/order-attribution-tracking/', [4, 5]),
        ('https://raw.githubusercontent.com/woocommerce/woocommerce/trunk/plugins/woocommerce/src/Internal/Features/FeaturesController.php', []),
    ]
    def fetch(item):
        url, numbers = item
        request = urllib.request.Request(url, headers={'User-Agent': 'Imagine-C32-official-doc-check/1.0'})
        with urllib.request.urlopen(request, timeout=60) as response:
            data = response.read()
            status = response.status
            final_url = response.url
        text = data.decode('utf-8')
        if numbers:
            parser = Text()
            parser.feed(text)
            text = ' '.join(parser.parts)
        excerpts = [excerpt for number in numbers for excerpt in re.findall('« ([^»]+) »', lines[number])]
        if not numbers:
            excerpts = ['woocommerce_feature_%s_enabled']
        present = [normalized(excerpt) in normalized(text) for excerpt in excerpts]
        return {'url':url, 'final_url':final_url, 'http_status':status, 'sha256':hashlib.sha256(data).hexdigest(), 'readme_lines':numbers, 'excerpts_checked':len(excerpts), 'excerpts_present':present, 'pass':bool(present) and all(present)}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        official = list(pool.map(fetch, urls))
    result = {'scope':'C32_OFFICIAL_DOCS_ONLY', 'demo_accessed':False, 'official':official, 'pass':all(row['pass'] for row in official), 'readme_c32_sha256':hashlib.sha256(readme.encode()).hexdigest()}
    with (OUT/(label+'.json')).open('x', encoding='utf-8') as file:
        json.dump(result, file, indent=2, ensure_ascii=False)
    print(json.dumps({'pass':result['pass'], 'sources':[{k:r[k] for k in ['url', 'excerpts_present']} for r in official]}, ensure_ascii=False))
    return 0 if result['pass'] else 1


if __name__=='__main__':
    if len(sys.argv)!=2 or not re.fullmatch(r'[A-Za-z0-9_-]+', sys.argv[1]):
        raise SystemExit('Usage : python -B production/C-32/verify-official.py LABEL')
    raise SystemExit(main(sys.argv[1]))
