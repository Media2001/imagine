# Securite des comptes — lecture seule

Comptes par role, jamais identites.

```json
{
    "schema": "imagine-a17-security-v1",
    "read_only": true,
    "storage": "hpos",
    "as_of_utc": "2026-11-28T02:10:33Z",
    "cutoff_utc": "2025-11-28T02:10:33Z",
    "unique_management_accounts": 1,
    "roles": [
        {
            "role": "administrator",
            "accounts": 1,
            "application_password_accounts": 0,
            "two_factor_active": null,
            "last_login": {
                "status": "inconnu",
                "no_recent_record": null,
                "unknown_accounts": 1
            }
        },
        {
            "role": "editor",
            "accounts": 0,
            "application_password_accounts": 0,
            "two_factor_active": null,
            "last_login": {
                "status": "inconnu",
                "no_recent_record": null,
                "unknown_accounts": 0
            }
        },
        {
            "role": "shop_manager",
            "accounts": 0,
            "application_password_accounts": 0,
            "two_factor_active": null,
            "last_login": {
                "status": "inconnu",
                "no_recent_record": null,
                "unknown_accounts": 0
            }
        }
    ],
    "two_factor_adapter": "inconnu",
    "two_factor_coverage": "inconnu",
    "last_login_adapter": "inconnu",
    "protections": [],
    "configuration": {
        "public_registration": false,
        "default_role": "subscriber",
        "admin_file_editing": true,
        "xmlrpc_authenticated_methods": true,
        "application_passwords_available": true
    },
    "audit_sha256": "ca97f96b7066822883f58ade4dd79951d24849ba212ec82d11853cbb43b8fbbf"
}
```
