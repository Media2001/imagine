# Références officielles consultées avant l'implémentation native C09

23 novembre 2026. Pages effectivement ouvertes par l'outil de recherche.

- WooCommerce CRUD : https://developer.woocommerce.com/docs/best-practices/data-management/crud-objects/ — objets, setters et save(), abstraction du stockage HPOS. Aucun SQL d'écriture de commande.
- Subscriptions : https://woocommerce.com/document/subscriptions/develop/functions/ — get_date(), update_dates() en GMT, dates interdépendantes, modes de renouvellement.
- Stockage Subscriptions : https://woocommerce.com/document/subscriptions/develop/data-structure/ — ne pas modifier directement le prochain paiement en méta ; WC_Subscription et relations natives.
- Memberships : https://woocommerce.com/document/woocommerce-memberships-function-reference/ — wc_memberships_create_user_membership(), get_user_memberships(), get_memberships_from_subscription().
- WordPress : https://developer.wordpress.org/reference/functions/wp_insert_user/ — création et distinction du mot de passe à la mise à jour ; wp_update_user et contrôle wp_check_password utilisés.
- WordPress : https://developer.wordpress.org/reference/classes/wp_user/set_role/ — remise à zéro des rôles.

Complément vérifié dans les extensions déjà installées, en lecture seule : signatures et méthodes natives par Reflection. Les associations _subscription_id de Memberships et les deux métadonnées de grâce sont les seules métadonnées de raccord de droits C08 conservées. Les autres métadonnées C09 ne servent qu'à marquer la propriété des objets, jamais à accorder un droit.

Décisions : aucun plugin/passerelle supplémentaire, aucun jeton ni accord bancaire factice, jamais payment_complete(). Les commandes restent pending/on-hold/cancelled (zéro montant et sans date de paiement), tandis que les abonnements/adhésions sont des objets de fixture administratifs natifs. Les limitations sont affichées profil par profil. Pas de nouveau hook ni modification des bibliothèques closes.

Chemin : le dossier littéral `C:\Users\Ced\imagine voie2` n'existe pas ; la consigne permanente définit « voie 2 » dans le dépôt existant `C:\Users\Ced\imagine`. C'est ce dépôt qui est utilisé, sans lire la file de voie 1.
