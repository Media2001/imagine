"""Read-only acceptance of the narrowly owned fictive prerequisite."""
from pathlib import Path
import importlib.util
import json
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('b04_work', HERE/'b04-work.py')
work = importlib.util.module_from_spec(spec)
spec.loader.exec_module(work)
work.guard()
result = work.wp(r'''
$f=get_option('imagine_b04_fixture',[]);$id=(int)($f['product']??0);$p=wc_get_product($id);
$checks=['produit_existe'=>$p instanceof WC_Product_Simple];
if($p){$checks += ['proprietaire'=>$p->get_meta('_imagine_b04_fixture',true,'edit')==='product-v1',
'publie'=>$p->get_status()==='publish','prix_zero'=>(float)$p->get_price()===0.0,
'virtuel'=>$p->is_virtual(),'pas_de_stock_reel'=>!$p->get_manage_stock(),
'natif_C14_numero11'=>Imagine\Site\AchatsNumeros::numero($p)===11,
'achetable'=>$p->is_purchasable()&&$p->is_in_stock(),'label_fictif'=>str_contains($p->get_name(),'FICTIF B04')];}
$checks['produit271_reste_prive']=get_post_status(271)==='private';
echo wp_json_encode(['total'=>count($checks),'checks'=>$checks,'failures'=>array_keys(array_filter($checks,static fn($v)=>$v!==true)),'product'=>$id]);
''')
phase=sys.argv[1] if len(sys.argv)>1 else 'final'
(work.PROOF/('fixture-'+phase+'.json')).write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
if result['failures']:raise SystemExit(1)
