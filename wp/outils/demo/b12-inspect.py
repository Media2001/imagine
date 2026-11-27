import sys
sys.dont_write_bytecode=True
import b11
s=b11.wp("$s=file_get_contents(ABSPATH.'wp-includes/rest-api/class-wp-rest-server.php');$i=strpos($s,\"'rest_request_before_callbacks'\");echo wp_json_encode(substr($s,$i-400,4800));")
print(s)
