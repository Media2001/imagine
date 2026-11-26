"""Rejeu C21 fusion, cible fictive unique ; reçus append-only."""
from pathlib import Path
import hashlib, json, sys
sys.dont_write_bytecode = True
import c21

def run(label):
    c21.c19.c18.c17.profils.guard('imagine-test-demo')
    before = c21.c19.c18.state()
    scheduled = c21.schedule_business()
    name = 'imagine-demo-build/c21-fusion-native.php'
    source = c21.ROOT / 'wp/tests/demo/c21-fusion-native.php'
    c21.c19.c18.c17.profils.b00.upload(name, source.read_bytes())
    assert c21.hashes([name])[name] == hashlib.sha256(source.read_bytes()).hexdigest()
    result = c21.wp('require WP_CONTENT_DIR."/' + name + '";')
    after = c21.c19.c18.state()
    for state in (before, after):
        for key in ('actionscheduler_actions', 'actionscheduler_logs'):
            state['native_fingerprints'].pop(key, None)
    result['checks']['profils_C09_et_actions_exacts'] = before == after and scheduled == c21.schedule_business()
    result['total'] = len(result['checks'])
    result['failures'] = [k for k, v in result['checks'].items() if v is not True]
    result['source_sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
    c21.save(label, result)
    return int(bool(result['failures']))

if __name__ == '__main__':
    sys.exit(run(sys.argv[1]))
