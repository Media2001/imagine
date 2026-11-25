"""Read public/native schema sources only inside an A10-owned disposable runner."""
import importlib.util
import json
import pathlib
import sys
import uuid
sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('a02bench', ROOT / 'wp/tests/a02-audit/run.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
b.LABEL = 'org.imagine.a10-coupons'
name = 'imagine-a10-source-' + uuid.uuid4().hex[:12]
try:
    b.call(['create','--name',name,'--label',b.LABEL+'='+name,'--network','none','--no-healthcheck','--cap-drop','ALL','--security-opt','no-new-privileges','--entrypoint','sleep',b.IMAGE,'infinity'])
    b.validate(json.loads(b.call(['inspect',name]).stdout)[0],name)
    b.call(['start',name])
    b.call(['cp','/home/ced/staging-wp/plugins/woocommerce-subscriptions.zip',name+':/subscription.zip'])
    code = '''import zipfile, pathlib
z=zipfile.ZipFile('/subscription.zip')
for name in z.namelist():
 if name.endswith('.php') and ('coupon' in name.lower()):
  text=z.read(name).decode('utf8')
  lines=text.splitlines()
  for i,line in enumerate(lines):
   if any(k in line for k in ['_wcs_number_payments','recurring_percent','recurring_fee','sign_up_fee','get_discount_type(', 'wcs_get_coupon_property']):
    print(name+':'+str(i+1)+'\\n'+'\\n'.join(lines[max(0,i-2):i+4]))
p=pathlib.Path('/opt/woocommerce/woocommerce/includes/data-stores/class-wc-coupon-data-store-cpt.php')
print('COUPON STORE\\n'+p.read_text()[4000:11500])
p=pathlib.Path('/opt/woocommerce/woocommerce/includes/data-stores/class-wc-order-item-coupon-data-store.php')
print('ORDER COUPON STORE\\n'+p.read_text())
'''
    p=b.call(['exec','-i',name,'python3','-'],input_text=code)
    out=ROOT/'production/A-10/native-schema.txt'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(p.stdout,encoding='utf8')
    print(str(out))
finally:
    info=json.loads(b.call(['inspect',name]).stdout)[0]
    b.validate(info,name)
    b.call(['rm','-f',name])
    missing=b.call(['inspect',name],check=False)
    assert 'no such object' in missing.stderr.lower() or 'no such container' in missing.stderr.lower()
