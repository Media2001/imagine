"""Diagnostic en lecture : variations de métadonnées UI après connexion native."""
from pathlib import Path
import sys
import json
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import construire as m
p = m.ROOT / 'production/B-00/tests'
s = Path(__file__).with_name('b00-integre-snapshot.php').read_text(encoding='utf-8')
s = s.replace('$meta = get_user_meta($id);', '$meta = get_user_meta($id); foreach(($GLOBALS["imagine_b00_ui_ignore"][$key] ?? []) as $field){unset($meta[$field]);}')
m.upload('imagine-demo-build/b00-ui-meta-diagnostic.php', s.encode())
code = '''$found=[];$fields=[['E-ADMIN','_woocommerce_tracks_anon_id'],['E-ADMIN','_wc_plugin_framework_memberships_dismissed_messages'],['E-REDAC','_woocommerce_tracks_anon_id'],['E-ABO','_woocommerce_tracks_anon_id']];for($mask=0;$mask<16;$mask++){$GLOBALS['imagine_b00_ui_ignore']=[];foreach($fields as $i=>[$k,$f]){if($mask & (1<<$i)){$GLOBALS['imagine_b00_ui_ignore'][$k][]=$f;}}ob_start();require WP_CONTENT_DIR . '/imagine-demo-build/b00-ui-meta-diagnostic.php';$d=json_decode(ob_get_clean(),true);$found[$mask]=$d['c09']['users_sha256'];}echo wp_json_encode($found);'''
actual = json.loads(m.wp('eval', code)['stdout'])
old = json.loads((p/'b00-integre-avant.json').read_text(encoding='utf-8'))['c09']['users_sha256']
matches = [i for i, value in enumerate(actual) if value == old]
print('Exact original identity/metadata hash matches masks:', matches)
(p/'b00-ui-meta-diagnostic.json').write_text(json.dumps({'masks_matching_original': matches, 'hashes': actual}), encoding='utf-8')
