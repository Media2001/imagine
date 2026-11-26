# Structure des contenus — lecture seule

Registre natif apres wp_loaded. Declarants observes pendant les enregistrements effectifs. Aucune decision de rattachement.

```json
{
    "schema": "imagine-a12-content-v1",
    "read_only": true,
    "storage": "classic",
    "registry": {
        "runtime_verified": true,
        "coverage": "native_registry_after_wp_loaded_plus_separately_marked_stored_only_objects",
        "post_type_count": 30,
        "taxonomy_count": 19,
        "session": "same_readonly_wpdb_from_before_bootstrap_through_all_aggregates"
    },
    "post_types": [
        {
            "name": "a12_article",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "mu_plugin",
                    "file": "wp-content\/mu-plugins\/a12-declarations.php"
                }
            ],
            "content_count": 5,
            "states": {
                "draft": 1,
                "private": 1,
                "publish": 2,
                "trash": 1
            },
            "first_published_utc": "2024-02-03T11:00:00Z",
            "last_published_utc": "2025-02-03T11:00:00Z",
            "metadata_keys": [
                {
                    "key": "_A12_product_id",
                    "content_count": 1
                },
                {
                    "key": "_a12_product_id",
                    "content_count": 3
                },
                {
                    "key": "_a12_product_ids",
                    "content_count": 1
                },
                {
                    "key": "a12_field",
                    "content_count": 5
                }
            ]
        },
        {
            "name": "a12_dynamic",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "mu_plugin",
                    "file": "wp-content\/mu-plugins\/a12-declarations.php"
                }
            ],
            "content_count": 0,
            "states": [],
            "first_published_utc": null,
            "last_published_utc": null,
            "metadata_keys": []
        },
        {
            "name": "a12_empty",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "mu_plugin",
                    "file": "wp-content\/mu-plugins\/a12-declarations.php"
                }
            ],
            "content_count": 0,
            "states": [],
            "first_published_utc": null,
            "last_published_utc": null,
            "metadata_keys": []
        },
        {
            "name": "a12_theme",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "theme",
                    "file": "wp-content\/themes\/a02-child\/functions.php"
                }
            ],
            "content_count": 0,
            "states": [],
            "first_published_utc": null,
            "last_published_utc": null,
            "metadata_keys": []
        },
        {
            "name": "attachment",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "core",
                    "file": "wp-includes\/post.php"
                }
            ],
            "content_count": 4,
            "states": {
                "inherit": 4
            },
            "first_published_utc": null,
            "last_published_utc": null,
            "metadata_keys": [
                {
                    "key": "_wp_attached_file",
                    "content_count": 4
                },
                {
                    "key": "_wp_attachment_metadata",
                    "content_count": 1
                }
            ]
        },
        {
            "name": "custom_css",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "core",
                    "file": "wp-includes\/post.php"
                }
            ],
            "content_count": 0,
            "states": [],
            "first_published_utc": null,
            "last_published_utc": null,
            "metadata_keys": []
        },
        {
            "name": "customize_changeset",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "core",
                    "file": "wp-includes\/post.php"
                }
            ],
            "content_count": 0,
            "states": [],
            "first_published_utc": null,
            "last_published_utc": null,
            "metadata_keys": []
        },
        {
            "name": "nav_menu_item",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "core",
                    "file": "wp-includes\/post.php"
                }
            ],
            "content_count": 0,
            "states": [],
            "first_published_utc": null,
            "last_published_utc": null,
            "metadata_keys": []
        },
        {
            "name": "oembed_cache",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "core",
                    "file": "wp-includes\/post.php"
                }
            ],
            "content_count": 0,
            "states": [],
            "first_published_utc": null,
            "last_published_utc": null,
            "metadata_keys": []
        },
        {
            "name": "page",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "core",
                    "file": "wp-includes\/post.php"
                }
            ],
            "content_count": 7,
            "states": {
                "draft": 2,
                "publish": 5
            },
            "first_published_utc": "2026-11-26T02:03:43Z",
            "last_published_utc": "2026-11-26T02:03:47Z",
            "metadata_keys": [
                {
                    "key": "_wp_page_template",
                    "content_count": 2
                }
            ]
        },
        {
            "name": "post",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "core",
                    "file": "wp-includes\/post.php"
                }
            ],
            "content_count": 4,
            "states": {
                "publish": 4
            },
            "first_published_utc": "2023-12-31T23:30:00Z",
            "last_published_utc": "2026-11-26T02:03:43Z",
            "metadata_keys": [
                {
                    "key": "_encloseme",
                    "content_count": 3
                },
                {
                    "key": "_pingme",
                    "content_count": 3
                },
                {
                    "key": "a02_editorial_field",
                    "content_count": 3
                }
            ]
        },
        {
            "name": "product",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "plugin",
                    "file": "wp-content\/plugins\/woocommerce\/includes\/class-wc-post-types.php"
                }
            ],
            "content_count": 2,
            "states": {
                "publish": 2
            },
            "first_published_utc": "2026-11-26T02:03:52Z",
            "last_published_utc": "2026-11-26T02:03:55Z",
            "metadata_keys": [
                {
                    "key": "_a12_article_id",
                    "content_count": 1
                },
                {
                    "key": "_backorders",
                    "content_count": 2
                },
                {
                    "key": "_download_expiry",
                    "content_count": 2
                },
                {
                    "key": "_download_limit",
                    "content_count": 2
                },
                {
                    "key": "_downloadable",
                    "content_count": 2
                },
                {
                    "key": "_manage_stock",
                    "content_count": 2
                },
                {
                    "key": "_price",
                    "content_count": 2
                },
                {
                    "key": "_product_version",
                    "content_count": 2
                },
                {
                    "key": "_regular_price",
                    "content_count": 2
                },
                {
                    "key": "_sold_individually",
                    "content_count": 2
                },
                {
                    "key": "_stock",
                    "content_count": 2
                },
                {
                    "key": "_stock_status",
                    "content_count": 2
                },
                {
                    "key": "_subscription_payment_sync_date",
                    "content_count": 1
                },
                {
                    "key": "_subscription_period",
                    "content_count": 1
                },
                {
                    "key": "_subscription_period_interval",
                    "content_count": 1
                },
                {
                    "key": "_subscription_sign_up_fee",
                    "content_count": 1
                },
                {
                    "key": "_subscription_trial_length",
                    "content_count": 1
                },
                {
                    "key": "_subscription_trial_period",
                    "content_count": 1
                },
                {
                    "key": "_tax_class",
                    "content_count": 2
                },
                {
                    "key": "_tax_status",
                    "content_count": 2
                },
                {
                    "key": "_virtual",
                    "content_count": 2
                },
                {
                    "key": "_wc_average_rating",
                    "content_count": 2
                },
                {
                    "key": "_wc_review_count",
                    "content_count": 2
                },
                {
                    "key": "total_sales",
                    "content_count": 2
                }
            ]
        },
        {
            "name": "product_variation",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "plugin",
                    "file": "wp-content\/plugins\/woocommerce\/includes\/class-wc-post-types.php"
                }
            ],
            "content_count": 0,
            "states": [],
            "first_published_utc": null,
            "last_published_utc": null,
            "metadata_keys": []
        },
        {
            "name": "revision",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "core",
                    "file": "wp-includes\/post.php"
                }
            ],
            "content_count": 0,
            "states": [],
            "first_published_utc": null,
            "last_published_utc": null,
            "metadata_keys": []
        },
        {
            "name": "scheduled-action",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "plugin",
                    "file": "wp-content\/plugins\/woocommerce\/packages\/action-scheduler\/classes\/data-stores\/ActionScheduler_wpPostStore_PostTypeRegistrar.php"
                }
            ],
            "content_count": 0,
            "states": [],
            "first_published_utc": null,
            "last_published_utc": null,
            "metadata_keys": []
        },
        {
            "name": "shop_coupon",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "plugin",
                    "file": "wp-content\/plugins\/woocommerce\/includes\/class-wc-post-types.php"
                }
            ],
            "content_count": 0,
            "states": [],
            "first_published_utc": null,
            "last_published_utc": null,
            "metadata_keys": []
        },
        {
            "name": "shop_order",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "plugin",
                    "file": "wp-content\/plugins\/woocommerce\/includes\/wc-order-functions.php"
                }
            ],
            "content_count": 3,
            "states": {
                "wc-pending": 3
            },
            "first_published_utc": null,
            "last_published_utc": null,
            "metadata_keys": [
                {
                    "key": "_billing_address_index",
                    "content_count": 3
                },
                {
                    "key": "_billing_email",
                    "content_count": 3
                },
                {
                    "key": "_cart_discount",
                    "content_count": 3
                },
                {
                    "key": "_cart_discount_tax",
                    "content_count": 3
                },
                {
                    "key": "_customer_ip_address",
                    "content_count": 3
                },
                {
                    "key": "_customer_user",
                    "content_count": 3
                },
                {
                    "key": "_customer_user_agent",
                    "content_count": 3
                },
                {
                    "key": "_download_permissions_granted",
                    "content_count": 3
                },
                {
                    "key": "_new_order_email_sent",
                    "content_count": 3
                },
                {
                    "key": "_order_currency",
                    "content_count": 3
                },
                {
                    "key": "_order_key",
                    "content_count": 3
                },
                {
                    "key": "_order_shipping",
                    "content_count": 3
                },
                {
                    "key": "_order_shipping_tax",
                    "content_count": 3
                },
                {
                    "key": "_order_stock_reduced",
                    "content_count": 3
                },
                {
                    "key": "_order_tax",
                    "content_count": 3
                },
                {
                    "key": "_order_total",
                    "content_count": 3
                },
                {
                    "key": "_order_version",
                    "content_count": 3
                },
                {
                    "key": "_prices_include_tax",
                    "content_count": 3
                },
                {
                    "key": "_recorded_coupon_usage_counts",
                    "content_count": 3
                },
                {
                    "key": "_recorded_sales",
                    "content_count": 3
                },
                {
                    "key": "_shipping_address_index",
                    "content_count": 3
                }
            ]
        },
        {
            "name": "shop_order_placehold",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "plugin",
                    "file": "wp-content\/plugins\/woocommerce\/includes\/wc-order-functions.php"
                }
            ],
            "content_count": 0,
            "states": [],
            "first_published_utc": null,
            "last_published_utc": null,
            "metadata_keys": []
        },
        {
            "name": "shop_order_refund",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "plugin",
                    "file": "wp-content\/plugins\/woocommerce\/includes\/wc-order-functions.php"
                }
            ],
            "content_count": 0,
            "states": [],
            "first_published_utc": null,
            "last_published_utc": null,
            "metadata_keys": []
        },
        {
            "name": "shop_subscription",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "plugin",
                    "file": "wp-content\/plugins\/woocommerce\/includes\/wc-order-functions.php"
                }
            ],
            "content_count": 3,
            "states": {
                "wc-active": 1,
                "wc-on-hold": 1,
                "wc-pending-cancel": 1
            },
            "first_published_utc": null,
            "last_published_utc": null,
            "metadata_keys": [
                {
                    "key": "_billing_address_index",
                    "content_count": 3
                },
                {
                    "key": "_billing_email",
                    "content_count": 3
                },
                {
                    "key": "_billing_first_name",
                    "content_count": 3
                },
                {
                    "key": "_billing_interval",
                    "content_count": 3
                },
                {
                    "key": "_billing_period",
                    "content_count": 3
                },
                {
                    "key": "_cancelled_email_sent",
                    "content_count": 3
                },
                {
                    "key": "_cart_discount",
                    "content_count": 3
                },
                {
                    "key": "_cart_discount_tax",
                    "content_count": 3
                },
                {
                    "key": "_contains_synced_subscription",
                    "content_count": 3
                },
                {
                    "key": "_customer_user",
                    "content_count": 3
                },
                {
                    "key": "_download_permissions_granted",
                    "content_count": 3
                },
                {
                    "key": "_last_order_date_created",
                    "content_count": 3
                },
                {
                    "key": "_new_order_email_sent",
                    "content_count": 3
                },
                {
                    "key": "_order_currency",
                    "content_count": 3
                },
                {
                    "key": "_order_key",
                    "content_count": 3
                },
                {
                    "key": "_order_shipping",
                    "content_count": 3
                },
                {
                    "key": "_order_shipping_tax",
                    "content_count": 3
                },
                {
                    "key": "_order_stock_reduced",
                    "content_count": 3
                },
                {
                    "key": "_order_tax",
                    "content_count": 3
                },
                {
                    "key": "_order_total",
                    "content_count": 3
                },
                {
                    "key": "_order_version",
                    "content_count": 3
                },
                {
                    "key": "_prices_include_tax",
                    "content_count": 3
                },
                {
                    "key": "_recorded_coupon_usage_counts",
                    "content_count": 3
                },
                {
                    "key": "_recorded_sales",
                    "content_count": 3
                },
                {
                    "key": "_requires_manual_renewal",
                    "content_count": 3
                },
                {
                    "key": "_schedule_cancelled",
                    "content_count": 3
                },
                {
                    "key": "_schedule_end",
                    "content_count": 3
                },
                {
                    "key": "_schedule_next_payment",
                    "content_count": 3
                },
                {
                    "key": "_schedule_payment_retry",
                    "content_count": 3
                },
                {
                    "key": "_schedule_start",
                    "content_count": 3
                },
                {
                    "key": "_schedule_trial_end",
                    "content_count": 3
                },
                {
                    "key": "_shipping_address_index",
                    "content_count": 3
                },
                {
                    "key": "_subscription_renewal_order_ids_cache",
                    "content_count": 3
                },
                {
                    "key": "_subscription_resubscribe_order_ids_cache",
                    "content_count": 3
                },
                {
                    "key": "_subscription_switch_data",
                    "content_count": 3
                },
                {
                    "key": "_subscription_switch_order_ids_cache",
                    "content_count": 3
                },
                {
                    "key": "_suspension_count",
                    "content_count": 3
                },
                {
                    "key": "_trial_period",
                    "content_count": 3
                },
                {
                    "key": "end_date_pre_cancellation",
                    "content_count": 1
                },
                {
                    "key": "trial_end_pre_cancellation",
                    "content_count": 1
                }
            ]
        },
        {
            "name": "user_request",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "core",
                    "file": "wp-includes\/post.php"
                }
            ],
            "content_count": 0,
            "states": [],
            "first_published_utc": null,
            "last_published_utc": null,
            "metadata_keys": []
        },
        {
            "name": "wc_membership_plan",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "plugin",
                    "file": "wp-content\/plugins\/woocommerce-memberships\/src\/class-wc-memberships-post-types.php"
                }
            ],
            "content_count": 1,
            "states": {
                "publish": 1
            },
            "first_published_utc": "2026-11-26T02:03:52Z",
            "last_published_utc": "2026-11-26T02:03:52Z",
            "metadata_keys": [
                {
                    "key": "_access_length",
                    "content_count": 1
                },
                {
                    "key": "_access_method",
                    "content_count": 1
                }
            ]
        },
        {
            "name": "wc_user_membership",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "plugin",
                    "file": "wp-content\/plugins\/woocommerce-memberships\/src\/class-wc-memberships-post-types.php"
                }
            ],
            "content_count": 3,
            "states": {
                "wcm-active": 1,
                "wcm-cancelled": 1,
                "wcm-expired": 1
            },
            "first_published_utc": null,
            "last_published_utc": null,
            "metadata_keys": [
                {
                    "key": "_end_date",
                    "content_count": 3
                },
                {
                    "key": "_start_date",
                    "content_count": 3
                }
            ]
        },
        {
            "name": "wp_block",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "core",
                    "file": "wp-includes\/post.php"
                }
            ],
            "content_count": 0,
            "states": [],
            "first_published_utc": null,
            "last_published_utc": null,
            "metadata_keys": []
        },
        {
            "name": "wp_font_face",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "core",
                    "file": "wp-includes\/post.php"
                }
            ],
            "content_count": 0,
            "states": [],
            "first_published_utc": null,
            "last_published_utc": null,
            "metadata_keys": []
        },
        {
            "name": "wp_font_family",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "core",
                    "file": "wp-includes\/post.php"
                }
            ],
            "content_count": 0,
            "states": [],
            "first_published_utc": null,
            "last_published_utc": null,
            "metadata_keys": []
        },
        {
            "name": "wp_global_styles",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "core",
                    "file": "wp-includes\/post.php"
                }
            ],
            "content_count": 0,
            "states": [],
            "first_published_utc": null,
            "last_published_utc": null,
            "metadata_keys": []
        },
        {
            "name": "wp_navigation",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "core",
                    "file": "wp-includes\/post.php"
                }
            ],
            "content_count": 0,
            "states": [],
            "first_published_utc": null,
            "last_published_utc": null,
            "metadata_keys": []
        },
        {
            "name": "wp_template",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "core",
                    "file": "wp-includes\/post.php"
                }
            ],
            "content_count": 0,
            "states": [],
            "first_published_utc": null,
            "last_published_utc": null,
            "metadata_keys": []
        },
        {
            "name": "wp_template_part",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "core",
                    "file": "wp-includes\/post.php"
                }
            ],
            "content_count": 0,
            "states": [],
            "first_published_utc": null,
            "last_published_utc": null,
            "metadata_keys": []
        }
    ],
    "taxonomies": [
        {
            "name": "a12_dynamic_tax",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "mu_plugin",
                    "file": "wp-content\/mu-plugins\/a12-declarations.php"
                }
            ],
            "object_types": [
                "a12_article"
            ],
            "count_status": "qualified_posts_domain",
            "content_count": 0,
            "states": [],
            "first_published_utc": null,
            "last_published_utc": null,
            "top_terms": [],
            "term_count": 0
        },
        {
            "name": "a12_mixed_tax",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "mu_plugin",
                    "file": "wp-content\/mu-plugins\/a12-declarations.php"
                }
            ],
            "object_types": [
                "a12_article",
                "link"
            ],
            "count_status": "unavailable_non_posts_or_mixed",
            "content_count": null,
            "states": null,
            "first_published_utc": null,
            "last_published_utc": null,
            "top_terms": null,
            "term_count": 1
        },
        {
            "name": "a12_rubrique",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "mu_plugin",
                    "file": "wp-content\/mu-plugins\/a12-declarations.php"
                }
            ],
            "object_types": [
                "a12_article"
            ],
            "count_status": "qualified_posts_domain",
            "content_count": 4,
            "states": {
                "draft": 1,
                "private": 1,
                "publish": 2
            },
            "first_published_utc": "2024-02-03T11:00:00Z",
            "last_published_utc": "2025-02-03T11:00:00Z",
            "top_terms": [
                {
                    "name": "Rubrique fictive 01",
                    "content_count": 3
                },
                {
                    "name": "Rubrique fictive 02",
                    "content_count": 2
                },
                {
                    "name": "Rubrique fictive 03",
                    "content_count": 0
                },
                {
                    "name": "Rubrique fictive 04",
                    "content_count": 0
                },
                {
                    "name": "Rubrique fictive 05",
                    "content_count": 0
                },
                {
                    "name": "Rubrique fictive 06",
                    "content_count": 0
                },
                {
                    "name": "Rubrique fictive 07",
                    "content_count": 0
                },
                {
                    "name": "Rubrique fictive 08",
                    "content_count": 0
                },
                {
                    "name": "Rubrique fictive 09",
                    "content_count": 0
                },
                {
                    "name": "Rubrique fictive 10",
                    "content_count": 0
                },
                {
                    "name": "Rubrique fictive 11",
                    "content_count": 0
                },
                {
                    "name": "Rubrique fictive 12",
                    "content_count": 0
                },
                {
                    "name": "Rubrique fictive 13",
                    "content_count": 0
                },
                {
                    "name": "Rubrique fictive 14",
                    "content_count": 0
                },
                {
                    "name": "Rubrique fictive 15",
                    "content_count": 0
                },
                {
                    "name": "Rubrique fictive 16",
                    "content_count": 0
                },
                {
                    "name": "Rubrique fictive 17",
                    "content_count": 0
                },
                {
                    "name": "Rubrique fictive 18",
                    "content_count": 0
                },
                {
                    "name": "Rubrique fictive 19",
                    "content_count": 0
                },
                {
                    "name": "Rubrique fictive 20",
                    "content_count": 0
                }
            ],
            "term_count": 23
        },
        {
            "name": "action-group",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "plugin",
                    "file": "wp-content\/plugins\/woocommerce\/packages\/action-scheduler\/classes\/data-stores\/ActionScheduler_wpPostStore_TaxonomyRegistrar.php"
                }
            ],
            "object_types": [
                "scheduled-action"
            ],
            "count_status": "qualified_posts_domain",
            "content_count": 0,
            "states": [],
            "first_published_utc": null,
            "last_published_utc": null,
            "top_terms": [],
            "term_count": 0
        },
        {
            "name": "category",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "core",
                    "file": "wp-includes\/taxonomy.php"
                }
            ],
            "object_types": [
                "post"
            ],
            "count_status": "qualified_posts_domain",
            "content_count": 4,
            "states": {
                "publish": 4
            },
            "first_published_utc": "2023-12-31T23:30:00Z",
            "last_published_utc": "2026-11-26T02:03:43Z",
            "top_terms": [
                {
                    "name": "Uncategorized",
                    "content_count": 4
                },
                {
                    "name": "Rubrique A02 fictive",
                    "content_count": 0
                }
            ],
            "term_count": 2
        },
        {
            "name": "link_category",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "core",
                    "file": "wp-includes\/taxonomy.php"
                }
            ],
            "object_types": [
                "link"
            ],
            "count_status": "unavailable_non_posts_or_mixed",
            "content_count": null,
            "states": null,
            "first_published_utc": null,
            "last_published_utc": null,
            "top_terms": null,
            "term_count": 1
        },
        {
            "name": "nav_menu",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "core",
                    "file": "wp-includes\/taxonomy.php"
                }
            ],
            "object_types": [
                "nav_menu_item"
            ],
            "count_status": "qualified_posts_domain",
            "content_count": 0,
            "states": [],
            "first_published_utc": null,
            "last_published_utc": null,
            "top_terms": [],
            "term_count": 0
        },
        {
            "name": "pos_product_visibility",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "plugin",
                    "file": "wp-content\/plugins\/woocommerce\/includes\/class-wc-post-types.php"
                }
            ],
            "object_types": [
                "product",
                "product_variation"
            ],
            "count_status": "qualified_posts_domain",
            "content_count": 0,
            "states": [],
            "first_published_utc": null,
            "last_published_utc": null,
            "top_terms": [],
            "term_count": 0
        },
        {
            "name": "post_format",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "core",
                    "file": "wp-includes\/taxonomy.php"
                }
            ],
            "object_types": [
                "post"
            ],
            "count_status": "qualified_posts_domain",
            "content_count": 0,
            "states": [],
            "first_published_utc": null,
            "last_published_utc": null,
            "top_terms": [],
            "term_count": 0
        },
        {
            "name": "post_tag",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "core",
                    "file": "wp-includes\/taxonomy.php"
                }
            ],
            "object_types": [
                "post"
            ],
            "count_status": "qualified_posts_domain",
            "content_count": 0,
            "states": [],
            "first_published_utc": null,
            "last_published_utc": null,
            "top_terms": [],
            "term_count": 0
        },
        {
            "name": "product_brand",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "plugin",
                    "file": "wp-content\/plugins\/woocommerce\/includes\/class-wc-brands.php"
                }
            ],
            "object_types": [
                "product"
            ],
            "count_status": "qualified_posts_domain",
            "content_count": 0,
            "states": [],
            "first_published_utc": null,
            "last_published_utc": null,
            "top_terms": [],
            "term_count": 0
        },
        {
            "name": "product_cat",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "plugin",
                    "file": "wp-content\/plugins\/woocommerce\/includes\/class-wc-post-types.php"
                }
            ],
            "object_types": [
                "product"
            ],
            "count_status": "qualified_posts_domain",
            "content_count": 2,
            "states": {
                "publish": 2
            },
            "first_published_utc": "2026-11-26T02:03:52Z",
            "last_published_utc": "2026-11-26T02:03:55Z",
            "top_terms": [
                {
                    "name": "Uncategorized",
                    "content_count": 2
                }
            ],
            "term_count": 1
        },
        {
            "name": "product_shipping_class",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "plugin",
                    "file": "wp-content\/plugins\/woocommerce\/includes\/class-wc-post-types.php"
                }
            ],
            "object_types": [
                "product",
                "product_variation"
            ],
            "count_status": "qualified_posts_domain",
            "content_count": 0,
            "states": [],
            "first_published_utc": null,
            "last_published_utc": null,
            "top_terms": [],
            "term_count": 0
        },
        {
            "name": "product_tag",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "plugin",
                    "file": "wp-content\/plugins\/woocommerce\/includes\/class-wc-post-types.php"
                }
            ],
            "object_types": [
                "product"
            ],
            "count_status": "qualified_posts_domain",
            "content_count": 0,
            "states": [],
            "first_published_utc": null,
            "last_published_utc": null,
            "top_terms": [],
            "term_count": 0
        },
        {
            "name": "product_type",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "plugin",
                    "file": "wp-content\/plugins\/woocommerce\/includes\/class-wc-post-types.php"
                }
            ],
            "object_types": [
                "product"
            ],
            "count_status": "qualified_posts_domain",
            "content_count": 2,
            "states": {
                "publish": 2
            },
            "first_published_utc": "2026-11-26T02:03:52Z",
            "last_published_utc": "2026-11-26T02:03:55Z",
            "top_terms": [
                {
                    "name": "simple",
                    "content_count": 1
                },
                {
                    "name": "subscription",
                    "content_count": 1
                },
                {
                    "name": "Variable Subscription",
                    "content_count": 0
                },
                {
                    "name": "external",
                    "content_count": 0
                },
                {
                    "name": "grouped",
                    "content_count": 0
                },
                {
                    "name": "variable",
                    "content_count": 0
                }
            ],
            "term_count": 6
        },
        {
            "name": "product_visibility",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "plugin",
                    "file": "wp-content\/plugins\/woocommerce\/includes\/class-wc-post-types.php"
                }
            ],
            "object_types": [
                "product",
                "product_variation"
            ],
            "count_status": "qualified_posts_domain",
            "content_count": 0,
            "states": [],
            "first_published_utc": null,
            "last_published_utc": null,
            "top_terms": [
                {
                    "name": "exclude-from-catalog",
                    "content_count": 0
                },
                {
                    "name": "exclude-from-search",
                    "content_count": 0
                },
                {
                    "name": "featured",
                    "content_count": 0
                },
                {
                    "name": "outofstock",
                    "content_count": 0
                },
                {
                    "name": "rated-1",
                    "content_count": 0
                },
                {
                    "name": "rated-2",
                    "content_count": 0
                },
                {
                    "name": "rated-3",
                    "content_count": 0
                },
                {
                    "name": "rated-4",
                    "content_count": 0
                },
                {
                    "name": "rated-5",
                    "content_count": 0
                }
            ],
            "term_count": 9
        },
        {
            "name": "wp_pattern_category",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "core",
                    "file": "wp-includes\/taxonomy.php"
                }
            ],
            "object_types": [
                "wp_block"
            ],
            "count_status": "qualified_posts_domain",
            "content_count": 0,
            "states": [],
            "first_published_utc": null,
            "last_published_utc": null,
            "top_terms": [],
            "term_count": 0
        },
        {
            "name": "wp_template_part_area",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "core",
                    "file": "wp-includes\/taxonomy.php"
                }
            ],
            "object_types": [
                "wp_template_part"
            ],
            "count_status": "qualified_posts_domain",
            "content_count": 0,
            "states": [],
            "first_published_utc": null,
            "last_published_utc": null,
            "top_terms": [],
            "term_count": 0
        },
        {
            "name": "wp_theme",
            "registration": "runtime_registered",
            "declarations": [
                {
                    "owner": "core",
                    "file": "wp-includes\/taxonomy.php"
                }
            ],
            "object_types": [
                "wp_global_styles",
                "wp_template",
                "wp_template_part"
            ],
            "count_status": "qualified_posts_domain",
            "content_count": 0,
            "states": [],
            "first_published_utc": null,
            "last_published_utc": null,
            "top_terms": [],
            "term_count": 0
        }
    ],
    "attachments": {
        "by_mime": [
            {
                "mime": "application\/pdf",
                "count": 2,
                "bytes": 28,
                "orphan_count": 1
            },
            {
                "mime": "image\/png",
                "count": 1,
                "bytes": 10,
                "orphan_count": 0
            },
            {
                "mime": "image\/webp",
                "count": 1,
                "bytes": 9892,
                "orphan_count": 1
            }
        ],
        "pdf_count": 2,
        "orphan_count": 2,
        "missing_files": 1,
        "size_basis": "stat_original_local_attached_file_only_no_derivatives; missing_files_excluded",
        "orphan_basis": "parent_zero_or_missing_not_proof_of_unused_media"
    },
    "product_links": [
        {
            "key": "_A12_product_id",
            "linked_contents": 1,
            "distinct_pairs": 1,
            "non_scalar_rows": 0
        },
        {
            "key": "_a12_article_id",
            "linked_contents": 1,
            "distinct_pairs": 1,
            "non_scalar_rows": 0
        },
        {
            "key": "_a12_product_id",
            "linked_contents": 2,
            "distinct_pairs": 2,
            "non_scalar_rows": 0
        },
        {
            "key": "_a12_product_ids",
            "linked_contents": 0,
            "distinct_pairs": 0,
            "non_scalar_rows": 1
        },
        {
            "key": "_product_version",
            "linked_contents": 0,
            "distinct_pairs": 0,
            "non_scalar_rows": 2
        }
    ],
    "native_guards": {
        "http": 1,
        "mail": 1,
        "scheduled": 1
    },
    "conventions": [
        "Etats: tous contenus stockes, corbeille et brouillons inclus; taxonomies: contenus distincts par taxonomie, pas somme des termes.",
        "Premiere et derniere publication: post_date_gmt des seuls contenus actuellement publish; null si aucun.",
        "Termes: vingt premiers par nombre de contenus distincts relies, tous etats; egalite par nom binaire puis identifiant interne non exporte.",
        "Champs: toutes les cles postmeta, internes incluses, sans limite top-N; comptes de contenus distincts, jamais les valeurs.",
        "Tailles: originaux locaux par MIME enregistre, sans miniatures; aucun telechargement ni appel de filtre tiers.",
        "Liaisons: cles product\/produit\/article\/numero\/issue; seules references scalaires canoniques entre contenu et produit\/variation, deux directions; structures serialisees non interpretees."
    ],
    "limitations": [
        "Registre natif apres wp_loaded dans le contexte CLI confine, sans requete front\/admin. Attribution: fichier appelant register_post_type\/register_taxonomy observe sur la pile. Objet injecte hors API: declarant inconnu, jamais invente.",
        "Site simple, tables InnoDB, configuration litterale et disposition standard. Requetes SELECT dans transaction READ ONLY; aucune action, tache, notification ni HTTP.",
        "Les seuls textes libres permis sont les noms des termes; valeurs suspectes masquees. Aucun titre, contenu, auteur, contact, identifiant de client, valeur de champ ou chemin de media exporte.",
        "Les comptes editoriaux restent dans posts\/postmeta dans les deux magasins; aucune lecture des coordonnees de commande HPOS ni interpretation des droits."
    ],
    "audit_sha256": "ca859a4df049f7ace96b872e1515329e40e7697ec21d4300e2ca3f1ac97cea3a"
}
```
