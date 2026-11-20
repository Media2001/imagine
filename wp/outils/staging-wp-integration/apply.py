#!/usr/bin/env python3
"""Apply a source-only overlay to an explicit isolated staging-wp tool copy.
No Docker, Git, data read, migration, shared restart or dependency installation.
Checks EVERY preimage before writing anything; backup each edited source once.
"""
import argparse
import ast
import json
import shutil
from pathlib import Path

EDITS = {
 'api/models.py': [
  ('    status TEXT NOT NULL DEFAULT \'creating\',', '    status TEXT NOT NULL DEFAULT \'creating\',\n    verification_state TEXT NOT NULL DEFAULT \'none\','),
  ('    if "php_version" not in cols:', '    if "verification_state" not in cols:\n        conn.execute("ALTER TABLE sites ADD COLUMN verification_state TEXT NOT NULL DEFAULT \'none\'")\n    if "php_version" not in cols:'),
 ],
 'api/orchestrator.py': [
  ('    template = get_template(template_slug)\n    php_version', '    template = get_template(template_slug)\n    if template.get("category") == "subscriptions":\n        raise ValueError("Profil abonnements : utiliser la commande opérateur hors-ligne")\n    php_version'),
 ],
 'api/main.py': [
  ('from . import config, mcp_proxy, models, orchestrator, unlimited_extension', 'from . import config, mcp_proxy, models, orchestrator, unlimited_extension, subscriptions, subscription_guards'),
  ('app.add_middleware(unlimited_extension.MutationGuard)', 'app.add_middleware(unlimited_extension.MutationGuard)\napp.add_middleware(subscription_guards.MutationGuard)'),
  ('    status: str\n    notes: str', '    status: str\n    verification_state: str = "none"\n    verification_report: dict | None = None\n    notes: str'),
  ('    url = f"http://{config.NAS_HOST}:{site[\'port\']}"', '    locked = subscriptions.is_subscription(site) and site.get("verification_state") != "verified"\n    url = "" if locked else f"http://{config.NAS_HOST}:{site[\'port\']}"'),
  ('        status=site["status"],', '        status=site["status"],\n        verification_state=site.get("verification_state", "none"),\n        verification_report=subscriptions.public_report(site),'),
  ('        admin_url=f"{url}/wp-admin/",', '        admin_url=f"{url}/wp-admin/" if url else "",'),
  ('        mcp_enabled=bool(site.get("mcp_enabled", False)),', '        mcp_enabled=False if locked else bool(site.get("mcp_enabled", False)),'),
  ('        mcp_status=site.get("mcp_status", "disabled"),', '        mcp_status="disabled" if locked else site.get("mcp_status", "disabled"),'),
  ('        mcp_tool_count=site.get("mcp_tool_count", 0),', '        mcp_tool_count=0 if locked else site.get("mcp_tool_count", 0),'),
  ('        wp_admin_user=site.get("wp_admin_user"),', '        wp_admin_user=None if locked else site.get("wp_admin_user"),'),
  ('    php_version: str = Form("8.3"),\n    file:', '    php_version: str = Form("8.3"),\n    profile: str = Form("imported"),\n    file:'),
  ('    if not file.filename or not file.filename.endswith(".wpress"):', '    if profile != "imported":\n        raise HTTPException(423, "Profil abonnements : commande hors-ligne obligatoire")\n    if not file.filename or not file.filename.endswith(".wpress"):'),
 ],
 'api/site_management.py': [
  ('from . import config, models, orchestrator', 'from . import config, models, orchestrator, subscriptions'),
  ('    site = models.get_site(site_slug)\n    credentials', '    site = models.get_site(site_slug)\n    subscriptions.require_verified(site)\n    credentials'),
 ],
 'api/mcp_client.py': [
  ('from . import models, orchestrator', 'from . import models, orchestrator, subscriptions'),
  ('    site = models.get_site(site_slug)\n    credentials', '    site = models.get_site(site_slug)\n    subscriptions.require_verified(site)\n    credentials'),
 ],
 'api/mcp_proxy.py': [
  ('from . import mcp_client, models, site_management', 'from . import mcp_client, models, site_management, subscriptions'),
  ('            "port": site["port"],', '            "port": None if subscriptions.is_subscription(site) and site.get("verification_state") != "verified" else site["port"],\n            "verification_state": site.get("verification_state", "none"),'),
 ],
 'api/unlimited_extension.py': [
  ('def protected(site: dict) -> bool:\n    return bool(', 'def protected(site: dict) -> bool:\n    if site.get("profile") == "subscriptions":\n        return True\n    return bool('),
  ('def wp(site: dict, *args: str) -> str:\n    return command(', 'def wp(site: dict, *args: str) -> str:\n    if site.get("profile") == "subscriptions":\n        raise SafeError("Profil abonnements : maintenance historique interdite")\n    return command('),
 ],
}
APPENDS = {
 'api/models.py': '''\n\ndef set_verification(slug: str, state: str) -> None:
    if state not in {"quarantined", "imported", "verified"}:
        raise ValueError("État de vérification invalide")
    with get_conn() as conn:
        conn.execute("UPDATE sites SET verification_state = ? WHERE slug = ? AND profile = 'subscriptions'", (state, slug))
''',
 'api/orchestrator.py': '\n\n# Subscription imports never enter the historical web-first lifecycle.\nfrom .subscription_guards import install_guards as _install_subscription_guards\n_install_subscription_guards(globals())\n',
}
PROFILE = dict(slug='import-subscriptions', name='Site à abonnements — import hors-ligne',
               category='subscriptions', import_only=True, icon='Shield',
               description='Neutralisation, anonymisation, vérification avant tout accès web ou agent.',
               default_php='8.3', free_plugins=[], premium_zips=[], theme=None)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('tool_copy', type=Path)
    parser.add_argument('--apply', action='store_true', help='default: validate only')
    args = parser.parse_args()
    root = args.tool_copy.resolve()
    results = {}
    for relative, edits in EDITS.items():
        path = root / relative
        text = path.read_text()
        for old, new in edits:
            if text.count(old) != 1:
                raise SystemExit(f'Preimage incompatible: {relative}; aucun fichier écrit')
            text = text.replace(old, new, 1)
        text += APPENDS.get(relative, '')
        ast.parse(text, filename=relative)
        results[relative] = text
    relative = 'api/templates/templates.json'
    profiles = json.loads((root / relative).read_text())
    if any(t['slug'] == PROFILE['slug'] for t in profiles['templates']):
        raise SystemExit('Profil déjà présent; aucun fichier écrit')
    profiles['templates'].append(PROFILE)
    results[relative] = json.dumps(profiles, ensure_ascii=False, indent=2) + '\n'
    overlay = Path(__file__).resolve().parent / 'overlay'
    for source in sorted(overlay.glob('api/*.py')):
        relative = source.relative_to(overlay).as_posix()
        if (root / relative).exists():
            raise SystemExit(f'Cible overlay déjà présente: {relative}; aucun fichier écrit')
        text = source.read_text()
        ast.parse(text, filename=relative)
        results[relative] = text
    for relative in results:
        path = root / relative
        if path.is_symlink() or path.with_name(path.name + '.pre-subscriptions').exists():
            raise SystemExit('Lien ou sauvegarde source existante; aucun fichier écrit')
    if not args.apply:
        print(json.dumps({'validated': sorted(results), 'written': False}))
        return
    for relative, text in results.items():
        path = root / relative
        if path.exists():
            backup = path.with_name(path.name + '.pre-subscriptions')
            if backup.exists():
                raise SystemExit('Sauvegarde source existante; arrêt sans écrasement')
            shutil.copyfile(path, backup)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    print(json.dumps({'written': sorted(results), 'data_touched': False, 'restart': False}))


if __name__ == '__main__':
    main()
