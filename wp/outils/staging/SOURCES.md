# Références officielles

Références consultées pour le code de ce lot ; elles documentent les mécanismes standard, pas une certification des versions payantes non installées. Les traitements de données et les tests restent entièrement offline.

| Sujet | Source officielle | Usage / limite |
|---|---|---|
| Court-circuit mail | https://developer.wordpress.org/reference/hooks/pre_wp_mail/ | Une valeur non `null` court-circuite `wp_mail`. Retour `false` choisi pour ne pas annoncer un envoi réussi. Ne bloque pas `mail()`/SMTP direct. |
| HTTP | https://developer.wordpress.org/reference/hooks/pre_http_request/ | Retour `WP_Error`, y compris pour le loopback. Les SDK/sockets contournant l’API WP exigent l’isolation réseau du worker. |
| Environnement | https://developer.wordpress.org/reference/functions/wp_get_environment_type/ | `staging` obligatoire, jamais déduit seulement du nom d’hôte. |
| Cron | https://developer.wordpress.org/plugins/cron/hooking-wp-cron-into-the-system-task-scheduler/ | `DISABLE_WP_CRON` est nécessaire mais ne bloque pas tous les appels manuels ; filtres de planification et court-circuit des jobs ajoutés. |
| Cron : hooks | https://developer.wordpress.org/reference/hooks/pre_schedule_event/ ; https://developer.wordpress.org/reference/hooks/pre_reschedule_event/ ; https://developer.wordpress.org/reference/hooks/pre_get_ready_cron_jobs/ | Empêcher de recréer la queue pendant un bootstrap quarantainé. |
| WCS staging | https://woocommerce.com/document/subscriptions-handles-staging-sites/ | WCS désactive paiements automatiques et emails d’abonnement sur copie ; ce mécanisme ne remplace ni suppression des tokens ni mail global. |
| Filtre exact WCS | https://github.com/Automattic/woocommerce-subscriptions-core/blob/trunk/includes/class-wcs-staging.php | `WCS_Staging::is_duplicate_site()` renvoie le filtre **`woocommerce_subscriptions_is_duplicate_site`**, pas un filtre nommé `wcs_is_duplicate_site`. Forcé vrai ; sonde par la méthode réelle obligatoire. |
| Métadonnées WCS classiques | https://github.com/Automattic/woocommerce-subscriptions-core/blob/trunk/includes/data-stores/class-wcs-subscription-data-store-cpt.php | Abonnements via commandes/CPT + métadonnées ; les `_schedule_*`, statuts et montants doivent rester, les références de paiement sont retirées. Pas d’essai sous licence dans ce lot. |
| Memberships | https://woocommerce.com/document/woocommerce-memberships-data-structure/ | `wc_user_membership` dans `posts/postmeta`, plans et références conservés ; pas de licence ni test des droits effectifs. |
| HPOS | https://developer.woocommerce.com/docs/features/high-performance-order-storage/database-schema/ | `wc_orders`, `wc_order_addresses`, `wc_order_operational_data`, `wc_orders_meta`. Tables classiques et HPOS toutes deux traitées quand présentes. |
| AS, runners | https://actionscheduler.org/perf/ | Runner via `action_scheduler_run_queue`, distinct des requêtes async. Supprimer uniquement WP-Cron ne suffit pas. |
| AS async, source | https://github.com/woocommerce/action-scheduler/blob/trunk/classes/ActionScheduler_AsyncRequest_QueueRunner.php | Filtre `action_scheduler_allow_async_request_runner`. |
| AS exécution, source | https://github.com/woocommerce/action-scheduler/blob/trunk/classes/abstracts/ActionScheduler_Abstract_QueueRunner.php | `action_scheduler_before_execute` interrompt également les exécutions manuelles. |
| Passerelles | https://woocommerce.github.io/code-reference/classes/WC-Payment-Gateways.html | Filtre `woocommerce_available_payment_gateways`; la valeur historique du moyen de paiement reste en commande. |

Le catalogue de tables/colonnes et les versions d’extensions réelles ne sont pas déduits de ces pages. Tout schéma divergent reste bloquant jusqu’à l’ajout d’un adaptateur documenté et testé sur données fictives.
