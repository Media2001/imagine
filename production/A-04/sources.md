# A-04 — standard avant le sur-mesure

Références officielles consultées le 25 novembre 2026, sans connexion à un compte :

- WordPress, `wp core update-db` : https://developer.wordpress.org/cli/commands/core/update-db/ — procédure native de migration du cœur ; paramètres globaux `--require`, `--path`, etc.
- WooCommerce, préparation/sauvegarde, staging, mises à jour de fichiers et de base puis réception : https://woocommerce.com/document/how-to-update-woocommerce/ . Le parcours habituel de connexion à un compte n'est **pas** utilisé : archives locales autorisées, versions et hashes explicites.
- WooCommerce CLI : https://developer.woocommerce.com/docs/wc-cli/cli-overview/ . Une première qualification de `wp wc update` a révélé une double voie CLI/file quand l'auto-migration était déjà planifiée ; la version finale utilise uniquement l'API native de planification et sa file ciblée.
- Action Scheduler, commandes individuelles, filtre hooks/groupes et avertissement sur les dépendances entre actions : https://actionscheduler.org/wp-cli/ . Aucune commande de queue globale ni nettoyage n'est utilisée.

Sources primaires réellement inspectées dans le conteneur jetable : distribution publique Woo **11.1.1** de l'image épinglée `sha256:2fa44089da3ca9aeaba5da0b74bbb3e9e1592b14c07d114c6a635b5c814208f2`, `WC_Install::run_manual_database_update`, `get_db_update_callbacks`, `run_update_callback`, `update_db_version`, et filtre `woocommerce_enable_auto_update_db`. Le callback Variation Gallery apparaît hors du registre de versions et peut n'être planifié qu'au bootstrap suivant ; il est nommé explicitement, jamais accepté sur le seul préfixe de classe.

Premium autorisés uniquement dans la fixture : Subscriptions **9.4.1**, SHA-256 du ZIP `ed8c529d1382e2d06fa6e605e799c9db5607d8459806c229e74a20571f871083` ; Memberships **1.30.3**, SHA-256 `d3a858a8d6ebc7153248a10d665c6752948ea4fa8a1836d6bdd8a8f267ee3285`. API native de l'upgrader WCS et cycle Lifecycle SkyVerge de Memberships, ainsi que leurs marqueurs, sont exercés sans modifier ces extensions. Le contrôleur WCS contient un processeur de notifications différé qui n'est pas une migration : il est conservé et non exécuté.

Les sources de banc A-02/A-03 et le garde-fou A-01 sont importés/copiés en lecture seule. Les hashes des dépendances effectivement utilisées et des sources A-04 sont liés à chaque reçu de rejeu. Aucun code premium, archive de site, export SQL ni compte réel n'est livré dans les résultats ; seuls métadonnées structurelles, rapports fictifs, journaux techniques expurgés et empreintes sont exportés. Les ZIP publics de préparation sont un cache reproductible, pas une archive de preuve.

Sur-mesure limité à ce qui manque aux composants : ordre et préalables opérateur, état atomique/reprise, maintenance persistante, verrou de site hérité par les enfants, traitement ciblé sans libérer la queue AS, journal de migrations et qualification restrictive des différences A-03. Ce lot ne remplace ni le moteur d'upgrade des éditeurs ni A-05.
