# Audit de l existant — lecture seule

Aucune valeur personnelle ou de reglage sensible. Inconnue signifie non observable sans reseau ou bootstrap.

## 1. Versions

```json
{
    "wordpress": "7.0",
    "php": "8.2.36",
    "php_sapi": "cli",
    "database": "10.11.19",
    "database_family": "MariaDB",
    "plugins": [
        {
            "name": "a08-orphan/entry.php",
            "version": "1.0.0",
            "active": true,
            "kind": "plugin",
            "latest": null,
            "requires_wp": null,
            "requires_php": null,
            "requires_woo": null,
            "requirements_source": "headers_or_literal_MINIMUM_constants_else_unknown",
            "latest_requires_wp": null,
            "latest_requires_php": null,
            "last_updated": null
        },
        {
            "name": "akismet/akismet.php",
            "version": "5.7",
            "active": false,
            "kind": "plugin",
            "latest": null,
            "requires_wp": "5.8",
            "requires_php": "7.2",
            "requires_woo": null,
            "requirements_source": "headers_or_literal_MINIMUM_constants_else_unknown",
            "latest_requires_wp": null,
            "latest_requires_php": null,
            "last_updated": null
        },
        {
            "name": "hello.php",
            "version": "1.7.2",
            "active": false,
            "kind": "plugin",
            "latest": null,
            "requires_wp": null,
            "requires_php": null,
            "requires_woo": null,
            "requirements_source": "headers_or_literal_MINIMUM_constants_else_unknown",
            "latest_requires_wp": null,
            "latest_requires_php": null,
            "last_updated": null
        },
        {
            "name": "woocommerce-memberships/woocommerce-memberships.php",
            "version": "1.30.3",
            "active": true,
            "kind": "plugin",
            "latest": null,
            "requires_wp": "5.6",
            "requires_php": "7.4",
            "requires_woo": "3.9.4",
            "requirements_source": "headers_or_literal_MINIMUM_constants_else_unknown",
            "latest_requires_wp": null,
            "latest_requires_php": null,
            "last_updated": null
        },
        {
            "name": "woocommerce-subscriptions/woocommerce-subscriptions.php",
            "version": "9.4.1",
            "active": true,
            "kind": "plugin",
            "latest": null,
            "requires_wp": "7.0",
            "requires_php": "7.4",
            "requires_woo": "11.1",
            "requirements_source": "headers_or_literal_MINIMUM_constants_else_unknown",
            "latest_requires_wp": null,
            "latest_requires_php": null,
            "last_updated": null
        },
        {
            "name": "woocommerce/woocommerce.php",
            "version": "11.0.1",
            "active": true,
            "kind": "plugin",
            "latest": null,
            "requires_wp": "6.9",
            "requires_php": "7.4",
            "requires_woo": null,
            "requirements_source": "headers_or_literal_MINIMUM_constants_else_unknown",
            "latest_requires_wp": null,
            "latest_requires_php": null,
            "last_updated": null
        },
        {
            "name": "mu/000-imagine-staging-safety.php",
            "version": null,
            "active": true,
            "kind": "mu",
            "latest": null,
            "requires_wp": null,
            "requires_php": null,
            "requires_woo": null,
            "requirements_source": "headers_or_literal_MINIMUM_constants_else_unknown",
            "latest_requires_wp": null,
            "latest_requires_php": null,
            "last_updated": null
        }
    ],
    "themes": [
        {
            "name": "a03-fiction",
            "version": "1.0.0",
            "active": true,
            "role": "stylesheet_template",
            "latest": null,
            "requires_wp": null,
            "requires_php": null,
            "latest_requires_wp": null,
            "latest_requires_php": null
        },
        {
            "name": "twentytwentyfive",
            "version": "1.5",
            "active": false,
            "role": "inactive",
            "latest": null,
            "requires_wp": "6.7",
            "requires_php": "7.2",
            "latest_requires_wp": null,
            "latest_requires_php": null
        },
        {
            "name": "twentytwentyfour",
            "version": "1.5",
            "active": false,
            "role": "inactive",
            "latest": null,
            "requires_wp": "6.4",
            "requires_php": "7.0",
            "latest_requires_wp": null,
            "latest_requires_php": null
        },
        {
            "name": "twentytwentythree",
            "version": "1.6",
            "active": false,
            "role": "inactive",
            "latest": null,
            "requires_wp": "6.1",
            "requires_php": "5.6",
            "latest_requires_wp": null,
            "latest_requires_php": null
        }
    ],
    "update_source": "local_cache_only_not_a_live_check",
    "plugin_cache_checked_epoch": null,
    "theme_cache_checked_epoch": null
}
```

