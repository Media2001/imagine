"""Installation idempotente de deux choix explicitement fictifs, avec journal C10 natif."""
import sys
sys.dont_write_bytecode=True
import c27
from importlib.util import spec_from_file_location,module_from_spec
spec=spec_from_file_location('native',c27.ROOT/'wp/outils/demo/c27-native.py');native=module_from_spec(spec);spec.loader.exec_module(native)
identity=c27.guard();saved=c27.snapshot();business=c27.state()
durable=c27.private('c27-seed',{'database':saved,'business':business})
choices={'lune':'Radio fictive \\ lune','mars':'Journal martien fictif'}
old=c27.wp('echo wp_json_encode(get_option(Imagine\\Site\\Acquisition::OPTION,null));')
assert old in [None,choices], 'Liste étrangère : aucun écrasement'
for unused in range(2):
    actual=c27.wp('update_option(Imagine\\Site\\Acquisition::OPTION,'+c27.php(choices)+',false);echo wp_json_encode(Imagine\\Site\\Acquisition::configuration());')
    assert actual==choices
current=c27.snapshot();exact=native.compare(saved,current)
assert all(v for k,v in exact.items() if k!='options_metier')
prior={r['option_name']:r for r in saved['options']}
added=[r for r in current['options'] if r['option_name'] not in prior and r['option_name'].startswith('imagine_')]
assert (old is None and len(added)==2) or (old==choices and not added)
for row in added:
    if row['option_name']=='imagine_acquisition_choix':continue
    event=c27.wp('echo wp_json_encode(get_option('+c27.php(row['option_name'])+'));')
    assert event['option']=='imagine_acquisition_choix' and event['avant'] is None and event['apres']==choices
volatile={'_transient_timeout_wcs_woocommerce_active_version'}
untouched=lambda data:[r for r in data['options'] if r['option_name'] in prior and r['option_name'] not in volatile]
assert untouched(saved)==untouched(current)
c27.save(sys.argv[1],{'identity':identity,'private_snapshot':durable,'choices':actual,'idempotent':True,'existing_nonvolatile_options_preserved':True,'volatile_options_excluded':sorted(volatile),'restoration_except_new_setting':exact,'added_business_options':len(added),'business_preserved':business==c27.state()})
print('Deux choix fictifs relus, deux rejeux identiques ; aucune commande, profil ou action changé.')
