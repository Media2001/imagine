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
                    "year": 0,
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
        "other_tables": 2,
        "clear_messages_after_import": true
    },
    "audit_sha256": "b03dc1f02c6e6987ccd747d54257dac60586bab3473464fc968296ac58c84568"
}
```