## 2. Commerce

```json
{
    "order_storage": "classic",
    "order_year_basis": "UTC_creation",
    "gateways": [
        "bacs",
        "cheque",
        "cod",
        "paypal",
        "pre_install_woocommerce_payments_promotion"
    ],
    "gateway_detection": "static_active_source_ids_not_enabled_status_dynamic_ids_unknown",
    "gateway_unresolved": [
        {
            "plugin": "woocommerce-memberships/woocommerce-memberships.php",
            "class": "wc_settings_memberships",
            "reason": "ancestry_unresolved"
        },
        {
            "plugin": "woocommerce-memberships/woocommerce-memberships.php",
            "class": "wc_memberships_user_membership_activated_email",
            "reason": "ancestry_unresolved"
        },
        {
            "plugin": "woocommerce-memberships/woocommerce-memberships.php",
            "class": "wc_memberships_user_membership_ended_email",
            "reason": "ancestry_unresolved"
        },
        {
            "plugin": "woocommerce-memberships/woocommerce-memberships.php",
            "class": "wc_memberships_user_membership_ending_soon_email",
            "reason": "ancestry_unresolved"
        },
        {
            "plugin": "woocommerce-memberships/woocommerce-memberships.php",
            "class": "wc_memberships_user_membership_note_email",
            "reason": "ancestry_unresolved"
        },
        {
            "plugin": "woocommerce-memberships/woocommerce-memberships.php",
            "class": "wc_memberships_user_membership_renewal_reminder_email",
            "reason": "ancestry_unresolved"
        },
        {
            "plugin": "woocommerce-memberships/woocommerce-memberships.php",
            "class": "[masque]",
            "reason": "ancestry_unresolved"
        },
        {
            "plugin": "woocommerce-subscriptions/woocommerce-subscriptions.php",
            "class": "wcs_email_cancelled_subscription",
            "reason": "ancestry_unresolved"
        },
        {
            "plugin": "woocommerce-subscriptions/woocommerce-subscriptions.php",
            "class": "wcs_email_completed_renewal_order",
            "reason": "ancestry_unresolved"
        },
        {
            "plugin": "woocommerce-subscriptions/woocommerce-subscriptions.php",
            "class": "wcs_email_completed_switch_order",
            "reason": "ancestry_unresolved"
        },
        {
            "plugin": "woocommerce-subscriptions/woocommerce-subscriptions.php",
            "class": "wcs_email_customer_cancelled_subscription",
            "reason": "ancestry_unresolved"
        },
        {
            "plugin": "woocommerce-subscriptions/woocommerce-subscriptions.php",
            "class": "wcs_email_customer_notification_auto_renewal",
            "reason": "ancestry_unresolved"
        },
        {
            "plugin": "woocommerce-subscriptions/woocommerce-subscriptions.php",
            "class": "wcs_email_customer_notification_auto_trial_expiration",
            "reason": "ancestry_unresolved"
        },
        {
            "plugin": "woocommerce-subscriptions/woocommerce-subscriptions.php",
            "class": "wcs_email_customer_notification_manual_renewal",
            "reason": "ancestry_unresolved"
        },
        {
            "plugin": "woocommerce-subscriptions/woocommerce-subscriptions.php",
            "class": "wcs_email_customer_notification_manual_trial_expiration",
            "reason": "ancestry_unresolved"
        },
        {
            "plugin": "woocommerce-subscriptions/woocommerce-subscriptions.php",
            "class": "wcs_email_customer_notification_subscription_expiration",
            "reason": "ancestry_unresolved"
        },
        {
            "plugin": "woocommerce-subscriptions/woocommerce-subscriptions.php",
            "class": "wcs_email_customer_on_hold_renewal_order",
            "reason": "ancestry_unresolved"
        },
        {
            "plugin": "woocommerce-subscriptions/woocommerce-subscriptions.php",
            "class": "wcs_email_customer_renewal_invoice",
            "reason": "ancestry_unresolved"
        },
        {
            "plugin": "woocommerce-subscriptions/woocommerce-subscriptions.php",
            "class": "wcs_email_expired_subscription",
            "reason": "ancestry_unresolved"
        },
        {
            "plugin": "woocommerce-subscriptions/woocommerce-subscriptions.php",
            "class": "wcs_email_new_renewal_order",
            "reason": "ancestry_unresolved"
        },
        {
            "plugin": "woocommerce-subscriptions/woocommerce-subscriptions.php",
            "class": "wcs_email_new_switch_order",
            "reason": "ancestry_unresolved"
        },
        {
            "plugin": "woocommerce-subscriptions/woocommerce-subscriptions.php",
            "class": "wcs_email_on_hold_subscription",
            "reason": "ancestry_unresolved"
        },
        {
            "plugin": "woocommerce-subscriptions/woocommerce-subscriptions.php",
            "class": "wcs_email_processing_renewal_order",
            "reason": "ancestry_unresolved"
        },
        {
            "plugin": "woocommerce-subscriptions/woocommerce-subscriptions.php",
            "class": "wcs_email_reactivated_subscription",
            "reason": "ancestry_unresolved"
        },
        {
            "plugin": "woocommerce-subscriptions/woocommerce-subscriptions.php",
            "class": "wcsg_email_completed_renewal_order",
            "reason": "ancestry_unresolved"
        },
        {
            "plugin": "woocommerce-subscriptions/woocommerce-subscriptions.php",
            "class": "wcsg_email_customer_new_account",
            "reason": "ancestry_unresolved"
        },
        {
            "plugin": "woocommerce-subscriptions/woocommerce-subscriptions.php",
            "class": "wcsg_email_processing_renewal_order",
            "reason": "ancestry_unresolved"
        },
        {
            "plugin": "woocommerce-subscriptions/woocommerce-subscriptions.php",
            "class": "wcsg_email_recipient_new_initial_order",
            "reason": "ancestry_unresolved"
        },
        {
            "plugin": "woocommerce-subscriptions/woocommerce-subscriptions.php",
            "class": "wcs_email_customer_payment_retry",
            "reason": "ancestry_unresolved"
        },
        {
            "plugin": "woocommerce-subscriptions/woocommerce-subscriptions.php",
            "class": "wcs_email_payment_retry",
            "reason": "ancestry_unresolved"
        },
        {
            "plugin": "woocommerce-subscriptions/woocommerce-subscriptions.php",
            "class": "[masque]",
            "reason": "ancestry_unresolved"
        },
        {
            "plugin": "woocommerce/woocommerce.php",
            "class": "wc_tax_rate_importer",
            "reason": "ancestry_unresolved"
        },
        {
            "plugin": "woocommerce/woocommerce.php",
            "class": "wc_payment_gateway_cc",
            "reason": "id_unresolved"
        },
        {
            "plugin": "woocommerce/woocommerce.php",
            "class": "wc_payment_gateway_echeck",
            "reason": "id_unresolved"
        },
        {
            "plugin": "woocommerce/woocommerce.php",
            "class": "[masque]",
            "reason": "id_unresolved"
        }
    ],
    "subscriptions": [
        {
            "status": "wc-active",
            "period": "month",
            "interval": 1,
            "count": 1
        },
        {
            "status": "wc-cancelled",
            "period": "year",
            "interval": 4,
            "count": 1
        },
        {
            "status": "wc-expired",
            "period": "month",
            "interval": 3,
            "count": 1
        },
        {
            "status": "wc-on-hold",
            "period": "year",
            "interval": 2,
            "count": 1
        },
        {
            "status": "wc-pending",
            "period": "month",
            "interval": 5,
            "count": 1
        },
        {
            "status": "wc-pending-cancel",
            "period": "year",
            "interval": 6,
            "count": 1
        }
    ],
    "memberships": [
        {
            "plan_id": 12,
            "status": "wcm-active",
            "count": 1
        },
        {
            "plan_id": 12,
            "status": "wcm-cancelled",
            "count": 1
        },
        {
            "plan_id": 12,
            "status": "wcm-expired",
            "count": 1
        },
        {
            "plan_id": 12,
            "status": "wcm-paused",
            "count": 1
        },
        {
            "plan_id": 12,
            "status": "wcm-pending",
            "count": 1
        }
    ],
    "subscription_meta_selection": "lowest_meta_row_id_per_subscription_and_key; not_a_data_repair",
    "subscription_meta_anomalies": [
        {
            "key": "_billing_interval",
            "subscriptions_with_duplicates": 0,
            "extra_rows": 0,
            "subscriptions_with_conflicts": 0
        },
        {
            "key": "_billing_period",
            "subscriptions_with_duplicates": 0,
            "extra_rows": 0,
            "subscriptions_with_conflicts": 0
        }
    ],
    "orders_by_year": [
        {
            "year": 2025,
            "count": 2
        },
        {
            "year": 2026,
            "count": 2
        }
    ],
    "subscription_products": []
}
```

