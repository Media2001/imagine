"""Témoin natif d'écriture B11 ; ne remplace pas la recette de l'éditeur livré."""
import sys
sys.dont_write_bytecode=True
import json
import b11

if __name__=='__main__':
    label=sys.argv[1]
    b11.guard();before=b11.state()
    source=(b11.ROOT/'wp/tests/demo/b11-write-witness.php').read_text(encoding='utf-8').split('<?php',1)[1]
    code='''global $wpdb;if(wp_using_ext_object_cache()){throw new RuntimeException('Cache externe refusé');}$wpdb->query('START TRANSACTION');try{eval('''+b11.php(source)+''');}finally{$wpdb->query('ROLLBACK');wp_cache_flush();}'''
    result=b11.wp(code)
    restored=b11.state()==before
    b11.save(label,{'native':result,'business_exactly_restored':restored,'sources':b11.sources()})
    print(json.dumps({'checks':len(result['checks']),'passed':sum(result['checks'].values()),'restored':restored,'boundary':result['boundary']}))
    assert restored and all(result['checks'].values())
