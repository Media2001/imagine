"""C24 fusion : reçus frais, snapshot durable et readbacks métier."""
import sys
sys.dont_write_bytecode=True
import json,hashlib,runpy
import c24

def run(case,label,mutation=''):
    assert case in ['journal-question','journal-choix','newsletter']
    assert not (c24.PROOF/(label+'.json')).exists()
    identity=c24.guard()
    m=runpy.run_path(str(c24.ROOT/'wp/tests/demo/c24-http.py'))
    fixture=c24.wp('echo wp_json_encode(get_option("imagine_c09_fixture")["users"]);')
    ids=[fixture[k] for k in ['A-PAPIER','A-SEPA4','A-SANSMAIL','E-ADMIN']]
    source=c24.ROOT/'wp/tests/demo/c24-corrections.php';target='imagine-demo-build/c24-corrections.php'
    c24.profils.b00.upload(target,source.read_bytes())
    assert c24.hashes([target])[target]==hashlib.sha256(source.read_bytes()).hexdigest()
    before=m['snapshot'](ids);native=c24.state()
    private=c24.b06.private_snapshot(label,{'baseline':'recovered-new-explicit','snapshot':before,'native':native,'ids':ids})
    p=c24.profils.b00.wp('eval','$GLOBALS["imagine_c24_case"]='+json.dumps(case)+';$GLOBALS["imagine_c24_mutation"]='+json.dumps(mutation)+';require WP_CONTENT_DIR."/'+target+'";',check=False)
    try:r=json.loads(p['stdout'])
    except Exception:raise AssertionError({'code':p['code'],'stderr':p['stderr'],'stdout':p['stdout'][:1500]})
    after=m['snapshot'](ids)
    r.update(identity=identity,exit=p['code'],stderr=p['stderr'],state_preserved=c24.state()==native,all_business_rows_preserved=m['business_snapshot'](before)==m['business_snapshot'](after),private_snapshot=private,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),product_sources=c24.hashes(c24.NAMES[:-1]))
    c24.save(label,r);print(json.dumps(r,ensure_ascii=False))
    assert r['state_preserved'] and r['all_business_rows_preserved'] and not r['stderr']
    if mutation:
        expected={'restauration':'preimage_restauree_exacte','origine':'origine_defaut_creation'}[mutation]
        assert r['exit']==1 and expected in r['failures'] and r['mutation_replacements']==1
    else:assert r['exit']==0 and not r['failures']

if __name__=='__main__':run(*sys.argv[1:])
