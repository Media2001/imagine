"""Collecte officielle bornée, sans site ni donnée de visiteur."""
import hashlib
import json
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]; self.skip=0
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style'): self.skip+=1
    def handle_endtag(self,tag):
        if tag in ('script','style'): self.skip=max(0,self.skip-1)
    def handle_data(self,d):
        if not self.skip and d.strip(): self.parts.append(d.strip())
urls={
 'pages':'https://wordpress.org/documentation/article/pages/',
 'blocs':'https://wordpress.org/documentation/article/details-block/',
 'privacy':'https://developer.wordpress.org/reference/functions/get_privacy_policy_url/',
 'insert':'https://developer.wordpress.org/reference/functions/wp_insert_post/',
 'meta':'https://developer.wordpress.org/reference/functions/update_post_meta/',
 'type':'https://developer.wordpress.org/reference/functions/register_post_type/',
 'menu':'https://developer.wordpress.org/reference/functions/wp_update_nav_menu_item/',
 'creation-menu':'https://developer.wordpress.org/reference/hooks/wp_create_nav_menu/',
 'export':'https://developer.wordpress.org/plugins/privacy/adding-the-personal-data-exporter-to-your-plugin/',
 'effacement':'https://developer.wordpress.org/plugins/privacy/adding-the-personal-data-eraser-to-your-plugin/'
}
rows={}
for key,url in urls.items():
    raw=urllib.request.urlopen(url,timeout=50).read(); parser=Text();parser.feed(raw.decode('utf-8'))
    parts=parser.parts
    needles=['wp_page_for_privacy_policy','wp_unslash','stripslashes','wp_slash','show_in_rest','publicly_queryable','exclude_from_search','wp_add_nav_menu_item','wp_create_nav_menu','content','callback','summary']
    selected=[]
    for i,line in enumerate(parts):
        if any(n.lower() in line.lower() for n in needles):
            selected.append(' '.join(parts[max(0,i-1):i+2])[:1600])
    rows[key]={'url':url,'sha256':hashlib.sha256(raw).hexdigest(),'extraits':selected[:16]}
    print(key,len(raw),selected[:1])
p=Path(__file__).resolve().parents[3]/'production/B-09/sources-officielles.json'
assert not p.exists()
p.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
