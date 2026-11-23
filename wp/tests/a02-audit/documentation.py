"""Optional public documentation check; never connects to a site or an account."""
import concurrent.futures
import datetime
import hashlib
import html
import json
import pathlib
import re
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[3]
URLS = [
    ('https://developer.wordpress.org/reference/functions/get_plugins/', 'get_plugins', [
        ('Plugin files and header inventory', 'Checks the plugins directory and retrieve all plugin files with plugin data.'),
    ]),
    ('https://developer.wordpress.org/reference/functions/wp_update_plugins/', 'update_plugins', [
        ('Native update cache', "get_site_transient( 'update_plugins' )"),
        ('Live checker sends plugin metadata; auditor must not invoke it', 'A list of all plugins installed is sent to api.wordpress.org, along with the site locale.'),
    ]),
    ('https://developer.woocommerce.com/docs/features/high-performance-order-storage/', 'authoritative', [
        ('Only count the authoritative store', 'If the woocommerce_custom_orders_table_enabled options is set to true, HPOS is active and the new tables are authoritative'),
    ]),
    ('https://woocommerce.com/document/woocommerce-memberships-restrict-content/', 'delay', [
        ('Native content and taxonomy restrictions', 'restriction rules for individual posts, pages, or taxonomies'),
        ('Native immediate and delayed access', 'immediately or after a certain time has passed'),
    ]),
    ('https://woocommerce.com/document/fix-outdated-templates-woocommerce/', 'version', [
        ('Woo templates evolve with releases', 'We sometimes update the default templates when a new version of WooCommerce is released.'),
        ('Theme and child overrides', 'templates overridden by your theme/child theme'),
    ]),
    ('https://developer.wordpress.org/reference/functions/locate_template/', 'stylesheet', [
        ('Child stylesheet directory precedes parent template directory', 'Searches in the stylesheet directory before the template directory'),
    ]),
]

def fetch(item):
    url, term, claims = item
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Imagine-A02-documentation'}), timeout=60) as response:
        raw = response.read()
        final = response.url
        status = response.status
    text = raw.decode('utf8')
    text = re.sub(r'<(script|style)\b[^>]*>.*?</\1>', '', text, flags=re.S | re.I)
    text = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', text)))
    hits = [m.start() for m in re.finditer(re.escape(term), text, re.I)]
    return {'url': url, 'final_url': final, 'status': status, 'sha256': hashlib.sha256(raw).hexdigest(), 'topic': term, 'topic_occurrences': len(hits)}

if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        results = list(pool.map(fetch, URLS))
    path = ROOT / 'production/A-02/sources-officielles.json'
    path.write_text(json.dumps(results, indent=2, ensure_ascii=False) + '\n', encoding='utf8')
    print(json.dumps(results, indent=2, ensure_ascii=False))
