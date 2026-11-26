"""Diagnostic C25 borné : seulement chemins de différence et noms d'options."""
import sys
sys.dont_write_bytecode = True
import json
import os
from pathlib import Path
import c25
receipt = json.loads((c25.PROOF / 'recette-02-V2.json').read_text(encoding='utf-8'))
raw = (Path(os.environ['TMPDIR']) / receipt['private_snapshot']['file']).read_bytes()
assert __import__('hashlib').sha256(raw).hexdigest() == receipt['private_snapshot']['sha256']
saved = json.loads(raw)['payload']
after = c25.b06.state()
def differences(a, b, path=''):
    if isinstance(a, dict) and isinstance(b, dict):
        for key in a.keys() | b.keys():
            if key not in a or key not in b:
                print('KEY', path + '/' + str(key))
            else:
                differences(a[key], b[key], path + '/' + str(key))
    elif a != b:
        print('DIFF', path)
differences(saved['business'], after)
current = c25.snapshot()
a = {x['option_name']: x for x in saved['database']['options']}
b = {x['option_name']: x for x in current['options']}
print('OPTIONS_CHANGED', [key for key in a.keys() | b.keys() if a.get(key) != b.get(key)])
print('POST_DATES_BEFORE', [{k: r[k] for k in ['ID','post_type','post_date_gmt','post_modified_gmt']} for r in saved['database']['posts'] if int(r['ID']) in [88,94]])
print('HPOS_DATES_AFTER', c25.wp('global $wpdb;echo wp_json_encode($wpdb->get_results("SELECT id,date_created_gmt,date_updated_gmt FROM {$wpdb->prefix}wc_orders WHERE id IN (88,94)",ARRAY_A));'))
c25.private('diagnostic-after', {'database': current, 'business': after})
