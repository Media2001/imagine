"""Mutation du scan B09, uniquement runner temporaire sur le site fictif."""
import sys
sys.dont_write_bytecode = True
import json
import b09
label = sys.argv[1]
b09.b08.c25.b06.guard()
before = b09.b08.snapshot()
business = b09.b08.c25.b06.state()
names = ['imagine-demo-build/b09-structure.php', 'imagine-demo-build/b09-seed.php']
assert b09.wp('$v=[];foreach(' + b09.php(names) + ' as $n){$v[]=file_exists(WP_CONTENT_DIR."/".$n);}echo wp_json_encode($v);') == [False, False]
source = (b09.ROOT / 'wp/outils/demo/b09-seed.php').read_text(encoding='utf-8')
assert source.count('foreach ($marked as $id)') == 1
mutant = source.replace('foreach ($marked as $id)', 'foreach ([] as $id)')
result = {}
try:
    b09.b08.c25.b06.profils.b00.upload(names[0], (b09.ROOT / 'wp/tests/demo/b09-structure.php').read_bytes())
    b09.b08.c25.b06.profils.b00.upload(names[1], mutant.encode())
    result = b09.wp('require WP_CONTENT_DIR."/' + names[0] + '";')
finally:
    b09.remove_remote(names)
    after = b09.b08.snapshot()
    restoration = {k: before[k] == after[k] for k in ['users', 'usermeta', 'posts', 'postmeta', 'navigation']}
    preserved = business == b09.b08.c25.b06.state()
    b09.save(label, {**result, 'restoration': restoration, 'business_preserved': preserved, 'runners_removed': True})
    assert all(restoration.values()) and preserved
failed = [k for k, v in result['checks'].items() if v is False]
assert set(failed) == {'marque_hors_option_refus_' + k for k in ['type', 'marqueur', 'doublon', 'rattachement_etranger']} | {'marqueurs_multiples_refuses'}, failed
print(json.dumps({'detected': True, 'failed_checks': failed, 'restored': True}, ensure_ascii=False))
