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
                "groups": [],
                "autres": 3
            },
            "email": {
                "groups": [],
                "autres": 2
            },
            "ip": {
                "groups": [],
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
                    "year": 2022,
                    "state": "autre",
                    "count": 5
                }
            ],
            "autres": 4
        },
        "guests": {
            "groups": [],
            "autres": 2
        }
    },
    "forms": {
        "listed_extensions": [
            "Fluent Forms"
        ],
        "other_tables": 2,
        "coverage": "heuristique bornée",
        "clear_messages_after_import": true,
        "clear_messages_after_import_label": "avertissement éditorial permanent, non mesuré sur la copie inspectée"
    },
    "audit_sha256": "9968b4137e211440d236dd74a6ba39ce93428c44fae9b835cf5dc1ea1487d9c0"
}
```
