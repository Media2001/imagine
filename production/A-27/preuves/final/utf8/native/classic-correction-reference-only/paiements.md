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
                    "type": "mandat_sepa",
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
                    "gateway": "stripe_sepa",
                    "metric": "subscriptions_unlinked",
                    "count": 5
                }
            ],
            "autres": 0
        }
    },
    "as_of_utc": "2026-11-26T12:00:00+00:00",
    "audit_sha256": "2643383e8ccc85f7ebf84f3318ca4161e72442b152c676cbbe44e694e5886349"
}
```
