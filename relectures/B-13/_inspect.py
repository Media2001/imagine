import json
d = json.load(open('browser-final-V2.json', encoding='utf-8'))
rows = d.get('rows')
print('rows type', type(rows), 'len', len(rows) if hasattr(rows,'__len__') else '?')
# rows likely list of surfaces
for r in (rows if isinstance(rows, list) else [rows]):
    if isinstance(r, dict):
        print('--- row keys', list(r.keys()))
        break
print(json.dumps(rows if not isinstance(rows,list) else rows[0], ensure_ascii=False)[:2000])
