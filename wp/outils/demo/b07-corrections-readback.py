"""Readback indépendant des corrections B07, aucune mutation ni session."""
import sys
sys.dont_write_bytecode=True
import json, os, hashlib, importlib.util
from pathlib import Path
import b07
spec=importlib.util.spec_from_file_location('b07_corrections',Path(__file__).with_name('b07-corrections.py'))
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
def run(label):
    identity=b07.b06.guard()
    install=json.loads((b07.PROOF/'correction2141-installation-V2.json').read_text(encoding='utf-8'))
    raw=(Path(os.environ['TMPDIR'])/install['private_snapshot']['file']).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==install['private_snapshot']['sha256']
    old=json.loads(raw)['payload'];now=b07.snapshot();actual=c.sources()
    checks={
        'sources_corrigees_relues_exactes':actual=={n:hashlib.sha256((b07.ROOT/'wp'/n).read_bytes()).hexdigest() for n in c.FILES},
        'etat_metier_exact_avant_installation':old['business']==c.business(),
        'evenements_et_metadonnees_anterieurs_exacts':all(old['database'][k]==now[k] for k in ['posts','meta']),
        'reglages_metier_exacts':old['database']['options']==now['options'],
        'aucune_inscription_essai':b07.wp('echo wp_json_encode(get_posts(["post_type"=>"imagine_inscription","post_status"=>"any","numberposts"=>-1,"fields"=>"ids"]));')==[],
        'observateur_et_option_absents':b07.wp('echo wp_json_encode(!file_exists(WP_CONTENT_DIR."/mu-plugins/b07-observer.php")&&get_option("imagine_b07_observer",null)===null);'),
    }
    content=(b07.ROOT/'wp/themes/imagine/functions.php').read_text(encoding='utf-8')
    contract=content.split('function imagine_partner_content(',1)[1].split("add_filter('the_content'",1)[0]
    data={'identity':identity,'checks':checks,'total':len(checks),'failures':[k for k,v in checks.items() if not v],'sources':actual,'filter_contract_sha256':hashlib.sha256(contract.encode()).hexdigest(),'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    b07.save(label,data);print(json.dumps(data,ensure_ascii=False));assert all(checks.values())
if __name__=='__main__':run(sys.argv[1])
