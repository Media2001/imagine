# Inventaire des codes — lecture seule

Noms des codes autorises; aucun contact ni identifiant client. Aucun reclassement.

```json
{
    "schema": "imagine-a10-coupons-v1",
    "read_only": true,
    "generated_at_utc": "2026-11-25T20:43:24Z",
    "storage": "hpos",
    "currency": "USD",
    "window": {
        "from_utc": "2025-11-25T20:43:24Z",
        "to_utc": "2026-11-25T20:43:24Z",
        "inclusive": true
    },
    "codes": [
        {
            "code": "a10-expired",
            "status": "publish",
            "type": "percent",
            "amount": "5",
            "amount_unit": "percent",
            "date_created_utc": "2026-11-25T20:43:21Z",
            "date_modified_utc": "2026-11-25T20:43:21Z",
            "date_expires_utc": "2000-01-01T00:00:00Z",
            "usage_count": 9,
            "usage_limit": 0,
            "usage_limit_per_user": 0,
            "item_limit": null,
            "product_ids": [],
            "excluded_product_ids": [],
            "product_categories": [],
            "excluded_product_categories": [],
            "allowed_email_count": 0,
            "individual_use": false,
            "free_shipping": false,
            "exclude_sale_items": false,
            "minimum_amount": "0",
            "maximum_amount": "0",
            "recurring_on_renewals": false,
            "payment_limit_including_initial": 0,
            "subscriptions": {
                "active": 0,
                "on_hold": 0,
                "pending": 0,
                "pending_cancel": 0
            },
            "orders_12_months": 0
        },
        {
            "code": "a10-expired-never-used",
            "status": "publish",
            "type": "percent",
            "amount": "5",
            "amount_unit": "percent",
            "date_created_utc": "2026-11-25T20:43:21Z",
            "date_modified_utc": "2026-11-25T20:43:21Z",
            "date_expires_utc": "2000-01-01T00:00:00Z",
            "usage_count": 0,
            "usage_limit": 0,
            "usage_limit_per_user": 0,
            "item_limit": null,
            "product_ids": [],
            "excluded_product_ids": [],
            "product_categories": [],
            "excluded_product_categories": [],
            "allowed_email_count": 0,
            "individual_use": false,
            "free_shipping": false,
            "exclude_sale_items": false,
            "minimum_amount": "0",
            "maximum_amount": "0",
            "recurring_on_renewals": false,
            "payment_limit_including_initial": 0,
            "subscriptions": {
                "active": 0,
                "on_hold": 0,
                "pending": 0,
                "pending_cancel": 0
            },
            "orders_12_months": 0
        },
        {
            "code": "a10-fixed-cart",
            "status": "publish",
            "type": "fixed_cart",
            "amount": "10.50",
            "amount_unit": "store_currency",
            "date_created_utc": "2025-01-01T12:00:00Z",
            "date_modified_utc": "2025-01-01T12:00:00Z",
            "date_expires_utc": "2035-01-01T00:00:00Z",
            "usage_count": 2,
            "usage_limit": 50,
            "usage_limit_per_user": 2,
            "item_limit": 3,
            "product_ids": [
                24
            ],
            "excluded_product_ids": [
                25
            ],
            "product_categories": [
                19
            ],
            "excluded_product_categories": [],
            "allowed_email_count": 2,
            "individual_use": true,
            "free_shipping": true,
            "exclude_sale_items": true,
            "minimum_amount": "5.00",
            "maximum_amount": "100.00",
            "recurring_on_renewals": false,
            "payment_limit_including_initial": 0,
            "subscriptions": {
                "active": 0,
                "on_hold": 0,
                "pending": 0,
                "pending_cancel": 0
            },
            "orders_12_months": 0
        },
        {
            "code": "a10-fixed-product",
            "status": "publish",
            "type": "fixed_product",
            "amount": "10.50",
            "amount_unit": "store_currency",
            "date_created_utc": "2025-01-01T12:00:00Z",
            "date_modified_utc": "2025-01-01T12:00:00Z",
            "date_expires_utc": "2035-01-01T00:00:00Z",
            "usage_count": 3,
            "usage_limit": 50,
            "usage_limit_per_user": 2,
            "item_limit": 3,
            "product_ids": [
                24
            ],
            "excluded_product_ids": [
                25
            ],
            "product_categories": [
                19
            ],
            "excluded_product_categories": [],
            "allowed_email_count": 2,
            "individual_use": true,
            "free_shipping": true,
            "exclude_sale_items": true,
            "minimum_amount": "5.00",
            "maximum_amount": "100.00",
            "recurring_on_renewals": false,
            "payment_limit_including_initial": 0,
            "subscriptions": {
                "active": 0,
                "on_hold": 0,
                "pending": 0,
                "pending_cancel": 0
            },
            "orders_12_months": 0
        },
        {
            "code": "a10-never-used",
            "status": "publish",
            "type": "percent",
            "amount": "5",
            "amount_unit": "percent",
            "date_created_utc": "2026-11-25T20:43:21Z",
            "date_modified_utc": "2026-11-25T20:43:21Z",
            "date_expires_utc": null,
            "usage_count": 0,
            "usage_limit": 0,
            "usage_limit_per_user": 0,
            "item_limit": null,
            "product_ids": [],
            "excluded_product_ids": [],
            "product_categories": [],
            "excluded_product_categories": [],
            "allowed_email_count": 0,
            "individual_use": false,
            "free_shipping": false,
            "exclude_sale_items": false,
            "minimum_amount": "0",
            "maximum_amount": "0",
            "recurring_on_renewals": false,
            "payment_limit_including_initial": 0,
            "subscriptions": {
                "active": 0,
                "on_hold": 0,
                "pending": 0,
                "pending_cancel": 0
            },
            "orders_12_months": 0
        },
        {
            "code": "a10-percent",
            "status": "publish",
            "type": "percent",
            "amount": "10.50",
            "amount_unit": "percent",
            "date_created_utc": "2025-01-01T12:00:00Z",
            "date_modified_utc": "2025-01-01T12:00:00Z",
            "date_expires_utc": "2035-01-01T00:00:00Z",
            "usage_count": 1,
            "usage_limit": 50,
            "usage_limit_per_user": 2,
            "item_limit": 3,
            "product_ids": [
                24
            ],
            "excluded_product_ids": [
                25
            ],
            "product_categories": [
                19
            ],
            "excluded_product_categories": [],
            "allowed_email_count": 2,
            "individual_use": true,
            "free_shipping": true,
            "exclude_sale_items": true,
            "minimum_amount": "5.00",
            "maximum_amount": "100.00",
            "recurring_on_renewals": false,
            "payment_limit_including_initial": 0,
            "subscriptions": {
                "active": 0,
                "on_hold": 0,
                "pending": 0,
                "pending_cancel": 0
            },
            "orders_12_months": 0
        },
        {
            "code": "a10-recurring-fee",
            "status": "publish",
            "type": "recurring_fee",
            "amount": "10.50",
            "amount_unit": "store_currency",
            "date_created_utc": "2025-01-01T12:00:00Z",
            "date_modified_utc": "2025-01-01T12:00:00Z",
            "date_expires_utc": "2035-01-01T00:00:00Z",
            "usage_count": 6,
            "usage_limit": 50,
            "usage_limit_per_user": 2,
            "item_limit": 3,
            "product_ids": [
                24
            ],
            "excluded_product_ids": [
                25
            ],
            "product_categories": [
                19
            ],
            "excluded_product_categories": [],
            "allowed_email_count": 2,
            "individual_use": true,
            "free_shipping": true,
            "exclude_sale_items": true,
            "minimum_amount": "5.00",
            "maximum_amount": "100.00",
            "recurring_on_renewals": true,
            "payment_limit_including_initial": 3,
            "subscriptions": {
                "active": 1,
                "on_hold": 1,
                "pending": 1,
                "pending_cancel": 1
            },
            "orders_12_months": 5
        },
        {
            "code": "a10-recurring-percent",
            "status": "publish",
            "type": "recurring_percent",
            "amount": "10.50",
            "amount_unit": "percent",
            "date_created_utc": "2025-01-01T12:00:00Z",
            "date_modified_utc": "2025-01-01T12:00:00Z",
            "date_expires_utc": "2035-01-01T00:00:00Z",
            "usage_count": 5,
            "usage_limit": 50,
            "usage_limit_per_user": 2,
            "item_limit": 3,
            "product_ids": [
                24
            ],
            "excluded_product_ids": [
                25
            ],
            "product_categories": [
                19
            ],
            "excluded_product_categories": [],
            "allowed_email_count": 2,
            "individual_use": true,
            "free_shipping": true,
            "exclude_sale_items": true,
            "minimum_amount": "5.00",
            "maximum_amount": "100.00",
            "recurring_on_renewals": true,
            "payment_limit_including_initial": 0,
            "subscriptions": {
                "active": 0,
                "on_hold": 0,
                "pending": 0,
                "pending_cancel": 0
            },
            "orders_12_months": 0
        },
        {
            "code": "a10-sign-up-fee",
            "status": "publish",
            "type": "sign_up_fee",
            "amount": "10.50",
            "amount_unit": "store_currency",
            "date_created_utc": "2025-01-01T12:00:00Z",
            "date_modified_utc": "2025-01-01T12:00:00Z",
            "date_expires_utc": "2035-01-01T00:00:00Z",
            "usage_count": 6,
            "usage_limit": 50,
            "usage_limit_per_user": 2,
            "item_limit": 3,
            "product_ids": [
                24
            ],
            "excluded_product_ids": [
                25
            ],
            "product_categories": [
                19
            ],
            "excluded_product_categories": [],
            "allowed_email_count": 2,
            "individual_use": true,
            "free_shipping": true,
            "exclude_sale_items": true,
            "minimum_amount": "5.00",
            "maximum_amount": "100.00",
            "recurring_on_renewals": false,
            "payment_limit_including_initial": 0,
            "subscriptions": {
                "active": 0,
                "on_hold": 0,
                "pending": 0,
                "pending_cancel": 0
            },
            "orders_12_months": 0
        },
        {
            "code": "a10-sign-up-fee-percent",
            "status": "publish",
            "type": "sign_up_fee_percent",
            "amount": "10.50",
            "amount_unit": "percent",
            "date_created_utc": "2025-01-01T12:00:00Z",
            "date_modified_utc": "2025-01-01T12:00:00Z",
            "date_expires_utc": "2035-01-01T00:00:00Z",
            "usage_count": 7,
            "usage_limit": 50,
            "usage_limit_per_user": 2,
            "item_limit": 3,
            "product_ids": [
                24
            ],
            "excluded_product_ids": [
                25
            ],
            "product_categories": [
                19
            ],
            "excluded_product_categories": [],
            "allowed_email_count": 2,
            "individual_use": true,
            "free_shipping": true,
            "exclude_sale_items": true,
            "minimum_amount": "5.00",
            "maximum_amount": "100.00",
            "recurring_on_renewals": false,
            "payment_limit_including_initial": 0,
            "subscriptions": {
                "active": 0,
                "on_hold": 0,
                "pending": 0,
                "pending_cancel": 0
            },
            "orders_12_months": 0
        }
    ],
    "expired": [
        "a10-expired",
        "a10-expired-never-used"
    ],
    "never_used": [
        "a10-expired-never-used",
        "a10-never-used"
    ],
    "limitations": [
        "Reglages enregistres uniquement, aucun bootstrap ni filtre tiers; aucune promesse de remise effective future.",
        "Recurrence standard Subscriptions; null pour type inconnu. Limite de paiements incluant le paiement initial: 0 illimitee; ce total configure ne mesure pas le solde de chaque abonnement.",
        "Commandes distinctes par code et creation UTC sur douze mois calendaires; tous statuts sauf corbeille et auto-draft, futurs et remboursements enfants exclus. Ce ne sont pas des ventes nettes.",
        "Abonnements porteurs distincts: active, on-hold, pending et pending-cancel separes; cancelled et expired exclus.",
        "Jamais utilise signifie usage_count enregistre egal a zero, pas une reconstruction historique. Expire et jamais utilise peuvent se recouper.",
        "Aucun reclassement ni suppression. Usage limits 0 sans limite, item_limit null sans limite, seuils vides 0 sans restriction; montants invalides null.",
        "Site simple, configuration litterale, tables InnoDB, stockage Woo standard; metadonnees coupon dupliquees refusees."
    ],
    "audit_sha256": "a34b06442886c18ac9ce7b7dd439aa3c4004b1ea5f48ec9caaa31df9bd121e83"
}
```