## 3. Memberships

```json
{
    "plans": [
        {
            "id": 12,
            "status": "publish"
        }
    ],
    "rules": [
        {
            "plan_id": 12,
            "active": true,
            "content_type": "post_type",
            "content_type_name": "post",
            "object_ids": [
                10
            ],
            "all_objects": false,
            "access_schedule": "immediate",
            "drip": false,
            "amount": null,
            "period": null
        }
    ],
    "interpretation": "raw_saved_rules_not_runtime_effective_access; ids_only_no_titles_or_user_ids"
}
```

## 4. Contenu

```json
{
    "post_types": [
        {
            "name": "attachment",
            "count": 1
        },
        {
            "name": "nav_menu_item",
            "count": 0
        },
        {
            "name": "page",
            "count": 8
        },
        {
            "name": "post",
            "count": 3
        },
        {
            "name": "revision",
            "count": 0
        },
        {
            "name": "shop_order",
            "count": 4
        },
        {
            "name": "shop_subscription",
            "count": 6
        },
        {
            "name": "wc_membership_plan",
            "count": 1
        },
        {
            "name": "wc_user_membership",
            "count": 5
        }
    ],
    "taxonomies": [
        {
            "name": "category",
            "count": 1
        },
        {
            "name": "link_category",
            "count": 0
        },
        {
            "name": "nav_menu",
            "count": 0
        },
        {
            "name": "post_format",
            "count": 0
        },
        {
            "name": "post_tag",
            "count": 0
        },
        {
            "name": "product_cat",
            "count": 1
        },
        {
            "name": "product_type",
            "count": 6
        },
        {
            "name": "product_visibility",
            "count": 9
        }
    ],
    "custom_fields": [
        {
            "name": "_billing_address_index",
            "count": 10
        },
        {
            "name": "_billing_email",
            "count": 10
        },
        {
            "name": "_cart_discount",
            "count": 10
        },
        {
            "name": "_cart_discount_tax",
            "count": 10
        },
        {
            "name": "_customer_user",
            "count": 10
        },
        {
            "name": "_download_permissions_granted",
            "count": 10
        },
        {
            "name": "_new_order_email_sent",
            "count": 10
        },
        {
            "name": "_order_currency",
            "count": 10
        },
        {
            "name": "_order_key",
            "count": 10
        },
        {
            "name": "_order_shipping",
            "count": 10
        },
        {
            "name": "_order_shipping_tax",
            "count": 10
        },
        {
            "name": "_order_stock_reduced",
            "count": 10
        },
        {
            "name": "_order_tax",
            "count": 10
        },
        {
            "name": "_order_total",
            "count": 10
        },
        {
            "name": "_order_version",
            "count": 10
        },
        {
            "name": "_prices_include_tax",
            "count": 10
        },
        {
            "name": "_recorded_coupon_usage_counts",
            "count": 10
        },
        {
            "name": "_recorded_sales",
            "count": 10
        },
        {
            "name": "_shipping_address_index",
            "count": 10
        },
        {
            "name": "_billing_first_name",
            "count": 6
        },
        {
            "name": "_billing_interval",
            "count": 6
        },
        {
            "name": "_billing_period",
            "count": 6
        },
        {
            "name": "_cancelled_email_sent",
            "count": 6
        },
        {
            "name": "_last_order_date_created",
            "count": 6
        },
        {
            "name": "_requires_manual_renewal",
            "count": 6
        },
        {
            "name": "_schedule_cancelled",
            "count": 6
        },
        {
            "name": "_schedule_end",
            "count": 6
        },
        {
            "name": "_schedule_next_payment",
            "count": 6
        },
        {
            "name": "_schedule_payment_retry",
            "count": 6
        },
        {
            "name": "_schedule_start",
            "count": 6
        },
        {
            "name": "_schedule_trial_end",
            "count": 6
        },
        {
            "name": "_subscription_renewal_order_ids_cache",
            "count": 6
        },
        {
            "name": "_subscription_switch_data",
            "count": 6
        },
        {
            "name": "_suspension_count",
            "count": 6
        },
        {
            "name": "_trial_period",
            "count": 6
        },
        {
            "name": "_end_date",
            "count": 5
        },
        {
            "name": "_start_date",
            "count": 5
        },
        {
            "name": "_subscription_resubscribe_order_ids_cache",
            "count": 5
        },
        {
            "name": "_subscription_switch_order_ids_cache",
            "count": 5
        },
        {
            "name": "_customer_ip_address",
            "count": 4
        },
        {
            "name": "_customer_user_agent",
            "count": 4
        },
        {
            "name": "_payment_method",
            "count": 3
        },
        {
            "name": "_payment_method_title",
            "count": 3
        },
        {
            "name": "_completed_date",
            "count": 2
        },
        {
            "name": "_date_completed",
            "count": 2
        },
        {
            "name": "_date_paid",
            "count": 2
        },
        {
            "name": "_encloseme",
            "count": 2
        },
        {
            "name": "_paid_date",
            "count": 2
        },
        {
            "name": "_pingme",
            "count": 2
        },
        {
            "name": "_wp_page_template",
            "count": 2
        }
    ],
    "post_year_basis": "UTC_creation",
    "custom_fields_scope": "all_postmeta_keys_including_internal_core_and_woocommerce; names_and_counts_only",
    "posts_by_year": [
        {
            "year": 2026,
            "count": 3
        }
    ],
    "page_builders": [],
    "page_builder_detection": "known_active_plugin_or_theme_names_only_not_exhaustive",
    "coverage": "stored_types_and_taxonomies_including_empty_core_types_not_runtime_registry; top_50_post_meta_keys"
}
```

