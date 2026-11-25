import importlib.util,pathlib,tempfile,unittest,zipfile
P=pathlib.Path('/subject/a04/update.py') if pathlib.Path('/subject').exists() else pathlib.Path(__file__).resolve().parents[2]/'outils/bascule/a04/update.py'
s=importlib.util.spec_from_file_location('a04_packages',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class PackageTests(unittest.TestCase):
    def package(self,root,text):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);p=pathlib.Path(self.tmp.name)/'fixture.zip'
        with zipfile.ZipFile(p,'w') as z:z.writestr(root,text)
        return p
    def test_archive_version_checked_before_copy(self):
        p=self.package('woocommerce/woocommerce.php','<?php\n/*\nVersion: 11.1.1\nRequires at least: 7.0\nRequires PHP: 8.2\n*/')
        self.assertEqual(m.package_metadata(p,'woocommerce')['version'],'11.1.1')
    def test_wrong_php_is_a_preflight_refusal(self):
        p=self.package('woocommerce/woocommerce.php','<?php\n/*\nVersion: 11.1.1\nRequires PHP: 8.3\n*/')
        with self.assertRaisesRegex(m.Refusal,'A04_PACKAGE_PHP'):m.check_package(p,'woocommerce','11.1.1','7.0.9','8.2.36')
    def test_wrong_wordpress_is_a_preflight_refusal(self):
        p=self.package('woocommerce/woocommerce.php','<?php\n/*\nVersion: 11.1.1\nRequires at least: 7.1\n*/')
        with self.assertRaisesRegex(m.Refusal,'A04_PACKAGE_WORDPRESS'):m.check_package(p,'woocommerce','11.1.1','7.0.9','8.2.36')
    def test_wrong_package_version_refused(self):
        p=self.package('woocommerce/woocommerce.php','<?php\n/*\nVersion: 11.0.1\n*/')
        with self.assertRaisesRegex(m.Refusal,'A04_PACKAGE_VERSION'):m.check_package(p,'woocommerce','11.1.1','7.0.9','8.2.36')
if __name__=='__main__':unittest.main(verbosity=2)
