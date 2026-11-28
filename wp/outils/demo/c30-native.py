"""C30: transaction native + inverse ciblé des rapports WCS créés à shutdown."""
import sys
sys.dont_write_bytecode=True
import c30 as o
import b13
identity=o.guard();before=b13.c29.state()
def report_rows():return o.wp('global $wpdb;$a=$wpdb->get_results("SELECT * FROM {$wpdb->prefix}actionscheduler_actions WHERE hook=\'wcs_report_update_cache\' ORDER BY action_id",ARRAY_A);$ids=array_column($a,"action_id");$l=$ids?$wpdb->get_results("SELECT * FROM {$wpdb->prefix}actionscheduler_logs WHERE action_id IN (".implode(",",array_map("intval",$ids)).") ORDER BY log_id",ARRAY_A):[];echo wp_json_encode(["actions"=>$a,"logs"=>$l]);')
old=report_rows();private=b13.b11.private(sys.argv[1],old)
src=(o.ROOT/'wp/tests/demo/c30-runtime.php').read_text(encoding='utf-8').split('<?php',1)[1]
code='global $wpdb;$wpdb->query("START TRANSACTION");try{eval('+o.php(src)+');}finally{$wpdb->query("ROLLBACK");wp_cache_flush();}'
r=b13.b11.b10.b09.b08.c25.b06.profils.b00.wp('eval',code,check=False)
now=report_rows();a={x['action_id']:x for x in old['actions']};n={x['action_id']:x for x in now['actions']}
changed=[k for k in a.keys()|n.keys() if a.get(k)!=n.get(k)]
if changed:
    for key in changed:
        assert n.get(key,{}).get('hook','wcs_report_update_cache')=='wcs_report_update_cache'
        o.wp('global $wpdb;$id=' + str(int(key)) + ';$wpdb->delete($wpdb->prefix."actionscheduler_logs",["action_id"=>$id]);$wpdb->delete($wpdb->prefix."actionscheduler_actions",["action_id"=>$id]);echo wp_json_encode(true);')
        if key in a:o.wp('global $wpdb;$wpdb->insert($wpdb->prefix."actionscheduler_actions",'+o.php(a[key])+');foreach('+o.php([x for x in old['logs'] if x['action_id']==key])+ ' as $r){$wpdb->insert($wpdb->prefix."actionscheduler_logs",$r);}echo wp_json_encode(true);')
assert report_rows()==old
after=b13.c29.state()
b13.save(o,sys.argv[1],{'identity':identity,'native':r,'before':before,'after':after,'restored':before==after,'sources':o.sources(o),'private':private,'restored_report_actions':changed})
print({'native':r,'restored':before==after,'reports_restored':len(changed)})
assert r['code']==0 and not r['stderr'] and before==after
