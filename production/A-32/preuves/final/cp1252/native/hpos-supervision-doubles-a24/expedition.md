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
            "subscriptions": 6,
            "shipping_empty": 6,
            "empty_with_billing": 3,
            "missing_any": 6,
            "missing_required": {
                "shipping_first_name": 6,
                "shipping_last_name": 6,
                "shipping_company": 0,
                "shipping_country": 6,
                "shipping_address_1": 6,
                "shipping_address_2": 0,
                "shipping_city": 6,
                "shipping_state": 6,
                "shipping_postcode": 6,
                "shipping_phone": 0
            },
            "country_absent": 6,
            "country_unknown": 0,
            "different_from_account": 0,
            "account_unavailable": 0
        },
        "countries": [
            {
                "country": "country_absent",
                "counts": {
                    "subscriptions": 6,
                    "shipping_empty": 6,
                    "empty_with_billing": 3,
                    "missing_any": 6,
                    "missing_required": {
                        "shipping_first_name": 6,
                        "shipping_last_name": 6,
                        "shipping_company": 0,
                        "shipping_country": 6,
                        "shipping_address_1": 6,
                        "shipping_address_2": 0,
                        "shipping_city": 6,
                        "shipping_state": 6,
                        "shipping_postcode": 6,
                        "shipping_phone": 0
                    },
                    "country_absent": 6,
                    "country_unknown": 0,
                    "different_from_account": 0,
                    "account_unavailable": 0
                }
            }
        ]
    },
    "audit_sha256": "807bf442702253ea47c94b5341970e169b2e31d9cbad34ad527d715567f03ffd"
}
```
