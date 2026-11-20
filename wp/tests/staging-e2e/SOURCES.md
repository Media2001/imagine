# Références officielles et preuves locales

Références techniques consultées pendant la construction (aucun accès à un site client) :

1. Docker, **None network driver** — `--network none` ne crée que l'interface loopback : https://docs.docker.com/engine/network/drivers/none
2. WordPress Developer, **wp eval-file** — `--use-include` traite le fichier par `include` plutôt que par `eval`, nécessaire ici pour les déclarations strictes PHP : https://developer.wordpress.org/cli/commands/eval-file
3. WooCommerce Developer, **High Performance Order Storage** — distinction tables autoritatives classiques/HPOS, option `woocommerce_custom_orders_table_enabled` et quatre tables HPOS : https://developer.woocommerce.com/docs/features/orders/high-performance-order-storage/

Les versions des dépendances ne sont pas des assertions sur les versions les plus récentes. Elles proviennent des téléchargements publics nommés et des sorties réellement exécutées. Les URL, tailles et SHA-256 exacts des fichiers reçus figurent dans `public-dependencies.json` ; l'image effectivement utilisée figure dans `results/dependencies.json`.

Les schémas et métadonnées testés sont ceux créés par WordPress/WooCommerce réels dans ce conteneur : `wp_users`, `wp_usermeta`, commandes dans `wp_posts`/`wp_postmeta` ou `wp_wc_orders`/`wp_wc_order_addresses`/`wp_wc_orders_meta`/`wp_wc_order_operational_data`, items Woo, tokens Woo, notes `wp_comments`, tables Action Scheduler, options cron et `wp_wc_webhooks`. Les noms des tables absentes du catalogue sujet sont tirés de `SHOW TABLES` et du préflight effectivement exécuté, pas d'une supposition documentaire.

Les contrôles des extensions commerciales Subscriptions/Memberships ne sont **pas** validés par ces sources ou par la ressemblance d'une métadonnée : aucune de ces extensions n'est installée. Le harness n'invente ni leur schéma ni leur résultat de sonde.
