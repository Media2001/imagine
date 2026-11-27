"""Assemble le paquet B09 corrigé, depuis preuves réelles, sans toucher l'historique."""
import sys
sys.dont_write_bytecode = True
import hashlib
import importlib.util
import json
import b09
spec = importlib.util.spec_from_file_location('b09_verifier', b09.PROOF / 'verifier.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
assert len(sys.argv) == 1
path = b09.PROOF / v.PACKET
assert not path.exists(), path
sources = b09.sources()
sources.pop('wp/themes/imagine/footer.php', None)
names = ['verifier.py', 'A-VOIR.md', 'NOTE.md', 'CORRECTIONS.md', 'sources-officielles.json', 'tests-finaux.log', 'mutations-finales.json', 'recette-finale.json', 'structure-finale-verifiee.json', 'pages-reprise-finale.json', 'reprise-stable-finale.json', 'readback-final.json', 'preparation-finale.json', 'preparation-finale.log', 'regression-finale.json', 'regression-finale.log']
names += ['mutations-finales-' + name + '.log' for name in sorted(v.MUTATIONS)]
names += ['corrections-red-partielle.log', 'corrections-red-seed.json', 'corrections-green-seed.json', 'corrections-effacement-natif.json', 'corrections-mutation-scan.json', 'corrections-final-mutant-meta.log']
artifacts = {}
for name in names:
    rel = v.RENAMES.get(v.PREFIX + name, v.PREFIX + name)
    artifacts[rel] = v.digest((b09.ROOT / rel).read_bytes())
def receipt(name):
    return v.load(b09.ROOT / v.RENAMES.get(v.PREFIX + name, v.PREFIX + name))
unit = v.junit((b09.ROOT / v.RENAMES[v.PREFIX + 'tests-finaux.log']).read_text(encoding='utf-8'))
reg = receipt('regression-finale.json')['results'][0]
readme = (b09.ROOT / 'wp/plugins/imagine-site/README.md').read_text(encoding='utf-8')
section = readme.split('## B-09 — FAQ, pages légales et contact', 1)[1].split('\n## ', 1)[0].strip()
counts = {'unit_tests': unit['tests'], 'unit_assertions': unit['assertions'], 'native_checks': len(receipt('recette-finale.json')['checks']) + len(receipt('structure-finale-verifiee.json')['checks']) + len(receipt('corrections-green-seed.json')['checks']) + len(receipt('corrections-effacement-natif.json')['checks']), 'source_mutations': len(receipt('mutations-finales.json')['mutations']) + 2, 'live_mutations': 2, 'global_tests': reg['tests'], 'global_assertions': reg['assertions'], 'global_tool_checks': reg['tools']['checks'], 'foreign_packet_failures': len(reg['packets']['failures'])}
packet = {'version': 2, 'scope': 'imagine-test-demo', 'sources': sources, 'artifacts': artifacts, 'readme_section_sha256': v.digest(section.encode()), 'counts': counts}
validated = v.validate(b09.ROOT, packet)
path.write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding='utf-8')
print('B09 PAQUET ' + json.dumps(validated, ensure_ascii=False, sort_keys=True))
