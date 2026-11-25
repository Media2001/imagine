import pathlib, re, zipfile
p=pathlib.Path('/opt/woocommerce/woocommerce/includes/class-wc-install.php')
s=p.read_text()
print('WOO_PUBLIC_UPDATE_METHODS',re.findall(r'public static function ([A-Za-z0-9_]+)',s))
for match in re.finditer('VariationGallery',s):print('WOO_NATIVE_CALLBACK_DECLARATION',s[max(0,match.start()-180):match.start()+220])
for match in re.finditer('woocommerce_run_update_callback',s):print('WOO_QUEUE_DEFINITION',s[max(0,match.start()-280):match.start()+420])
for marker in ['public static function run_update_callback','public static function get_db_update_callbacks']:
    start=s.find(marker)
    print('WOO_UPDATE_IMPLEMENTATION',s[start:start+2600])
for root in ['/opt/wordpress/wordpress', '/opt/woocommerce/woocommerce']:
    p=pathlib.Path(root)/('wp-includes/version.php' if 'wordpress' in root else 'woocommerce.php')
    print(str(p),re.findall(r"(?:\$wp_version\s*=\s*'([^']+)'|Version:\s*([^\r\n]+))",p.read_text())[:2])
for f in pathlib.Path('/opt/a04').glob('*.zip'):
    with zipfile.ZipFile(f) as z:
        print(f.name)
        for n in z.namelist():
            if n.endswith('.php') and ('class-wcs-upgrade' in n or 'batch-processing' in n or 'batch-processor' in n or 'class-wc-subscriptions-upgrade' in n or 'class-wc-memberships-upgrade' in n or 'class-upgrade.php' in n or 'woocommerce-subscriptions.php' in n or 'woocommerce-memberships.php' in n):
                s=z.read(n).decode(errors='replace')
                print(n, {'sha256':__import__('hashlib').sha256(s.encode()).hexdigest(), 'methods': re.findall(r'public (?:static )?function ([A-Za-z0-9_]+)', s), 'requirements':re.findall(r'Requires (?:at least|PHP):[^\\r\\n]+',s)})
        if 'memberships' in f.name:
            for n in z.namelist():
                if n.endswith('.php'):
                    text=z.read(n).decode(errors='replace')
                    if 'function get_lifecycle' in text or 'class Lifecycle' in text:
                        print('MEMBERSHIPS_LIFECYCLE_API',n,re.findall(r'public (?:static )?function ([A-Za-z0-9_]+)',text))
                        print('MEMBERSHIPS_METHOD_SIGNATURES',[line.strip() for line in text.splitlines() if 'public function init(' in line or 'function get_lifecycle_handler(' in line])
