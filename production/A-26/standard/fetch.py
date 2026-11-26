"""Retrieve official technical references only; no site or account access."""
import datetime
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import urllib.request

class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.skip += 1
    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip = max(0, self.skip - 1)
    def handle_data(self, value):
        if not self.skip and value.strip():
            self.parts.append(value.strip())

urls = [
    ('parse_blocks', 'https://developer.wordpress.org/reference/functions/parse_blocks/'),
    ('get_shortcode_regex', 'https://developer.wordpress.org/reference/functions/get_shortcode_regex/'),
    ('get_option', 'https://developer.wordpress.org/reference/functions/get_option/'),
    ('get_plugins', 'https://developer.wordpress.org/reference/functions/get_plugins/'),
    ('privacy', 'https://developer.wordpress.org/plugins/privacy/'),
    ('sitekit_settings', 'https://raw.githubusercontent.com/google/site-kit-wp/develop/includes/Modules/Analytics_4/Settings.php'),
    ('embeds', 'https://wordpress.org/documentation/article/embeds/'),
    ('consent_api', 'https://wordpress.org/plugins/wp-consent-api/'),
]
out = Path(__file__).resolve().parent
rows = []
for name, url in urls:
    try:
        data = urllib.request.urlopen(url, timeout=45).read()
        text = data.decode('utf-8')
        if '<html' in text.lower() or '<!doctype' in text.lower():
            parser = Text()
            parser.feed(text)
            text = '\n'.join(parser.parts)
        (out / (name + '.txt')).write_text(text, encoding='utf-8')
        rows.append({'name': name, 'url': url, 'retrieved_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                     'source_sha256': hashlib.sha256(data).hexdigest(), 'text_sha256': hashlib.sha256(text.encode()).hexdigest(), 'status': 'retrieved'})
        print(name, 'OK')
    except Exception as error:
        rows.append({'name': name, 'url': url, 'status': type(error).__name__})
        print(name, type(error).__name__)
(out / 'sources.json').write_text(json.dumps(rows, indent=2) + '\n', encoding='utf-8')
