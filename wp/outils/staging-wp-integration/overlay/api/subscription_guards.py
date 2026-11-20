"""Subscription-only guards for every historical lifecycle and ASGI route."""
import functools
import inspect
from . import models, subscriptions as s


def install_guards(namespace):
    deny = {'_render_compose', '_provision_site', 'run_create_task', 'change_php_version',
            'clone_site', 'run_clone_task', '_do_clone', 'run_import_wpress_task',
            '_do_import_wpress', 'destroy_site'}
    guarded = deny | {'mcp_connection', 'enable_novamira_abilities', 'create_mcp_credentials',
                      'resolve_mcp_admin_user', 'activate_novamira_pro_license',
                      'validate_mcp_connection', 'provision_mcp', 'adopt_mcp', '_wp', '_compose',
                      'read_theme_file', 'write_theme_file', 'list_admins', 'magic_login_url',
                      'export_wpress', 'start_site', 'stop_site', '_wait_for_wp', '_wait_for_db',
                      '_install_import_unlimited'}
    def wrap(name, fn):
        @functools.wraps(fn)
        def guarded_call(*args, **kwargs):
            signature = inspect.signature(fn)
            bound = signature.bind_partial(*args, **kwargs)
            names = list(signature.parameters)[:2 if name in ('_do_clone', 'run_clone_task') else 1]
            values = [bound.arguments[key] for key in names if key in bound.arguments]
            sites = []
            for value in values:
                if isinstance(value, dict):
                    canonical = models.get_site(value['slug']) if value.get('slug') else None
                    sites.append(canonical or value)
                elif isinstance(value, str):
                    sites.append(models.get_site(value))
            selected = [site for site in sites if s.is_subscription(site)]
            if selected:
                if name in deny:
                    raise s.QuarantineError('Route historique interdite au profil abonnements ; utiliser la commande hors-ligne')
                for site in selected:
                    s.require_verified(site)
                if name == '_compose':
                    return s.runtime_compose(selected[0]['slug'], *args[1:], **kwargs)
                if name in ('start_site', 'stop_site'):
                    slug = selected[0]['slug']
                    s.runtime_compose(slug, *(('up', '-d') if name == 'start_site' else ('stop',)))
                    models.update_status(slug, 'verified' if name == 'start_site' else 'stopped')
                    return None
            return fn(*args, **kwargs)
        return guarded_call
    for name in guarded:
        namespace[name] = wrap(name, namespace[name])


class MutationGuard:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        path = scope.get('path', '')
        if scope['type'] == 'http' and path.startswith('/api/sites/'):
            parts = path[len('/api/sites/'):].strip('/').split('/')
            site = models.get_site(parts[0])
            if s.is_subscription(site):
                metadata = len(parts) == 1 and scope['method'] == 'GET'
                denied = parts[1:2] in (['clone'], ['php-version']) or scope['method'] == 'DELETE'
                if not metadata and (denied or site.get('verification_state') != 'verified'):
                    body = b'{"detail":"Copie en quarantaine ou route historique interdite"}'
                    await send({'type': 'http.response.start', 'status': 423,
                                'headers': [(b'content-type', b'application/json')]})
                    await send({'type': 'http.response.body', 'body': body})
                    return
        await self.app(scope, receive, send)
