"""Corrections C22 : vrai WP-CLI transactionnel, cible gardée et reçus immuables."""
from pathlib import Path
import hashlib, json, sys
sys.dont_write_bytecode = True
import c22


def runtime(label, case):
    c22.profils.guard('imagine-test-demo')
    assert case in ('retired', 'history', 'utf8', 'privacy')
    assert not (c22.PROOF/(label+'.json')).exists()
    source = c22.ROOT/'wp/tests/demo/c22-corrections.php'
    target = 'imagine-demo-build/c22-corrections.php'
    c22.profils.b00.upload(target, source.read_bytes())
    assert c22.hashes([target])[target] == hashlib.sha256(source.read_bytes()).hexdigest()
    before = c22.state()
    own_options = '''global $wpdb;echo wp_json_encode($wpdb->get_results("SELECT * FROM {$wpdb->options} WHERE option_name IN ('imagine_newsletters_catalogue','imagine_newsletters_creation') OR option_name LIKE 'imagine_newsletters_reserve_%' ORDER BY option_id",ARRAY_A));'''
    prior = c22.wp(own_options)
    p = c22.profils.b00.wp('eval', '$GLOBALS["imagine_c22_case"]="'+case+'";require WP_CONTENT_DIR."/'+target+'";', check=False)
    try:
        data = json.loads(p['stdout'])
    except ValueError:
        data = {'failures':['runtime_output_invalid'], 'stdout':p['stdout']}
    data.update(exit=p['code'], stderr=p['stderr'], state_preserved=before==c22.state(), own_options_exact=prior==c22.wp(own_options), source_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
    c22.save(label, data)
    print(json.dumps(data, ensure_ascii=False))
    assert not data['failures'] and not data['exit'] and not data['stderr'] and data['state_preserved'] and data['own_options_exact']


if __name__ == '__main__':
    runtime(sys.argv[1], sys.argv[2])
