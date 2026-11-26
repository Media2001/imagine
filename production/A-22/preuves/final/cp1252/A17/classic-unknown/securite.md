# Securite des comptes — lecture seule

Comptes par role, jamais identites.

```json
{
    "schema": "imagine-a17-security-v1",
    "read_only": true,
    "storage": "classic",
    "as_of_utc": "2026-11-26T12:00:00Z",
    "cutoff_utc": "2025-11-26T12:00:00Z",
    "unique_management_accounts": 10,
    "roles": [
        {
            "role": "a17_edit_users",
            "accounts": 1,
            "application_password_accounts": 0,
            "two_factor_active": null,
            "last_login": {
                "status": "observe",
                "no_recent_record": 0,
                "unknown_accounts": 1
            }
        },
        {
            "role": "a17_gestion",
            "accounts": 1,
            "application_password_accounts": 0,
            "two_factor_active": null,
            "last_login": {
                "status": "observe",
                "no_recent_record": 0,
                "unknown_accounts": 1
            }
        },
        {
            "role": "a17_switch_themes",
            "accounts": 1,
            "application_password_accounts": 0,
            "two_factor_active": null,
            "last_login": {
                "status": "observe",
                "no_recent_record": 0,
                "unknown_accounts": 1
            }
        },
        {
            "role": "a17_update_plugins",
            "accounts": 1,
            "application_password_accounts": 0,
            "two_factor_active": null,
            "last_login": {
                "status": "observe",
                "no_recent_record": 0,
                "unknown_accounts": 1
            }
        },
        {
            "role": "administrator",
            "accounts": 2,
            "application_password_accounts": 1,
            "two_factor_active": null,
            "last_login": {
                "status": "observe",
                "no_recent_record": 1,
                "unknown_accounts": 0
            }
        },
        {
            "role": "editor",
            "accounts": 3,
            "application_password_accounts": 0,
            "two_factor_active": null,
            "last_login": {
                "status": "observe",
                "no_recent_record": 0,
                "unknown_accounts": 2
            }
        },
        {
            "role": "shop_manager",
            "accounts": 1,
            "application_password_accounts": 0,
            "two_factor_active": null,
            "last_login": {
                "status": "observe",
                "no_recent_record": 0,
                "unknown_accounts": 1
            }
        }
    ],
    "two_factor_adapter": "inconnu",
    "two_factor_coverage": "inconnu",
    "last_login_adapter": "WP Last Login:wp-last-login",
    "protections": [
        {
            "name": "Limit Login Attempts Reloaded fixture",
            "version": "2.26.0",
            "active": true,
            "kind": "limitation_tentatives"
        },
        {
            "name": "Other 2FA fixture",
            "version": "1.0.0",
            "active": true,
            "kind": "double_authentification"
        },
        {
            "name": "Two-Factor fixture",
            "version": "0.17.0",
            "active": true,
            "kind": "double_authentification"
        },
        {
            "name": "Wordfence fixture inactive",
            "version": "8.0.0",
            "active": false,
            "kind": "pare_feu"
        }
    ],
    "configuration": {
        "public_registration": true,
        "default_role": "subscriber",
        "admin_file_editing": true,
        "xmlrpc_authenticated_methods": true,
        "application_passwords_available": true
    },
    "audit_sha256": "143dacce929782cb4b88a6c52111473af602c001fcb843deab66ac1e3dd39223"
}
```
