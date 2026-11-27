"""Scelle les seules preuves finales C27 ; ne lance ni site, ni Git, ni verrou."""
import sys
sys.dont_write_bytecode=True
import importlib.util,json,hashlib
import c27
spec=importlib.util.spec_from_file_location('verify',c27.PROOF/'verifier.py');verify=importlib.util.module_from_spec(spec);spec.loader.exec_module(verify)
NAMES={'unit':'unitaire-final.json','native':'native-final.json','recipe':'recette-finale.json','mutations':'mutations-finales.json','prepare':'preparation-finale.json','regression':'regression-finale.json','seed':'liste-demo.json','readback':'readback-final.json','style':'style-final.json'}
if len(sys.argv)!=1:raise SystemExit('Aucun argument attendu')
path=c27.PROOF/'final-V2.json';assert not path.exists(),path
files={'verifier.py','A-VOIR.md','NOTE.md','sources-officielles.json',*NAMES.values()}
for key,name in NAMES.items():
    if key=='style':continue
    d=verify.load(c27.PROOF/name)
    if 'log' in d:files.add(d['log'])
    for row in d.get('mutations',[]):files.add(row['log'])
result=verify.load(c27.PROOF/NAMES['regression'])['results'][0]
packet={'scope':'imagine-test-demo','version':1,'sources':c27.sources(),'artifacts':{'production/C-27/'+n:verify.digest((c27.PROOF/n).read_bytes()) for n in sorted(files)},'receipts':NAMES,'readme_section_sha256':verify.digest((c27.ROOT/'wp/plugins/imagine-site/README.md').read_text(encoding='utf-8').split(verify.HEADER,1)[1].split('\n## ',1)[0].strip().encode()),'counts':{'unit_tests':7,'unit_assertions':55,'native_checks':len(verify.NATIVE)+len(verify.RECIPE),'source_mutations':8,'live_mutations':2,'global_tests':result['tests'],'global_assertions':result['assertions'],'tool_checks':result['tools']['checks'],'foreign_packet_failures':len(result['packets']['failures'])}}
counts=verify.validate(c27.ROOT,packet)
path.write_text(json.dumps(packet,ensure_ascii=False,indent=2),encoding='utf-8')
print('C27 paquet vérifié et scellé '+json.dumps(counts,ensure_ascii=False))
