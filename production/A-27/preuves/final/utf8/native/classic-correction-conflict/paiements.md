# Moyens de paiement enregistrés — lecture seule

Comptes seulement ; aucune garantie de renouvellement.

```json
{
    "schema": "imagine-a27-saved-payments-v1",
    "read_only": true,
    "storage": "classic",
    "neutralisation": "observe",
    "counts": {
        "automatic": {
            "groups": [
                {
                    "gateway": "stripe_sepa",
                    "type": "illisible",
                    "count": 5
                }
            ],
            "autres": 0
        },
        "cards": {
            "groups": [],
            "autres": 0
        },
        "relations": {
            "groups": [
                {
                    "gateway": "autre",
                    "metric": "accounts_multiple_tokens",
                    "count": 5
                },
                {
                    "gateway": "stripe_sepa",
                    "metric": "subscriptions_link_unknown",
                    "count": 5
                }
            ],
            "autres": 0
        }
    },
    "as_of_utc": "2026-11-26T12:00:00+00:00",
    "audit_sha256": "ad8f6c9fbed2fc731aecc0ff533771221e6372bb23ce27c66f9c87ea4191f0c7"
}
```