## 5. Base

```json
{
    "tables": [
        {
            "name": "wp_a08_orphan",
            "bytes": 16384,
            "rows": 1,
            "ownership": "unattributed_candidate"
        },
        {
            "name": "wp_actionscheduler_actions",
            "bytes": 163840,
            "rows": 27,
            "ownership": "active_action_scheduler"
        },
        {
            "name": "wp_actionscheduler_claims",
            "bytes": 32768,
            "rows": 0,
            "ownership": "active_action_scheduler"
        },
        {
            "name": "wp_actionscheduler_groups",
            "bytes": 32768,
            "rows": 8,
            "ownership": "active_action_scheduler"
        },
        {
            "name": "wp_actionscheduler_logs",
            "bytes": 49152,
            "rows": 38,
            "ownership": "active_action_scheduler"
        },
        {
            "name": "wp_commentmeta",
            "bytes": 49152,
            "rows": 15,
            "ownership": "wordpress"
        },
        {
            "name": "wp_comments",
            "bytes": 147456,
            "rows": 25,
            "ownership": "wordpress"
        },
        {
            "name": "wp_links",
            "bytes": 32768,
            "rows": 0,
            "ownership": "wordpress"
        },
        {
            "name": "wp_options",
            "bytes": 1228800,
            "rows": 430,
            "ownership": "wordpress"
        },
        {
            "name": "wp_postmeta",
            "bytes": 81920,
            "rows": 340,
            "ownership": "wordpress"
        },
        {
            "name": "wp_posts",
            "bytes": 147456,
            "rows": 28,
            "ownership": "wordpress"
        },
        {
            "name": "wp_termmeta",
            "bytes": 49152,
            "rows": 0,
            "ownership": "wordpress"
        },
        {
            "name": "wp_terms",
            "bytes": 49152,
            "rows": 17,
            "ownership": "wordpress"
        },
        {
            "name": "wp_term_relationships",
            "bytes": 32768,
            "rows": 3,
            "ownership": "wordpress"
        },
        {
            "name": "wp_term_taxonomy",
            "bytes": 49152,
            "rows": 17,
            "ownership": "wordpress"
        },
        {
            "name": "wp_usermeta",
            "bytes": 49152,
            "rows": 128,
            "ownership": "wordpress"
        },
        {
            "name": "wp_users",
            "bytes": 65536,
            "rows": 8,
            "ownership": "wordpress"
        },
        {
            "name": "wp_wcs_health_check_candidates",
            "bytes": 81920,
            "rows": 0,
            "ownership": "active_subscriptions"
        },
        {
            "name": "wp_wcs_health_check_runs",
            "bytes": 32768,
            "rows": 0,
            "ownership": "active_subscriptions"
        },
        {
            "name": "wp_wc_admin_notes",
            "bytes": 16384,
            "rows": 0,
            "ownership": "active_woocommerce"
        },
        {
            "name": "wp_wc_admin_note_actions",
            "bytes": 32768,
            "rows": 0,
            "ownership": "active_woocommerce"
        },
        {
            "name": "wp_wc_category_lookup",
            "bytes": 16384,
            "rows": 0,
            "ownership": "active_woocommerce"
        },
        {
            "name": "wp_wc_customer_lookup",
            "bytes": 49152,
            "rows": 0,
            "ownership": "active_woocommerce"
        },
        {
            "name": "wp_wc_download_log",
            "bytes": 49152,
            "rows": 0,
            "ownership": "active_woocommerce"
        },
        {
            "name": "wp_wc_email_unsubscribes",
            "bytes": 32768,
            "rows": 0,
            "ownership": "active_woocommerce"
        },
        {
            "name": "wp_wc_orders",
            "bytes": 163840,
            "rows": 0,
            "ownership": "active_woocommerce"
        },
        {
            "name": "wp_wc_orders_meta",
            "bytes": 49152,
            "rows": 0,
            "ownership": "active_woocommerce"
        },
        {
            "name": "wp_wc_order_addresses",
            "bytes": 81920,
            "rows": 0,
            "ownership": "active_woocommerce"
        },
        {
            "name": "wp_wc_order_coupon_lookup",
            "bytes": 49152,
            "rows": 0,
            "ownership": "active_woocommerce"
        },
        {
            "name": "wp_wc_order_operational_data",
            "bytes": 49152,
            "rows": 0,
            "ownership": "active_woocommerce"
        },
        {
            "name": "wp_wc_order_product_lookup",
            "bytes": 98304,
            "rows": 0,
            "ownership": "active_woocommerce"
        },
        {
            "name": "wp_wc_order_stats",
            "bytes": 81920,
            "rows": 0,
            "ownership": "active_woocommerce"
        },
        {
            "name": "wp_wc_order_tax_lookup",
            "bytes": 49152,
            "rows": 0,
            "ownership": "active_woocommerce"
        },
        {
            "name": "wp_wc_product_attributes_lookup",
            "bytes": 65536,
            "rows": 0,
            "ownership": "active_woocommerce"
        },
        {
            "name": "wp_wc_product_download_directories",
            "bytes": 32768,
            "rows": 2,
            "ownership": "active_woocommerce"
        },
        {
            "name": "wp_wc_product_meta_lookup",
            "bytes": 131072,
            "rows": 0,
            "ownership": "active_woocommerce"
        },
        {
            "name": "wp_wc_rate_limits",
            "bytes": 32768,
            "rows": 0,
            "ownership": "active_woocommerce"
        },
        {
            "name": "wp_wc_reserved_stock",
            "bytes": 32768,
            "rows": 0,
            "ownership": "active_woocommerce"
        },
        {
            "name": "wp_wc_tax_rate_classes",
            "bytes": 32768,
            "rows": 2,
            "ownership": "active_woocommerce"
        },
        {
            "name": "wp_wc_webhooks",
            "bytes": 32768,
            "rows": 0,
            "ownership": "active_woocommerce"
        },
        {
            "name": "wp_woocommerce_api_keys",
            "bytes": 49152,
            "rows": 0,
            "ownership": "active_woocommerce"
        },
        {
            "name": "wp_woocommerce_attribute_taxonomies",
            "bytes": 32768,
            "rows": 0,
            "ownership": "active_woocommerce"
        },
        {
            "name": "wp_woocommerce_downloadable_product_permissions",
            "bytes": 98304,
            "rows": 0,
            "ownership": "active_woocommerce"
        },
        {
            "name": "wp_woocommerce_log",
            "bytes": 32768,
            "rows": 0,
            "ownership": "active_woocommerce"
        },
        {
            "name": "wp_woocommerce_order_itemmeta",
            "bytes": 49152,
            "rows": 0,
            "ownership": "active_woocommerce"
        },
        {
            "name": "wp_woocommerce_order_items",
            "bytes": 32768,
            "rows": 0,
            "ownership": "active_woocommerce"
        },
        {
            "name": "wp_woocommerce_payment_tokenmeta",
            "bytes": 49152,
            "rows": 0,
            "ownership": "active_woocommerce"
        },
        {
            "name": "wp_woocommerce_payment_tokens",
            "bytes": 32768,
            "rows": 0,
            "ownership": "active_woocommerce"
        },
        {
            "name": "wp_woocommerce_sessions",
            "bytes": 49152,
            "rows": 0,
            "ownership": "active_woocommerce"
        },
        {
            "name": "wp_woocommerce_shipping_zones",
            "bytes": 32768,
            "rows": 0,
            "ownership": "active_woocommerce"
        },
        {
            "name": "wp_woocommerce_shipping_zone_locations",
            "bytes": 49152,
            "rows": 0,
            "ownership": "active_woocommerce"
        },
        {
            "name": "wp_woocommerce_shipping_zone_methods",
            "bytes": 49152,
            "rows": 0,
            "ownership": "active_woocommerce"
        },
        {
            "name": "wp_woocommerce_subscription_downloads",
            "bytes": 16384,
            "rows": 0,
            "ownership": "active_subscriptions"
        },
        {
            "name": "wp_woocommerce_tax_rates",
            "bytes": 81920,
            "rows": 0,
            "ownership": "active_woocommerce"
        },
        {
            "name": "wp_woocommerce_tax_rate_locations",
            "bytes": 49152,
            "rows": 0,
            "ownership": "active_woocommerce"
        }
    ],
    "total_bytes": 4276224,
    "largest_autoload": [
        {
            "name": "_transient_wp_core_block_css_files",
            "bytes": 22748
        },
        {
            "name": "wp_user_roles",
            "bytes": 9988
        },
        {
            "name": "cron",
            "bytes": 2348
        },
        {
            "name": "widget_block",
            "bytes": 890
        },
        {
            "name": "woocommerce_paypal_settings",
            "bytes": 861
        },
        {
            "name": "wc_memberships_rules",
            "bytes": 443
        },
        {
            "name": "active_plugins",
            "bytes": 207
        },
        {
            "name": "woocommerce_permalinks",
            "bytes": 182
        },
        {
            "name": "woocommerce_registration_privacy_policy_text",
            "bytes": 175
        },
        {
            "name": "wc_memberships_milestone_messages",
            "bytes": 168
        },
        {
            "name": "woocommerce_checkout_privacy_policy_text",
            "bytes": 161
        },
        {
            "name": "sidebars_widgets",
            "bytes": 154
        },
        {
            "name": "wc_memberships_profile_field_upload_allowed_file_types",
            "bytes": 69
        },
        {
            "name": "woocommerce_maxmind_geolocation_settings",
            "bytes": 69
        },
        {
            "name": "wc_subscriptions_siteurl",
            "bytes": 50
        },
        {
            "name": "woocommerce_subscriptions_customer_notifications_offset",
            "bytes": 49
        },
        {
            "name": "_transient_jetpack_autoloader_plugin_paths",
            "bytes": 47
        },
        {
            "name": "theme_mods_a03-fiction",
            "bytes": 38
        },
        {
            "name": "woocommerce_store_id",
            "bytes": 36
        },
        {
            "name": "woocommerce_maybe_regenerate_images_hash",
            "bytes": 32
        }
    ],
    "ownership_policy": "conservative_core_woo_wcs_as_registry; unknown_is_not_proof_of_orphan_never_delete",
    "size_basis": "information_schema_data_plus_indexes_estimate; exact_select_row_counts"
}
```

