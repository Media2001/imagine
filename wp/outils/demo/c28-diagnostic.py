import sys
sys.dont_write_bytecode=True
import c28
print(c28.wp("global $wpdb;$a=$wpdb->prefix.'actionscheduler_actions';$l=$wpdb->prefix.'actionscheduler_logs';echo wp_json_encode(['actions'=>$wpdb->get_results(\"SELECT action_id,hook,status,scheduled_date_gmt,args,attempts,claim_id FROM $a WHERE hook<>'wcs_report_update_cache' ORDER BY action_id DESC LIMIT 12\",ARRAY_A),'logs'=>$wpdb->get_results(\"SELECT l.* FROM $l l INNER JOIN $a a ON a.action_id=l.action_id WHERE a.hook<>'wcs_report_update_cache' ORDER BY l.log_id DESC LIMIT 12\",ARRAY_A),'comingsoon'=>glob(WP_PLUGIN_DIR.'/woocommerce/src/Internal/ComingSoon/*')]);"))
