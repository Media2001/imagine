# Audit de l existant — lecture seule

Aucune valeur personnelle ou de reglage sensible. Inconnue signifie non observable sans reseau ou bootstrap.

## 1. Versions

```json
{
    "wordpress": "7.0.9",
    "php": "8.2.36",
    "php_sapi": "cli",
    "database": "10.11.19",
    "database_family": "MariaDB",
    "plugins": [
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
            "name": "fixture-builder/fixture-builder.php",
            "version": "1.0.0",
            "active": true,
            "kind": "plugin",
            "latest": "3.0.0",
            "requires_wp": "6.0",
            "requires_php": "8.2",
            "requires_woo": null,
            "requirements_source": "headers_or_literal_MINIMUM_constants_else_unknown",
            "latest_requires_wp": "6.9",
            "latest_requires_php": "8.2",
            "last_updated": "2020-01-01"
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
            "name": "inactive-fixture/inactive-fixture.php",
            "version": "0.5.0",
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
            "version": "11.1.1",
            "active": true,
            "kind": "plugin",
            "latest": null,
            "requires_wp": "7.0",
            "requires_php": "7.4",
            "requires_woo": null,
            "requirements_source": "headers_or_literal_MINIMUM_constants_else_unknown",
            "latest_requires_wp": null,
            "latest_requires_php": null,
            "last_updated": null
        },
        {
            "name": "mu/a02-fixture.php",
            "version": "1.0.0",
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
        },
        {
            "name": "mu/a11-fixture.php",
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
            "name": "a02-child",
            "version": "1.0.0",
            "active": true,
            "role": "stylesheet",
            "latest": null,
            "requires_wp": null,
            "requires_php": null,
            "latest_requires_wp": null,
            "latest_requires_php": null
        },
        {
            "name": "a02-theme",
            "version": "1.0.0",
            "active": true,
            "role": "template",
            "latest": "2.0.0",
            "requires_wp": "6.0",
            "requires_php": "8.2",
            "latest_requires_wp": "6.0",
            "latest_requires_php": "8.2"
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
    "plugin_cache_checked_epoch": 1795713934,
    "theme_cache_checked_epoch": 1795713934
}
```

## 2. Commerce

