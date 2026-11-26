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
                    "year": 1999,
                    "state": "Fluent Forms",
                    "count": 5
                }
            ],
            "autres": 4
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
        "listed_extensions": [
            "Fluent Forms"
        ],
        "other_tables": 1,
        "clear_messages_after_import": true
    },
    "audit_sha256": "be24a15c6637eeaf703cac81ae18b1fd9080b011d75c51117f8009828e3c7557"
}
```
