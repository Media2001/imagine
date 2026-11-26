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
    "audit_sha256": "f90a4edf10fce37c1fb17266aeeb1faee513144c1012de4dac9053fe2ae2e945"
}
```