## 6. Planification

```json
{
    "actions_available": true,
    "actions": [
        {
            "hook": "a03_fixture_action",
            "status": "pending",
            "count": 1
        },
        {
            "hook": "action_scheduler/migration_hook",
            "status": "pending",
            "count": 1
        },
        {
            "hook": "wc-admin_import_orders",
            "status": "pending",
            "count": 4
        },
        {
            "hook": "wcs_report_update_cache",
            "status": "pending",
            "count": 4
        },
        {
            "hook": "wcs_schedule_pending_batch_processes",
            "status": "pending",
            "count": 1
        },
        {
            "hook": "woocommerce_delete_legacy_report_transients",
            "status": "pending",
            "count": 1
        },
        {
            "hook": "woocommerce_scheduled_subscription_customer_notification_expiration",
            "status": "pending",
            "count": 1
        },
        {
            "hook": "woocommerce_scheduled_subscription_customer_notification_renewal",
            "status": "canceled",
            "count": 5
        },
        {
            "hook": "woocommerce_scheduled_subscription_customer_notification_renewal",
            "status": "pending",
            "count": 1
        },
        {
            "hook": "woocommerce_scheduled_subscription_end_of_prepaid_term",
            "status": "canceled",
            "count": 1
        },
        {
            "hook": "woocommerce_scheduled_subscription_end_of_prepaid_term",
            "status": "pending",
            "count": 1
        },
        {
            "hook": "woocommerce_scheduled_subscription_payment",
            "status": "canceled",
            "count": 5
        },
        {
            "hook": "woocommerce_scheduled_subscription_payment",
            "status": "pending",
            "count": 1
        }
    ],
    "cron": [
        {
            "hook": "a08_orphan_hook",
            "schedule": "single",
            "count": 1,
            "next_epoch": 1795638699
        },
        {
            "hook": "action_scheduler_run_queue",
            "schedule": "every_minute",
            "count": 1,
            "next_epoch": 1795635085
        },
        {
            "hook": "do_pings",
            "schedule": "single",
            "count": 1,
            "next_epoch": 1795635093
        },
        {
            "hook": "jetpack_clean_nonces",
            "schedule": "hourly",
            "count": 1,
            "next_epoch": 1795635089
        },
        {
            "hook": "jetpack_v2_heartbeat",
            "schedule": "daily",
            "count": 1,
            "next_epoch": 1795635089
        },
        {
            "hook": "recovery_mode_clean_expired_keys",
            "schedule": "daily",
            "count": 1,
            "next_epoch": 1795635084
        },
        {
            "hook": "wc_admin_process_orders_milestone",
            "schedule": "hourly",
            "count": 1,
            "next_epoch": 1795635089
        },
        {
            "hook": "wc_memberships_jobs_cleanup",
            "schedule": "daily",
            "count": 1,
            "next_epoch": 1795652100
        },
        {
            "hook": "wp_1_wc_regenerate_images_cron",
            "schedule": "wp_1_wc_regenerate_images_cron_interval",
            "count": 1,
            "next_epoch": 1795635093
        },
        {
            "hook": "wp_privacy_delete_old_export_files",
            "schedule": "hourly",
            "count": 1,
            "next_epoch": 1795635085
        },
        {
            "hook": "wp_site_health_scheduled_check",
            "schedule": "weekly",
            "count": 1,
            "next_epoch": 1795721485
        },
        {
            "hook": "wp_update_plugins",
            "schedule": "twicedaily",
            "count": 1,
            "next_epoch": 1795640484
        },
        {
            "hook": "wp_update_themes",
            "schedule": "twicedaily",
            "count": 1,
            "next_epoch": 1795642284
        },
        {
            "hook": "wp_version_check",
            "schedule": "twicedaily",
            "count": 1,
            "next_epoch": 1795638684
        }
    ],
    "arguments_excluded": true
}
```

