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
            "subscriptions": 12,
            "shipping_empty": 1,
            "empty_with_billing": 1,
            "missing_any": 5,
            "missing_required": {
                "shipping_first_name": 1,
                "shipping_last_name": 1,
                "shipping_company": 0,
                "shipping_country": 2,
                "shipping_address_1": 1,
                "shipping_address_2": 0,
                "shipping_city": 1,
                "shipping_state": 2,
                "shipping_postcode": 2,
                "shipping_phone": 0
            },
            "country_absent": 2,
            "country_unknown": 1,
            "different_from_account": 1,
            "account_unavailable": 1
        },
        "countries": [
            {
                "country": "BE",
                "counts": {
                    "subscriptions": 6,
                    "shipping_empty": 0,
                    "empty_with_billing": 0,
                    "missing_any": 0,
                    "missing_required": {
                        "shipping_first_name": 0,
                        "shipping_last_name": 0,
                        "shipping_company": 0,
                        "shipping_country": 0,
                        "shipping_address_1": 0,
                        "shipping_address_2": 0,
                        "shipping_city": 0,
                        "shipping_state": 0,
                        "shipping_postcode": 0,
                        "shipping_phone": 0
                    },
                    "country_absent": 0,
                    "country_unknown": 0,
                    "different_from_account": 1,
                    "account_unavailable": 1
                }
            },
            {
                "country": "autres pays",
                "counts": {
                    "subscriptions": 6,
                    "shipping_empty": 1,
                    "empty_with_billing": 1,
                    "missing_any": 5,
                    "missing_required": {
                        "shipping_first_name": 1,
                        "shipping_last_name": 1,
                        "shipping_company": 0,
                        "shipping_country": 2,
                        "shipping_address_1": 1,
                        "shipping_address_2": 0,
                        "shipping_city": 1,
                        "shipping_state": 2,
                        "shipping_postcode": 2,
                        "shipping_phone": 0
                    },
                    "country_absent": 2,
                    "country_unknown": 1,
                    "different_from_account": 0,
                    "account_unavailable": 0
                }
            }
        ]
    },
    "audit_sha256": "00a3e4093362e568f8c35c3d1180e1797bbd95f4fb369bf1e9861da1ee8216c5"
}
```
