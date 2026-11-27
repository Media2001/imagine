# Moyens de paiement enregistrés — lecture seule

Comptes seulement ; aucune garantie de renouvellement.

```json
{
    "schema": "imagine-a27-saved-payments-v1",
    "read_only": true,
    "storage": "hpos",
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
    "audit_sha256": "6646eaae0d4d87154e9c5aaff08302dde8548b48b90e68d18895cbb9094b5edd"
}
```
