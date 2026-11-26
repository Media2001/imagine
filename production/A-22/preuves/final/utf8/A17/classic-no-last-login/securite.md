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
            "two_factor_active": 0,
            "last_login": {
                "status": "inconnu",
                "no_recent_record": null,
                "unknown_accounts": 1
            }
        },
        {
            "role": "a17_gestion",
            "accounts": 1,
            "application_password_accounts": 0,
            "two_factor_active": 0,
            "last_login": {
                "status": "inconnu",
                "no_recent_record": null,
                "unknown_accounts": 1
            }
        },
        {
            "role": "a17_switch_themes",
            "accounts": 1,
            "application_password_accounts": 0,
            "two_factor_active": 0,
            "last_login": {
                "status": "inconnu",
                "no_recent_record": null,
                "unknown_accounts": 1
            }
        },
        {
            "role": "a17_update_plugins",
            "accounts": 1,
            "application_password_accounts": 0,
            "two_factor_active": 0,
            "last_login": {
                "status": "inconnu",
                "no_recent_record": null,
                "unknown_accounts": 1
            }
        },
        {
            "role": "administrator",
            "accounts": 2,
            "application_password_accounts": 1,
            "two_factor_active": 1,
            "last_login": {
                "status": "inconnu",
                "no_recent_record": null,
                "unknown_accounts": 2
            }
        },
        {
            "role": "editor",
            "accounts": 3,
            "application_password_accounts": 0,
            "two_factor_active": 0,
            "last_login": {
                "status": "inconnu",
                "no_recent_record": null,
                "unknown_accounts": 3
            }
        },
        {
            "role": "shop_manager",
            "accounts": 1,
            "application_password_accounts": 0,
            "two_factor_active": 0,
            "last_login": {
                "status": "inconnu",
                "no_recent_record": null,
                "unknown_accounts": 1
            }
        }
    ],
    "two_factor_adapter": "Two_Factor_Core::is_user_using_two_factor",
    "two_factor_coverage": "supported_adapter_only",
    "last_login_adapter": "inconnu",
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
    "audit_sha256": "8d14d0dc9db869e1c1eeb98f0916b84ad3c452c1ab6b10e542f8d421829508c3"
}
```
