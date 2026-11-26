# Données des visiteurs — lecture seule

Comptes seulement ; aucune suppression ni durée de conservation.

```json
{
    "schema": "imagine-a25-visitor-retention-v1",
    "read_only": true,
    "storage": "classic",
    "neutralisation": "observe",
    "counts": {
        "comments": {
            "all": {
                "groups": [
                    {
                        "year": 1999,
                        "state": "1",
                        "count": 5
                    }
                ],
                "autres": 3
            },
            "email": {
                "groups": [
                    {
                        "year": 1999,
                        "state": "1",
                        "count": 5
                    }
                ],
                "autres": 2
            },
            "ip": {
                "groups": [
                    {
                        "year": 1999,
                        "state": "1",
                        "count": 5
                    }
                ],
                "autres": 2
            },
            "account": {
                "groups": [],
                "autres": 1
            }
        },
        "forms": {
            "groups": [
                {
                    "year": 0,
                    "state": "autre",
                    "count": 5
                },
                {
                    "year": 2022,
                    "state": "autre",
                    "count": 5
                }
            ],
            "autres": 2
        },
        "guests": {
            "groups": [
                {
                    "year": 1999,
                    "state": "guest",
                    "count": 5
                }
            ],
            "autres": 2
        }
    },
    "forms": {
        "listed_extensions": [],
        "other_tables": 3,
        "coverage": "heuristique bornée",
        "clear_messages_after_import": true,
        "clear_messages_after_import_label": "avertissement éditorial permanent, non mesuré sur la copie inspectée"
    },
    "audit_sha256": "42c7c5cde272f01a5c17dbd77a313d1a4b0d402194227aa7c3f956cceea54adb"
}
```