```json
{
    "order_storage": "classic",
    "order_year_basis": "UTC_creation",
    "gateways": [
        "a02_indirect",
        "bacs",
        "cheque",
        "cod",
        "paypal",
        "pre_install_woocommerce_payments_promotion"
    ],
    "gateway_detection": "static_active_source_ids_not_enabled_status_dynamic_ids_unknown",
    "gateway_unresolved": [
        {
            "plugin": "fixture-builder/fixture-builder.php",
            "class": "a02_dynamic",
            "reason": "id_unresolved"
        },
        {
            "plugin": "fixture-builder/fixture-builder.php",
            "class": "a02_missing",
            "reason": "ancestry_unresolved"
        },
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
            "status": "wc-on-hold",
            "period": "month",
            "interval": 2,
            "count": 1
        },
        {
            "status": "wc-pending-cancel",
            "period": "year",
            "interval": 3,
            "count": 1
        }
    ],
    "memberships": [
        {
            "plan_id": 13,
            "status": "wcm-active",
            "count": 1
        },
        {
            "plan_id": 13,
            "status": "wcm-cancelled",
            "count": 1
        },
        {
            "plan_id": 13,
            "status": "wcm-expired",
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
            "year": 2023,
            "count": 1
        },
        {
            "year": 2025,
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
            "id": 13,
            "status": "publish"
        }
    ],
    "rules": [
        {
            "plan_id": 13,
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
        },
        {
            "plan_id": 13,
            "active": true,
            "content_type": "taxonomy",
            "content_type_name": "category",
            "object_ids": [
                18
            ],
            "all_objects": false,
            "access_schedule": "after_membership_start",
            "drip": true,
            "amount": 7,
            "period": "day"
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
            "name": "a11_story",
            "count": 1
        },
        {
            "name": "attachment",
            "count": 4
        },
        {
            "name": "nav_menu_item",
            "count": 0
        },
        {
            "name": "page",
            "count": 4
        },
        {
            "name": "post",
            "count": 4
        },
        {
            "name": "product",
            "count": 1
        },
        {
            "name": "revision",
            "count": 0
        },
        {
            "name": "shop_order",
            "count": 3
        },
        {
            "name": "shop_subscription",
            "count": 3
        },
        {
            "name": "wc_membership_plan",
            "count": 1
        },
        {
            "name": "wc_user_membership",
            "count": 3
        }
    ],
    "taxonomies": [
        {
            "name": "a11_topic",
            "count": 2
        },
        {
            "name": "category",
            "count": 3
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
            "count": 2
        },
        {
            "name": "product_cat",
            "count": 2
        },
        {
            "name": "product_tag",
            "count": 2
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
            "count": 6
        },
        {
            "name": "_billing_email",
            "count": 6
        },
        {
            "name": "_cart_discount",
            "count": 6
        },
        {
            "name": "_cart_discount_tax",
            "count": 6
        },
        {
            "name": "_customer_user",
            "count": 6
        },
        {
            "name": "_download_permissions_granted",
            "count": 6
        },
        {
            "name": "_new_order_email_sent",
            "count": 6
        },
        {
            "name": "_order_currency",
            "count": 6
        },
        {
            "name": "_order_key",
            "count": 6
        },
        {
            "name": "_order_shipping",
            "count": 6
        },
        {
            "name": "_order_shipping_tax",
            "count": 6
        },
        {
            "name": "_order_stock_reduced",
            "count": 6
        },
        {
            "name": "_order_tax",
            "count": 6
        },
        {
            "name": "_order_total",
            "count": 6
        },
        {
            "name": "_order_version",
            "count": 6
        },
        {
            "name": "_prices_include_tax",
            "count": 6
        },
        {
            "name": "_recorded_coupon_usage_counts",
            "count": 6
        },
        {
            "name": "_recorded_sales",
            "count": 6
        },
        {
            "name": "_shipping_address_index",
            "count": 6
        },
        {
            "name": "_billing_first_name",
            "count": 3
        },
        {
            "name": "_billing_interval",
            "count": 3
        },
        {
            "name": "_billing_period",
            "count": 3
        },
        {
            "name": "_cancelled_email_sent",
            "count": 3
        },
        {
            "name": "_contains_synced_subscription",
            "count": 3
        },
        {
            "name": "_customer_ip_address",
            "count": 3
        },
        {
            "name": "_customer_user_agent",
            "count": 3
        },
        {
            "name": "_encloseme",
            "count": 3
        },
        {
            "name": "_end_date",
            "count": 3
        },
        {
            "name": "_last_order_date_created",
            "count": 3
        },
        {
            "name": "_pingme",
            "count": 3
        },
        {
            "name": "_requires_manual_renewal",
            "count": 3
        },
        {
            "name": "_schedule_cancelled",
            "count": 3
        },
        {
            "name": "_schedule_end",
            "count": 3
        },
        {
            "name": "_schedule_next_payment",
            "count": 3
        },
        {
            "name": "_schedule_payment_retry",
            "count": 3
        },
        {
            "name": "_schedule_start",
            "count": 3
        },
        {
            "name": "_schedule_trial_end",
            "count": 3
        },
        {
            "name": "_start_date",
            "count": 3
        },
        {
            "name": "_subscription_renewal_order_ids_cache",
            "count": 3
        },
        {
            "name": "_subscription_resubscribe_order_ids_cache",
            "count": 3
        },
        {
            "name": "_subscription_switch_data",
            "count": 3
        },
        {
            "name": "_subscription_switch_order_ids_cache",
            "count": 3
        },
        {
            "name": "_suspension_count",
            "count": 3
        },
        {
            "name": "_trial_period",
            "count": 3
        },
        {
            "name": "_access_length",
            "count": 1
        },
        {
            "name": "_access_method",
            "count": 1
        },
        {
            "name": "_backorders",
            "count": 1
        },
        {
            "name": "_download_expiry",
            "count": 1
        },
        {
            "name": "_download_limit",
            "count": 1
        },
        {
            "name": "_downloadable",
            "count": 1
        }
    ],
    "post_year_basis": "UTC_creation",
    "custom_fields_scope": "all_postmeta_keys_including_internal_core_and_woocommerce; names_and_counts_only",
    "posts_by_year": [
        {
            "year": 2025,
            "count": 4
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
            "name": "wp_actionscheduler_actions",
            "bytes": 163840,
            "rows": 26,
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
            "rows": 9,
            "ownership": "active_action_scheduler"
        },
        {
            "name": "wp_actionscheduler_logs",
            "bytes": 49152,
            "rows": 31,
            "ownership": "active_action_scheduler"
        },
        {
            "name": "wp_commentmeta",
            "bytes": 49152,
            "rows": 2,
            "ownership": "wordpress"
        },
        {
            "name": "wp_comments",
            "bytes": 147456,
            "rows": 7,
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
            "bytes": 1245184,
            "rows": 412,
            "ownership": "wordpress"
        },
        {
            "name": "wp_orphan_fixture",
            "bytes": 16384,
            "rows": 1,
            "ownership": "unattributed_candidate"
        },
        {
            "name": "wp_postmeta",
            "bytes": 49152,
            "rows": 210,
            "ownership": "wordpress"
        },
        {
            "name": "wp_posts",
            "bytes": 98304,
            "rows": 24,
            "ownership": "wordpress"
        },
        {
            "name": "wp_termmeta",
            "bytes": 49152,
            "rows": 2,
            "ownership": "wordpress"
        },
        {
            "name": "wp_terms",
            "bytes": 49152,
            "rows": 26,
            "ownership": "wordpress"
        },
        {
            "name": "wp_term_relationships",
            "bytes": 32768,
            "rows": 9,
            "ownership": "wordpress"
        },
        {
            "name": "wp_term_taxonomy",
            "bytes": 49152,
            "rows": 26,
            "ownership": "wordpress"
        },
        {
            "name": "wp_usermeta",
            "bytes": 49152,
            "rows": 121,
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
            "rows": 2,
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
            "rows": 1,
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
            "rows": 27,
            "ownership": "active_woocommerce"
        },
        {
            "name": "wp_woocommerce_order_items",
            "bytes": 32768,
            "rows": 3,
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
    "total_bytes": 4210688,
    "largest_autoload": [
        {
            "name": "a02_heavy_secret_setting",
            "bytes": 115000
        },
        {
            "name": "rewrite_rules",
            "bytes": 23781
        },
        {
            "name": "_transient_wp_core_block_css_files",
            "bytes": 22750
        },
        {
            "name": "wp_user_roles",
            "bytes": 9988
        },
        {
            "name": "cron",
            "bytes": 2197
        },
        {
            "name": "widget_block",
            "bytes": 890
        },
        {
            "name": "wc_memberships_rules",
            "bytes": 880
        },
        {
            "name": "woocommerce_paypal_settings",
            "bytes": 861
        },
        {
            "name": "a11_fixture_ids",
            "bytes": 295
        },
        {
            "name": "active_plugins",
            "bytes": 222
        },
        {
            "name": "sidebars_widgets",
            "bytes": 198
        },
        {
            "name": "woocommerce_permalinks",
            "bytes": 198
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
            "name": "woocommerce_bacs_settings",
            "bytes": 75
        },
        {
            "name": "woocommerce_maxmind_geolocation_settings",
            "bytes": 69
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
            "name": "woocommerce_store_id",
            "bytes": 36
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
            "hook": "a02_fixture_action",
            "status": "pending",
            "count": 1
        },
        {
            "hook": "a02_fixture_failed",
            "status": "failed",
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
            "count": 3
        },
        {
            "hook": "wcs_report_update_cache",
            "status": "pending",
            "count": 5
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
            "hook": "woocommerce_run_product_attribute_lookup_update_callback",
            "status": "pending",
            "count": 3
        },
        {
            "hook": "woocommerce_run_update_callback",
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
            "count": 2
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
            "count": 2
        },
        {
            "hook": "woocommerce_scheduled_subscription_payment",
            "status": "pending",
            "count": 1
        }
    ],
    "cron": [
        {
            "hook": "a02_fixture_cron",
            "schedule": "daily",
            "count": 1,
            "next_epoch": 1795717534
        },
        {
            "hook": "action_scheduler_run_queue",
            "schedule": "every_minute",
            "count": 1,
            "next_epoch": 1795713924
        },
        {
            "hook": "do_pings",
            "schedule": "single",
            "count": 1,
            "next_epoch": 1795713932
        },
        {
            "hook": "jetpack_clean_nonces",
            "schedule": "hourly",
            "count": 1,
            "next_epoch": 1795713928
        },
        {
            "hook": "jetpack_v2_heartbeat",
            "schedule": "daily",
            "count": 1,
            "next_epoch": 1795713928
        },
        {
            "hook": "recovery_mode_clean_expired_keys",
            "schedule": "daily",
            "count": 1,
            "next_epoch": 1795713924
        },
        {
            "hook": "wc_admin_process_orders_milestone",
            "schedule": "hourly",
            "count": 1,
            "next_epoch": 1795713928
        },
        {
            "hook": "wc_memberships_jobs_cleanup",
            "schedule": "daily",
            "count": 1,
            "next_epoch": 1795738500
        },
        {
            "hook": "wp_privacy_delete_old_export_files",
            "schedule": "hourly",
            "count": 1,
            "next_epoch": 1795713924
        },
        {
            "hook": "wp_site_health_scheduled_check",
            "schedule": "weekly",
            "count": 1,
            "next_epoch": 1795800324
        },
        {
            "hook": "wp_update_plugins",
            "schedule": "twicedaily",
            "count": 1,
            "next_epoch": 1795719323
        },
        {
            "hook": "wp_update_themes",
            "schedule": "twicedaily",
            "count": 1,
            "next_epoch": 1795721123
        },
        {
            "hook": "wp_version_check",
            "schedule": "twicedaily",
            "count": 1,
            "next_epoch": 1795717523
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
            "name": "akismet/akismet.php",
            "installed": "5.7",
            "latest": null,
            "update_available": null,
            "comparison": "unknown",
            "last_updated": null,
            "older_than_two_years": null
        },
        {
            "name": "fixture-builder/fixture-builder.php",
            "installed": "1.0.0",
            "latest": "3.0.0",
            "update_available": true,
            "comparison": "behind_cached_latest",
            "last_updated": "2020-01-01",
            "older_than_two_years": true
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
            "name": "inactive-fixture/inactive-fixture.php",
            "installed": "0.5.0",
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
            "installed": "11.1.1",
            "latest": null,
            "update_available": null,
            "comparison": "unknown",
            "last_updated": null,
            "older_than_two_years": null
        },
        {
            "name": "mu/a02-fixture.php",
            "installed": "1.0.0",
            "latest": null,
            "update_available": null,
            "comparison": "unknown",
            "last_updated": null,
            "older_than_two_years": null
        },
        {
            "name": "mu/a11-fixture.php",
            "installed": null,
            "latest": null,
            "update_available": null,
            "comparison": "unknown",
            "last_updated": null,
            "older_than_two_years": null
        }
    ],
    "woocommerce_templates": [
        {
            "theme": "a02-child",
            "file": "myaccount/form-login.php",
            "effective": true,
            "resolution": "effective",
            "override_version": "9.9.0",
            "installed_woo_template_version": "9.9.0",
            "outdated": false
        },
        {
            "theme": "a02-theme",
            "file": "checkout/form-checkout.php",
            "effective": true,
            "resolution": "effective",
            "override_version": "1.0.0",
            "installed_woo_template_version": "9.4.0",
            "outdated": true
        },
        {
            "theme": "a02-theme",
            "file": "myaccount/form-login.php",
            "effective": false,
            "resolution": "masked_by_child",
            "override_version": "1.0.0",
            "installed_woo_template_version": "9.9.0",
            "outdated": true
        }
    ],
    "deprecated_functions": [
        {
            "function": "a02_legacy_function",
            "count": 1
        }
    ],
    "debug_log_coverage": "complete",
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

1. Verifier les compatibilites WordPress/PHP/Woo des extensions: 1 mise(s) a jour connue(s) en cache; inconnues a confirmer hors audit.

2. Rejouer les droits Memberships et le goutte-a-goutte avant changement; plans et regles sont inventories sans utilisateurs.

3. Tester renouvellements manuels et commandes dans le stockage faisant autorite (classic); controler passerelles et planification sans executer de tache.

4. Relire les surcharges WooCommerce: 1 perimee(s) par rapport au Woo installe; traiter les fonctions depreciees extraites.

5. Qualifier 1 table(s) non attribuee(s) et les options autoload lourdes avant tout nettoyage; ne rien supprimer sur cette seule indication.
