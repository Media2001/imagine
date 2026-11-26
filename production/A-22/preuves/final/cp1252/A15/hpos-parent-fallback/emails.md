# Emails declares — lecture seule

Registre WC_Emails reellement charge, pas un historique d'envoi. Aucun email declenche.

plugin:woocommerce : 12 actif(s)
plugin:woocommerce-memberships : 1 actif(s)
plugin:woocommerce-subscriptions : 16 actif(s)
Gabarits surcharges distincts : 4

```json
{
    "schema": "imagine-a15-v1",
    "read_only": true,
    "storage": "hpos",
    "registry": {
        "native_loaded": true,
        "email_count": 43
    },
    "emails": [
        {
            "id": "WCSG_Email_Customer_New_Account",
            "title": "New Recipient Account",
            "extension": "plugin:woocommerce-subscriptions",
            "enabled": true,
            "recipient_nature": "client",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "WC_Memberships_User_Membership_Activated_Email",
            "title": "Delayed membership activated",
            "extension": "plugin:woocommerce-memberships",
            "enabled": false,
            "recipient_nature": "client",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": true,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "WC_Memberships_User_Membership_Ended_Email",
            "title": "Membership ended",
            "extension": "plugin:woocommerce-memberships",
            "enabled": false,
            "recipient_nature": "client",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "WC_Memberships_User_Membership_Ending_Soon_Email",
            "title": "Membership ending soon",
            "extension": "plugin:woocommerce-memberships",
            "enabled": false,
            "recipient_nature": "client",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "WC_Memberships_User_Membership_Note_Email",
            "title": "Membership note",
            "extension": "plugin:woocommerce-memberships",
            "enabled": true,
            "recipient_nature": "client",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "WC_Memberships_User_Membership_Renewal_Reminder_Email",
            "title": "Membership renewal reminder",
            "extension": "plugin:woocommerce-memberships",
            "enabled": false,
            "recipient_nature": "client",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "admin_payment_gateway_enabled",
            "title": "Payment gateway enabled",
            "extension": "plugin:woocommerce",
            "enabled": true,
            "recipient_nature": "administration",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "cancelled_order",
            "title": "Cancelled order",
            "extension": "plugin:woocommerce",
            "enabled": true,
            "recipient_nature": "administration",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "cancelled_subscription",
            "title": "Cancelled Subscription",
            "extension": "plugin:woocommerce-subscriptions",
            "enabled": false,
            "recipient_nature": "administration",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "customer_cancelled_order",
            "title": "Cancelled order",
            "extension": "plugin:woocommerce",
            "enabled": false,
            "recipient_nature": "client",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "customer_cancelled_subscription",
            "title": "Customer Cancelled Subscription",
            "extension": "plugin:woocommerce-subscriptions",
            "enabled": false,
            "recipient_nature": "client",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "customer_completed_order",
            "title": "Completed order",
            "extension": "plugin:woocommerce",
            "enabled": true,
            "recipient_nature": "client",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "customer_completed_renewal_order",
            "title": "Completed Renewal Order",
            "extension": "plugin:woocommerce-subscriptions",
            "enabled": true,
            "recipient_nature": "client",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "customer_completed_switch_order",
            "title": "Subscription Switch Complete",
            "extension": "plugin:woocommerce-subscriptions",
            "enabled": true,
            "recipient_nature": "client",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "customer_failed_order",
            "title": "Failed order",
            "extension": "plugin:woocommerce",
            "enabled": true,
            "recipient_nature": "client",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "customer_invoice",
            "title": "Order details",
            "extension": "plugin:woocommerce",
            "enabled": false,
            "recipient_nature": "client",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "customer_new_account",
            "title": "New account",
            "extension": "plugin:woocommerce",
            "enabled": true,
            "recipient_nature": "client",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "customer_note",
            "title": "Customer note",
            "extension": "plugin:woocommerce",
            "enabled": true,
            "recipient_nature": "client",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "customer_notification_auto_renewal",
            "title": "Customer Notification: Automatic renewal notice",
            "extension": "plugin:woocommerce-subscriptions",
            "enabled": true,
            "recipient_nature": "client",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "customer_notification_auto_trial_expiry",
            "title": "Customer Notification: Free trial expiration: automatic payment notice",
            "extension": "plugin:woocommerce-subscriptions",
            "enabled": true,
            "recipient_nature": "client",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "customer_notification_manual_renewal",
            "title": "Customer Notification: Manual renewal notice",
            "extension": "plugin:woocommerce-subscriptions",
            "enabled": true,
            "recipient_nature": "client",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "customer_notification_manual_trial_expiry",
            "title": "Customer Notification: Free trial expiration: manual payment required",
            "extension": "plugin:woocommerce-subscriptions",
            "enabled": true,
            "recipient_nature": "client",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "customer_notification_subscription_expiry",
            "title": "Customer Notification: Subscription expiration notice",
            "extension": "plugin:woocommerce-subscriptions",
            "enabled": true,
            "recipient_nature": "client",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "customer_on_hold_order",
            "title": "Order on-hold",
            "extension": "plugin:woocommerce",
            "enabled": false,
            "recipient_nature": "client",
            "recipient_customised": false,
            "subject_customised": true,
            "content_customised": true,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/customer-on-hold-order.php",
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "customer_on_hold_renewal_order",
            "title": "On-hold Renewal Order",
            "extension": "plugin:woocommerce-subscriptions",
            "enabled": true,
            "recipient_nature": "client",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "customer_pos_completed_order",
            "title": "POS completed order",
            "extension": "plugin:woocommerce",
            "enabled": false,
            "recipient_nature": "client",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "customer_pos_refunded_order",
            "title": "POS refunded order",
            "extension": "plugin:woocommerce",
            "enabled": false,
            "recipient_nature": "client",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "customer_processing_order",
            "title": "Processing order",
            "extension": "plugin:woocommerce",
            "enabled": true,
            "recipient_nature": "client",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "customer_processing_renewal_order",
            "title": "Processing Renewal order",
            "extension": "plugin:woocommerce-subscriptions",
            "enabled": true,
            "recipient_nature": "client",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "customer_refunded_order",
            "title": "Refunded order",
            "extension": "plugin:woocommerce",
            "enabled": true,
            "recipient_nature": "client",
            "recipient_customised": false,
            "subject_customised": true,
            "content_customised": true,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "customer_renewal_invoice",
            "title": "Customer Renewal Invoice",
            "extension": "plugin:woocommerce-subscriptions",
            "enabled": true,
            "recipient_nature": "client",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "customer_reset_password",
            "title": "Reset password",
            "extension": "plugin:woocommerce",
            "enabled": true,
            "recipient_nature": "client",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "customer_verify_email",
            "title": "Confirm email address",
            "extension": "plugin:woocommerce",
            "enabled": true,
            "recipient_nature": "client",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "expired_subscription",
            "title": "Expired Subscription",
            "extension": "plugin:woocommerce-subscriptions",
            "enabled": false,
            "recipient_nature": "administration",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "failed_order",
            "title": "Failed order",
            "extension": "plugin:woocommerce",
            "enabled": true,
            "recipient_nature": "administration",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "gift_recipient_processing_renewal_order",
            "title": "Processing Renewal Order - Recipient",
            "extension": "plugin:woocommerce-subscriptions",
            "enabled": true,
            "recipient_nature": "client",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "new_order",
            "title": "New order",
            "extension": "plugin:woocommerce",
            "enabled": true,
            "recipient_nature": "administration",
            "recipient_customised": true,
            "subject_customised": true,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "new_renewal_order",
            "title": "New Renewal Order",
            "extension": "plugin:woocommerce-subscriptions",
            "enabled": true,
            "recipient_nature": "administration",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "new_switch_order",
            "title": "Subscription Switched",
            "extension": "plugin:woocommerce-subscriptions",
            "enabled": true,
            "recipient_nature": "administration",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "reactivated_subscription",
            "title": "Reactivated Subscription",
            "extension": "plugin:woocommerce-subscriptions",
            "enabled": false,
            "recipient_nature": "administration",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "recipient_completed_order",
            "title": "New Initial Order - Recipient",
            "extension": "plugin:woocommerce-subscriptions",
            "enabled": true,
            "recipient_nature": "client",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "recipient_completed_renewal_order",
            "title": "Completed Renewal Order - Recipient",
            "extension": "plugin:woocommerce-subscriptions",
            "enabled": true,
            "recipient_nature": "client",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        },
        {
            "id": "suspended_subscription",
            "title": "Suspended Subscription",
            "extension": "plugin:woocommerce-subscriptions",
            "enabled": false,
            "recipient_nature": "administration",
            "recipient_customised": false,
            "subject_customised": false,
            "content_customised": false,
            "template_overrides": [
                "wp-content\/themes\/a02-child\/woocommerce\/emails\/email-styles.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-footer.php",
                "wp-content\/themes\/a02-theme\/woocommerce\/emails\/email-header.php"
            ],
            "template_overridden": true
        }
    ],
    "transport_plugins": [
        {
            "name": "A15 SMTP fictif",
            "version": "1.2.3",
            "active": true,
            "runtime_mail_hook": true
        },
        {
            "name": "A15 SMTP inactif fictif",
            "version": "4.5.6",
            "active": false,
            "runtime_mail_hook": false
        }
    ],
    "summary": {
        "active_by_extension": {
            "plugin:woocommerce": 12,
            "plugin:woocommerce-memberships": 1,
            "plugin:woocommerce-subscriptions": 16
        },
        "overridden_template_files": 4
    },
    "audit_sha256": "1f283a9ef3e807e003f875fce4bd9cd7b4383b958c2ab1635ec3e0ea2c194b9f"
}
```
