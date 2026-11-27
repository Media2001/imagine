# Comptes des lecteurs — lecture seule

Comptes seulement ; aucune activation ni décision de reprise.

```json
{
    "schema": "imagine-a23-reader-accounts-v1",
    "read_only": true,
    "storage": "hpos",
    "neutralisation": "observe",
    "counts": {
        "readers": {
            "accounts": 32,
            "families": {
                "groups": [
                    {
                        "label": "phpass",
                        "accounts": 10
                    },
                    {
                        "label": "wordpress_bcrypt",
                        "accounts": 20
                    }
                ],
                "autres": 2
            },
            "emails": {
                "groups": [
                    {
                        "label": "email_empty",
                        "accounts": 5
                    },
                    {
                        "label": "email_malformed",
                        "accounts": 5
                    },
                    {
                        "label": "email_shared_case_insensitive",
                        "accounts": 11
                    }
                ],
                "autres": 0
            },
            "logins": {
                "groups": [
                    {
                        "label": "login_equals_email",
                        "accounts": 10
                    },
                    {
                        "label": "login_case_collision",
                        "accounts": 10
                    }
                ],
                "autres": 0
            }
        },
        "live_readers": {
            "accounts": 20,
            "families": {
                "groups": [
                    {
                        "label": "phpass",
                        "accounts": 10
                    },
                    {
                        "label": "wordpress_bcrypt",
                        "accounts": 10
                    }
                ],
                "autres": 0
            },
            "emails": {
                "groups": [
                    {
                        "label": "email_empty",
                        "accounts": 5
                    },
                    {
                        "label": "email_malformed",
                        "accounts": 5
                    },
                    {
                        "label": "email_shared_case_insensitive",
                        "accounts": 10
                    }
                ],
                "autres": 0
            },
            "logins": {
                "groups": [
                    {
                        "label": "login_equals_email",
                        "accounts": 5
                    },
                    {
                        "label": "login_case_collision",
                        "accounts": 5
                    }
                ],
                "autres": 0
            }
        },
        "without_commerce": {
            "groups": [],
            "autres": 3
        }
    },
    "audit_sha256": "56b0a2910d84cfb105dbbb94416f3e37faffc736225e473e72ad895e86e80db2"
}
```
