import sys
sys.dont_write_bytecode=True
import hashlib,urllib.request
import c33 as o
urls=['https://developer.wordpress.org/reference/functions/redirect_canonical/','https://developer.wordpress.org/reference/hooks/rest_pre_dispatch/','https://developer.wordpress.org/reference/hooks/wp_sitemaps_add_provider/','https://developer.wordpress.org/reference/hooks/the_author/','https://developer.wordpress.org/reference/hooks/oembed_response_data/']
refs=[]
for url in urls:
    raw=urllib.request.urlopen(url,timeout=40).read();refs.append({'url':url,'status':200,'sha256':hashlib.sha256(raw).hexdigest()})
native=o.wp('''$o=['wp'=>get_bloginfo('version'),'blog_public'=>get_option('blog_public'),'sources'=>[]];foreach(['redirect_canonical','get_the_author_meta','get_oembed_response_data'] as $name){$r=new ReflectionFunction($name);$code=implode('',array_slice(file($r->getFileName()),$r->getStartLine()-1,$r->getEndLine()-$r->getStartLine()+1));$o['sources'][$name]=['file'=>basename($r->getFileName()),'line'=>$r->getStartLine(),'sha256'=>hash('sha256',$code),'author_url_hook'=>$name==='get_the_author_meta'?str_contains($code,"get_the_author_{$field}"):null];} $p=WC_ABSPATH.'includes/class-wc-post-data.php';$s=file($p);$o['native_product_query_cache_invalidation']=[];foreach($s as $i=>$line){if(str_contains($line,'product_query')){$o['native_product_query_cache_invalidation'][]=['line'=>$i+1,'source'=>trim($line)];}}echo wp_json_encode($o);'''.replace('"get_the_author_{$field}"',"'get_the_author_{$field}'"))
assert refs and native['sources']['get_the_author_meta']['author_url_hook'] and native['native_product_query_cache_invalidation']
o.b13.save(o,sys.argv[1],{'official':refs,'native':native,'sources':o.sources(o)})
print({'official_pages':len(refs),'wp':native['wp'],'sitemap_off_at_rest':native['blog_public']})
