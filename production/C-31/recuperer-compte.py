"""Restauration bornée d'une recette Mon compte interrompue avant son reçu."""
import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'wp/outils/demo'))
import c31 as o
import b13
path = Path(sys.argv[1])
private = json.loads(path.read_text(encoding='utf-8'))
assert private['scope'] == 'imagine-test-demo' and private['label'].startswith('corrections-compte-')
raw = private['payload']
old = [r for r in raw['options'] if r['option_name'] == 'imagine_domaines_refuses']
maxid = max(int(r['option_id']) for r in raw['options'])
o.guard()
result = o.wp('global $wpdb;$wpdb->query("DELETE FROM {$wpdb->options} WHERE option_name LIKE \'imagine_reglages_journal_%\' AND option_id>' + str(maxid) + '");$wpdb->delete($wpdb->options,["option_name"=>"imagine_domaines_refuses"]);foreach(' + o.php(old) + ' as $r){$wpdb->insert($wpdb->options,$r);}wp_cache_flush();echo wp_json_encode(true);')
actual = o.wp('global $wpdb;echo wp_json_encode($wpdb->get_results("SELECT * FROM {$wpdb->options} WHERE option_name=\'imagine_domaines_refuses\' OR option_name LIKE \'imagine_reglages_journal_%\'",ARRAY_A));')
assert actual == raw['options']
b13.b11.b10.b09.remove_remote(['mu-plugins/c31-observer.php'])
assert o.wp('echo wp_json_encode(!file_exists(WP_CONTENT_DIR."/mu-plugins/c31-observer.php"));')
print('Réglage et journaux exactement restaurés, sonde retirée.')
