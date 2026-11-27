import sys
sys.dont_write_bytecode=True
import json
import b16 as owner
import b13
f=b13.wp('echo wp_json_encode(get_option("imagine_b11_fixture"));')
before=b13.c29.state()
src=(owner.ROOT/'wp/tests/demo/b11-runtime.php').read_text(encoding='utf-8').split('<?php',1)[1]
code="global $wpdb;$wpdb->query('START TRANSACTION');try{$GLOBALS['b11_issue']="+str(f['issue'])+";$GLOBALS['b11_article']="+str(f['article'])+";eval("+b13.php(src)+");}finally{$wpdb->query('ROLLBACK');wp_cache_flush();}"
r=b13.b11.b10.b09.b08.c25.b06.profils.b00.wp('eval',code,check=False)
after=b13.c29.state()
b13.save(owner,sys.argv[1],{'native':r,'restored':before==after,'sources':owner.sources(owner)})
print(r);print('restored',before==after)
assert r['code']==0 and not r['stderr'] and before==after
