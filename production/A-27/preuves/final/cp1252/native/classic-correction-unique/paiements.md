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
                    "gateway": "autre",
                    "metric": "accounts_multiple_tokens",
                    "count": 5
                }
            ],
            "autres": 0
        }
    },
    "as_of_utc": "2026-11-26T12:00:00+00:00",
    "audit_sha256": "522c563f2b135d3b99b7ee6bbbb97e6c2f5d4efac4d7c8d02b1dde3f72ffde7d"
}
```
