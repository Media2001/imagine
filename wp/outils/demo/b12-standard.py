"""Read official native hook references; no WordPress/demo request."""
import sys
sys.dont_write_bytecode=True
import concurrent.futures
import hashlib
import html
import re
import urllib.request
import b12
URLS = [
 'https://developer.wordpress.org/reference/functions/wp_embed_register_handler/',
 'https://developer.wordpress.org/reference/classes/wp_embed/shortcode/',
 'https://developer.wordpress.org/reference/classes/wp_embed/cache_oembed/',
 'https://developer.wordpress.org/reference/hooks/pre_oembed_result/',
 'https://developer.wordpress.org/reference/hooks/pre_render_block/',
 'https://developer.wordpress.org/reference/hooks/rest_dispatch_request/',
 'https://developer.wordpress.org/reference/classes/wp_oembed_controller/get_proxy_item/'
]
def read(url):
    with urllib.request.urlopen(url,timeout=40) as response:
        raw=response.read(); status=response.status
    text=html.unescape(re.sub('<[^>]+>', ' ', re.sub(r'<(script|style)\b.*?</\1>', '', raw.decode('utf-8'), flags=re.S)))
    text=re.sub(r'\s+', ' ', text)
    title=html.unescape(re.search(r'<title>(.*?)</title>',raw.decode('utf-8'),re.S)[1])
    terms=['Registers an embed handler', 'Short-circuits the oEmbed result', 'Triggers a caching', 'Filters the REST API dispatch request result', 'Allow plugins to override', 'Serve oEmbed data from cache', 'null !== $dispatch_result', 'short-circuit', 'Allows render_block() to be short-circuited']
    excerpts=[]
    for term in terms:
        i=text.lower().find(term.lower())
        if i>=0: excerpts.append(text[max(0,i-50):i+600])
    return {'url':url,'status':status,'title':title,'page_sha256':hashlib.sha256(raw).hexdigest(),'excerpts':excerpts or [text[text.find('Description'):text.find('Description')+700]]}
if __name__=='__main__':
    rows=list(concurrent.futures.ThreadPoolExecutor(7).map(read,URLS))
    b12.save('sources-officielles-V2',{'sources':rows,'runtime_also_inspected':'WordPress 7.0.9 class-wp-embed.php, class-wp-oembed-controller.php, class-wp-rest-server.php'})
    for row in rows:print(row['title'], row['status'], row['excerpts'])