## 7. Risques de mise a niveau

```json
{
    "plugin_updates": [
        {
            "name": "a08-orphan/entry.php",
            "installed": "1.0.0",
            "latest": null,
            "update_available": null,
            "comparison": "unknown",
            "last_updated": null,
            "older_than_two_years": null
        },
        {
            "name": "akismet/akismet.php",
            "installed": "5.7",
            "latest": null,
            "update_available": null,
            "comparison": "unknown",
            "last_updated": null,
            "older_than_two_years": null
        },
        {
            "name": "hello.php",
            "installed": "1.7.2",
            "latest": null,
            "update_available": null,
            "comparison": "unknown",
            "last_updated": null,
            "older_than_two_years": null
        },
        {
            "name": "woocommerce-memberships/woocommerce-memberships.php",
            "installed": "1.30.3",
            "latest": null,
            "update_available": null,
            "comparison": "unknown",
            "last_updated": null,
            "older_than_two_years": null
        },
        {
            "name": "woocommerce-subscriptions/woocommerce-subscriptions.php",
            "installed": "9.4.1",
            "latest": null,
            "update_available": null,
            "comparison": "unknown",
            "last_updated": null,
            "older_than_two_years": null
        },
        {
            "name": "woocommerce/woocommerce.php",
            "installed": "11.0.1",
            "latest": null,
            "update_available": null,
            "comparison": "unknown",
            "last_updated": null,
            "older_than_two_years": null
        },
        {
            "name": "mu/000-imagine-staging-safety.php",
            "installed": null,
            "latest": null,
            "update_available": null,
            "comparison": "unknown",
            "last_updated": null,
            "older_than_two_years": null
        }
    ],
    "woocommerce_templates": [],
    "deprecated_functions": [],
    "debug_log_coverage": "absent",
    "deprecated_detection": "PHP Deprecated Function_or_Method_only_no_raw_lines",
    "staleness_unknown_when_no_cached_last_updated": true
}
```

