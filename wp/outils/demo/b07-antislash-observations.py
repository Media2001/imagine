"""Termine seulement l'observation native, sans rejouer les quatre parcours acquis."""
import sys
sys.dont_write_bytecode = True
import importlib.util
import json
import hashlib
import subprocess
from pathlib import Path

spec = importlib.util.spec_from_file_location('b07_native', Path(__file__).with_name('b07-antislash-native.py'))
n = importlib.util.module_from_spec(spec)
spec.loader.exec_module(n)
c27 = n.c27


def run():
    path = n.PROOF/'antislash-observation-native.json'
    assert not path.exists()
    prior = json.loads((n.PROOF/'antislash-native.json').read_text(encoding='utf-8'))
    assert len(prior['cases']) == 4 and all(prior['restoration'].values()) and prior['business_preserved']
    assert all(prior['cleanup'].values()) and prior['native_red']['http'] == 400
    identity = c27.guard()
    before = c27.snapshot()
    business = c27.state()
    durable = c27.private('b07-observation-native', {'database': before, 'business': business})
    email = 'b07-antislash-observation@example.org'
    assert c27.wp('echo wp_json_encode(Imagine\\Site\\Agenda::inscriptions('+c27.php(email)+'));') == []
    assert c27.wp('$v=[];foreach('+c27.php([n.OBSERVER,n.TRACE])+' as $p){$v[]=file_exists(WP_CONTENT_DIR."/".$p);}echo wp_json_encode($v);') == [False,False]
    result = {'identity':identity, 'private_snapshot':durable,
              'sources': {p:hashlib.sha256((n.ROOT/p).read_bytes()).hexdigest() for p in ['wp/outils/demo/b07-antislash-observations.py','wp/tests/demo/b07-antislash-observer.php']},
              'prior_native_receipt_sha256':hashlib.sha256((n.PROOF/'antislash-native.json').read_bytes()).hexdigest()}
    try:
        c27.upload(n.TRACE,b'')
        p='/app/sites/imagine-test-demo/wp-content/'+n.TRACE
        subprocess.run(['wsl.exe','-d','Ubuntu','--','docker','exec','staging-wp-dashboard','python','-c','from pathlib import Path;Path('+repr(p)+').chmod(0o666)'],check=True,capture_output=True)
        c27.upload(n.OBSERVER,(n.ROOT/'wp/tests/demo/b07-antislash-observer.php').read_bytes())
        code,_,body=n.http(prior['fixture']['url'])
        assert code==200 and 'imagine-agenda-inscription' in body
        parser=n.Inputs();parser.feed(body)
        values={'action':'imagine_agenda','evenement':str(prior['fixture']['id']),'imagine_agenda_nonce':parser.inputs['imagine_agenda_nonce'],'nom':'Fictif \\ Observation','email':email,'consentement':'1'}
        codes=[]
        for _ in range(2):
            code,_,_=n.http(identity['url']+'/wp-admin/admin-post.php',values)
            codes.append(code)
            assert code==303
        result['post_codes']=codes
        result['unique_registration']=len(c27.wp('echo wp_json_encode(Imagine\\Site\\Agenda::inscriptions('+c27.php(email)+'));'))==1
        raw=c27.wp('echo wp_json_encode(file_get_contents(WP_CONTENT_DIR."/'+n.TRACE+'"));')
        rows=[json.loads(line) for line in raw.splitlines()]
        result['observations']={'rows':rows,'requests':len(rows)}
        def quiet(items):
            return bool(items) and all(all(row[k] == 0 for k in ['mail','http_agenda','http_autre','transport_mail','transport_http'])
                                       and row['http'] == row['http_infrastructure'] for row in items)
        assert quiet(rows)
        mutations = {}
        for key in ['mail','http_agenda','http_autre','transport_mail','transport_http']:
            changed = [dict(row) for row in rows]
            changed[0][key] = 1
            mutations[key] = not quiet(changed)
        assert all(mutations.values())
        result['absence_mutations_detected'] = mutations
        result['checks_passed']=True
    finally:
        c27.wp('foreach(Imagine\\Site\\Agenda::inscriptions('+c27.php(email)+') as $id){wp_delete_post($id,true);}echo wp_json_encode(true);')
        c27.b09.remove_remote([n.OBSERVER])
        c27.b09.remove_remote([n.TRACE])
        after=c27.snapshot()
        exact={k:before[k]==after[k] for k in before if k!='options'}
        opts=lambda d:[r for r in d['options'] if r['option_name'].startswith('imagine_') or r['option_name']=='cron']
        exact['options_metier']=opts(before)==opts(after)
        absent=c27.wp('$v=[];foreach('+c27.php([n.OBSERVER,n.TRACE])+' as $p){$v[]=!file_exists(WP_CONTENT_DIR."/".$p);}echo wp_json_encode($v);')
        result.update(restoration=exact,business_preserved=business==c27.state(),temporary_files_absent=absent,
                      registrations_removed=c27.wp('echo wp_json_encode(Imagine\\Site\\Agenda::inscriptions('+c27.php(email)+'));')==[])
        path.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps(result,ensure_ascii=False))
        assert all(exact.values()) and result['business_preserved'] and all(absent) and result['registrations_removed']
    assert result['checks_passed'] and result['unique_registration']


if __name__=='__main__':
    run()
