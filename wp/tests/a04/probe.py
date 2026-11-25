import pathlib, re, zipfile
for root in ['/opt/wordpress/wordpress', '/opt/woocommerce/woocommerce']:
    p=pathlib.Path(root)/('wp-includes/version.php' if 'wordpress' in root else 'woocommerce.php')
    print(str(p),re.findall(r"(?:\$wp_version\s*=\s*'([^']+)'|Version:\s*([^\r\n]+))",p.read_text())[:2])
for f in pathlib.Path('/opt/a04').glob('*.zip'):
    with zipfile.ZipFile(f) as z:
        print(f.name)
        for n in z.namelist():
            if n.endswith('.php') and ('class-wcs-upgrade' in n or 'class-wc-subscriptions-upgrade' in n or 'class-wc-memberships-upgrade' in n or 'class-upgrade.php' in n or 'woocommerce-subscriptions.php' in n or 'woocommerce-memberships.php' in n):
                s=z.read(n).decode(errors='replace')
                print(n, {'sha256':__import__('hashlib').sha256(s.encode()).hexdigest(), 'methods': re.findall(r'public (?:static )?function ([A-Za-z0-9_]+)', s), 'requirements':re.findall(r'Requires (?:at least|PHP):[^\\r\\n]+',s)})
