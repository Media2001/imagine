# Données des visiteurs — lecture seule

Comptes seulement ; aucune suppression ni durée de conservation.

```json
{
    "schema": "imagine-a25-visitor-retention-v1",
    "read_only": true,
    "storage": "hpos",
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
    "audit_sha256": "02a7268c926a18125473efe19035314de26e434e7627144edd8f552a5150ba2a"
}
```
