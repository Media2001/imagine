"""Public official documentation only, separate from offline native acceptance."""
import concurrent.futures
import datetime
import hashlib
import html
import json
import pathlib
import re
import urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[3]
SOURCES=[
('https://woocommerce.com/document/coupon-management/','Coupons: Overview','Core provides coupon types, product/email restrictions and usage limits; no custom rule engine needed.'),
('https://woocommerce.com/document/subscriptions/subscriptions-coupons/','Recurring Product Discount','Subscriptions distinguishes recurring and sign-up discounts; fixed payment limit is a configured total, not remaining renewals.'),
('https://woocommerce.com/document/subscriptions/limited-payment-coupon-guide/','initial payment','The configured limited-coupon total includes an eligible initial payment; future effective discount depends on payment history.'),
('https://developer.woocommerce.com/docs/features/high-performance-order-storage/','Authoritative tables','Only the configured authoritative order store is counted; order items are the native coupon carrier relation.'),
]
def fetch(item):
    url,anchor,decision=item
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Imagine-A10-public-documentation'}),timeout=60) as r:
        body=r.read(); final=r.url; status=r.status
    text=html.unescape(re.sub('<[^>]+>',' ',body.decode('utf8')))
    assert anchor in text, 'OFFICIAL_ANCHOR_MISSING'
    return {'url':url,'final_url':final,'http_status':status,'sha256':hashlib.sha256(body).hexdigest(),'anchor':anchor,'decision':decision,'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    results=list(pool.map(fetch,SOURCES))
path=ROOT/'production/A-10/sources-officielles.json'
path.write_text(json.dumps(results,indent=2)+'\n',encoding='utf8')
print(json.dumps(results,indent=2))
