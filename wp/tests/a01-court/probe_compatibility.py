"""Data-only commercial header check in an owned, network-none container."""
import hashlib
import json
from pathlib import Path
import sys
import uuid

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'wp/outils/staging-court'))
import publish


def main():
    output = ROOT / 'production/A-01/corrections-22nov' / ('compatibility-' + uuid.uuid4().hex[:12] + '.json')
    name = 'imagine-a01-publication-' + uuid.uuid4().hex[:12]
    result = {'status': 'FAIL', 'no_sites_created': True, 'no_php_or_plugin_bootstrap': True,
              'expected_production_core': '6.9.1', 'real_archive_opened': False}
    created = False
    try:
        sources = publish.fresh_runner(name)
        created = True
        result['isolation'] = publish.offline_isolation(name)
        for slug in ('woocommerce-memberships', 'woocommerce-subscriptions'):
            publish.call(['cp', '/home/ced/staging-wp/plugins/' + slug + '.zip', name + ':/opt/e2e/' + slug + '.zip'])
        program = r'''import hashlib,json,re,zipfile
from pathlib import Path
expected='6.9.1'
checksums={'woocommerce-subscriptions':'ed8c529d1382e2d06fa6e605e799c9db5607d8459806c229e74a20571f871083',
'woocommerce-memberships':'d3a858a8d6ebc7153248a10d665c6752948ea4fa8a1836d6bdd8a8f267ee3285'}
def header(text,label):
 m=re.search(r'^\s*\*?\s*'+label+r':\s*([0-9]+\.[0-9]+(?:\.[0-9]+)?)\s*$',text,re.M)
 return m[1] if m else None
def parts(v): return tuple(map(int,v.split('.')))+(0,)*(3-len(v.split('.')))
rows=[]
for slug,digest in checksums.items():
 package=Path('/opt/e2e/'+slug+'.zip')
 assert hashlib.sha256(package.read_bytes()).hexdigest()==digest
 with zipfile.ZipFile(package) as archive:
  text=archive.read(slug+'/'+slug+'.php').decode('utf-8')[:16384]
 minimum=header(text,'Requires at least')
 rows.append({'slug':slug,'package_sha256':digest,'version':header(text,'Version'),
  'requires_wordpress':minimum,'requires_woocommerce':header(text,'WC requires at least'),
  'compatible_with_expected_core':parts(expected)>=parts(minimum) if minimum else None})
woo=Path('/opt/woocommerce/woocommerce/woocommerce.php').read_text()[:16384]
minimum=header(woo,'Requires at least')
rows.append({'slug':'woocommerce','version':header(woo,'Version'),'requires_wordpress':minimum,
 'compatible_with_expected_core':parts(expected)>=parts(minimum) if minimum else None})
print(json.dumps({'plugins':rows,'runtime_core':re.search(r"^\$wp_version\s*=\s*'([0-9.]+)';",Path('/opt/wordpress/wordpress/wp-includes/version.php').read_text(),re.M)[1]}))
'''
        result.update(json.loads(publish.call(['exec', '-i', name, 'python3', '-'], program.encode()).stdout))
        result['source_manifest'] = sources
        result['status'] = 'HEADER_CHECK_COMPLETED_NOT_COMPATIBILITY_ACCEPTANCE'
        result['driver_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    finally:
        if created:
            result['cleanup'] = publish.remove_owned(name)
        output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': result['status'], 'report': str(output), 'plugins': result.get('plugins')}))
    return 0 if result['status'] != 'FAIL' else 1


if __name__ == '__main__':
    raise SystemExit(main())