## Limites

- Aucun reseau de mise a jour. Cache absent ou ancien ne prouve pas la derniere version ni la maintenance.
- Aucun bootstrap WordPress: types/taxonomies sans donnees et passerelles dynamiques non inferables; sources actives et base seulement.
- Regles Memberships enregistrees, pas une preuve des droits effectifs; verifier les parcours avant mise a niveau.
- Tables non attribuees: candidates a examiner, pas autorisation de supprimer; registre volontairement conservateur.
- Structure wp-content standard, configuration litterale et site simple requis; refuser plutot qu executer un fichier de configuration.

## Synthese — cinq points a regarder en premier

1. Verifier les compatibilites WordPress/PHP/Woo des extensions: 0 mise(s) a jour connue(s) en cache; inconnues a confirmer hors audit.

2. Rejouer les droits Memberships et le goutte-a-goutte avant changement; plans et regles sont inventories sans utilisateurs.

3. Tester renouvellements manuels et commandes dans le stockage faisant autorite (classic); controler passerelles et planification sans executer de tache.

4. Relire les surcharges WooCommerce: 0 perimee(s) par rapport au Woo installe; traiter les fonctions depreciees extraites.

5. Qualifier 1 table(s) non attribuee(s) et les options autoload lourdes avant tout nettoyage; ne rien supprimer sur cette seule indication.
