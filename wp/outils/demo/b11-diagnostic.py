import sys,json
sys.dont_write_bytecode=True
sys.path.insert(0,str(__import__('pathlib').Path(__file__).resolve().parents[3]/'wp/outils/demo'))
import b11
print(json.dumps(b11.wp('''$u=get_option('imagine_c09_fixture')['users'];$o=[];foreach(['A-CARTE','A-SEPA4','P-NUMERO'] as $key){wp_set_current_user((int)$u[$key]);foreach([11,18,25,32,39] as $id){$o[$key][$id]=Imagine\\Site\\Paywall::decisionPdf(get_post($id));}}echo wp_json_encode($o);'''),ensure_ascii=False))
