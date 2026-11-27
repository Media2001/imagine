"""Assemble le paquet B09 final depuis les vrais reçus ; ne crée pas PRET."""
import sys
sys.dont_write_bytecode=True
import hashlib
import importlib.util
import json
import b09
spec=importlib.util.spec_from_file_location('b09_verifier',b09.PROOF/'verifier.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
assert len(sys.argv)==1
path=b09.PROOF/'final-V2.json'
assert not path.exists(),path
sources=b09.sources();sources.pop('wp/themes/imagine/footer.php',None)
names=['verifier.py','A-VOIR.md','NOTE.md','sources-officielles.json','tests-finaux.log','mutations-finales.json','recette-finale.json','structure-finale-verifiee.json','pages-reprise-finale.json','reprise-stable-finale.json','readback-final.json','preparation-finale.json','preparation-finale.log','regression-finale.json','regression-finale.log','red-contact.log','red-structure.json','red-seed-stable.json']
names += ['mutations-finales-'+name+'.log' for name in sorted(v.MUTATIONS)]
artifacts={p.relative_to(b09.ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [b09.PROOF/n for n in names]}
r=v.load(b09.PROOF/'recette-finale.json');s=v.load(b09.PROOF/'structure-finale-verifiee.json');seed=v.load(b09.PROOF/'pages-reprise-finale.json')
unit=v.junit((b09.PROOF/'tests-finaux.log').read_text(encoding='utf-8'))
reg=v.load(b09.PROOF/'regression-finale.json')['results'][0]
mut=v.load(b09.PROOF/'mutations-finales.json')
readme=(b09.ROOT/'wp/plugins/imagine-site/README.md').read_text(encoding='utf-8')
section=readme.split('## B-09 — FAQ, pages légales et contact',1)[1].split('\n## ',1)[0].strip()
packet={'version':1,'scope':'imagine-test-demo','sources':sources,'artifacts':artifacts,'readme_section_sha256':v.digest(section.encode()),'counts':{'unit_tests':unit['tests'],'unit_assertions':unit['assertions'],'native_checks':len(r['checks'])+len(s['checks'])+len(seed['checks']),'source_mutations':len(mut['mutations']),'live_mutations':1,'global_tests':reg['tests'],'global_assertions':reg['assertions'],'global_tool_checks':reg['tools']['checks'],'foreign_packet_failures':len(reg['packets']['failures'])}}
counts=v.validate(b09.ROOT,packet)
path.write_text(json.dumps(packet,ensure_ascii=False,indent=2),encoding='utf-8')
# Relire le paquet exact produit, avant toute annonce de succès.
assert v.validate(b09.ROOT,v.load(path))==counts
print('B09 PAQUET '+json.dumps(counts,ensure_ascii=False,sort_keys=True))
