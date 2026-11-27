# Adresses d’expédition — lecture seule

Comptes seulement ; aucune adresse ni décision postale.

```json
{
    "schema": "imagine-a24-shipping-addresses-v1",
    "read_only": true,
    "storage": "hpos",
    "neutralisation": "observe",
    "counts": {
        "overall": {
            "subscriptions": 3,
            "shipping_empty": 3,
            "empty_with_billing": 3,
            "missing_any": 3,
            "missing_required": {
                "shipping_first_name": 3,
                "shipping_last_name": 3,
                "shipping_company": 0,
                "shipping_country": 3,
                "shipping_address_1": 3,
                "shipping_address_2": 0,
                "shipping_city": 3,
                "shipping_state": 3,
                "shipping_postcode": 3,
                "shipping_phone": 0
            },
            "country_absent": 3,
            "country_unknown": 0,
            "different_from_account": 0,
            "account_unavailable": 0
        },
        "countries": [
            {
                "country": "autres pays",
                "counts": {
                    "subscriptions": 3,
                    "shipping_empty": 3,
                    "empty_with_billing": 3,
                    "missing_any": 3,
                    "missing_required": {
                        "shipping_first_name": 3,
                        "shipping_last_name": 3,
                        "shipping_company": 0,
                        "shipping_country": 3,
                        "shipping_address_1": 3,
                        "shipping_address_2": 0,
                        "shipping_city": 3,
                        "shipping_state": 3,
                        "shipping_postcode": 3,
                        "shipping_phone": 0
                    },
                    "country_absent": 3,
                    "country_unknown": 0,
                    "different_from_account": 0,
                    "account_unavailable": 0
                }
            }
        ]
    },
    "audit_sha256": "078e2d960f7b66b563b652fe1df2bebd0a9617fc143afd6a3d351c65db112760"
}
```
