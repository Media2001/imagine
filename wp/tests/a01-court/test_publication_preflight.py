"""Read-only publication diagnosis; no site lifecycle or archive I/O."""
import importlib.util
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True
MODULE = Path(__file__).resolve().parents[2] / 'outils/staging-court/publication_preflight.py'
spec = importlib.util.spec_from_file_location('publication_preflight', MODULE)
preflight = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preflight)


def fixture():
    return {
        'create_fields': ['name', 'template_slug', 'php_version', 'client_name', 'target_domain'],
        'create_required': ['name', 'template_slug'],
        'functions': {
            'create_site': 'def create_site():\n    template = get_template(template_slug)\n',
            '_provision_site': 'def _provision_site():\n'
                              '    premium_zips = list(dict.fromkeys([*template["premium_zips"], *_MCP_PLATFORM_ZIPS]))\n'
                              '    if config.NOVAMIRA_PRO_LICENSE:\n'
                              '        activate_novamira_pro_license(site, config.NOVAMIRA_PRO_LICENSE)\n'
                              '    provision_mcp(site)\n',
            'provision_mcp': 'def provision_mcp():\n    enable_novamira_abilities(site)\n'
                             '    create_mcp_credentials(site)\n    validate_mcp_connection(site)\n',
        },
        'platform_zips': ['novamira.zip', 'novamira-pro.zip'],
        'novamira_zip_present': True,
        'novamira_pro_zip_present': True,
        'novamira_license_configured': True,
    }


class PublicationPreflightTest(unittest.TestCase):
    def test_configured_real_license_blocks_normal_creation(self):
        result = preflight.assess(fixture())
        self.assertIn('NORMAL_CREATE_ACTIVATES_CONFIGURED_NOVAMIRA_LICENSE', result['issues'])
        self.assertFalse(result['full_staging_ready'])
        self.assertEqual('BLOCKED', result['status'])

    def test_mcp_provisioning_is_separate_blocker(self):
        data = fixture()
        data['novamira_license_configured'] = False
        result = preflight.assess(data)
        self.assertNotIn('NORMAL_CREATE_ACTIVATES_CONFIGURED_NOVAMIRA_LICENSE', result['issues'])
        self.assertIn('NORMAL_CREATE_PROVISIONS_NOVAMIRA_MCP', result['issues'])

    def test_missing_commercial_package_does_not_claim_license_activation(self):
        data = fixture()
        data['novamira_pro_zip_present'] = False
        self.assertNotIn('NORMAL_CREATE_ACTIVATES_CONFIGURED_NOVAMIRA_LICENSE', preflight.assess(data)['issues'])

    def test_creation_has_no_current_bypass_field(self):
        self.assertIn('CREATE_API_HAS_NO_EMPTY_WITHOUT_MCP_BYPASS', preflight.assess(fixture())['issues'])

    def test_source_drift_is_not_an_authorization(self):
        data = fixture()
        data['functions'] = {}
        result = preflight.assess(data)
        self.assertEqual('REVIEW_REQUIRED', result['status'])
        self.assertFalse(result['full_staging_ready'])

    def test_future_api_field_requires_new_review(self):
        data = fixture()
        data['create_fields'].append('skip_mcp')
        result = preflight.assess(data)
        self.assertNotIn('CREATE_API_HAS_NO_EMPTY_WITHOUT_MCP_BYPASS', result['issues'])
        self.assertFalse(result['full_staging_ready'])

    def test_no_source_or_environment_values_leak_from_assessment(self):
        data = fixture()
        data['unknown_environment_value'] = 'must-not-escape'
        self.assertNotIn('must-not-escape', str(preflight.assess(data)))


if __name__ == '__main__':
    unittest.main(verbosity=2)
