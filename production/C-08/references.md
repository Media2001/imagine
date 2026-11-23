# C-08 — sources officielles vérifiées

Consultation 23/11/2026. Sources officielles (lecture en ligne et inspection ciblée du code installé, sans modifier les tiers).

- https://woocommerce.com/document/woocommerce-memberships-function-reference/ : `wc_memberships_get_user_memberships`, `wc_memberships_create_user_membership`; états natifs et appartenances multiples. On conserve ces objets, aucun compte/droit parallèle.
- https://woocommerce.com/document/woocommerce-memberships-user-memberships/ : attribution manuelle possible, suspension Subscriptions = pause Memberships. Memberships seul ne représente pas notre décision de grâce C-06.
- https://woocommerce.com/document/subscriptions/develop/functions/ : `WC_Subscription::get_date`, `update_dates`, méthodes héritées de WC_Order. Lecture/écriture CRUD, pas SQL pour les abonnements.
- https://woocommerce.com/document/subscriptions/develop/data-structure/ : `wcs_get_subscription`, stockage abstrait; ne pas écrire les dates de calendrier directement en métadonnées.
- https://developer.wordpress.org/reference/hooks/the_posts/ : filtrage des objets obtenus après traitement interne (clones par requête, jamais de corps expurgé écrit dans le cache partagé).
- https://developer.wordpress.org/reference/hooks/rest_prepare_this-post_type/ : garde finale du REST contenu, champs rendered/raw, même avec `_fields` et intégration.
- https://developer.wordpress.org/reference/hooks/get_the_excerpt/ : couper l'extrait automatique avant qu'il lise le corps; extrait public explicite ou texte générique, jamais un morceau arbitraire du texte réservé.
- https://developer.wordpress.org/reference/hooks/oembed_response_data/ : réponse oEmbed (également cache privé), contenu embarqué public minimal.
- https://developer.wordpress.org/reference/functions/wp_get_nocache_headers/ : no-cache, no-store, private; garde appliquée conservativement à toutes les réponses dynamiques de ce squelette.
- https://developers.google.com/search/docs/appearance/structured-data/paywalled-content : `isAccessibleForFree=false` / `hasPart` et sélecteur de la zone payante; aucune `articleBody` dans le partage.

## Choix de branchement

Les plans natifs explicitement désignés par `imagine_acces_plans` sont seuls reconnus. Sans réglage, aucun droit abonné. Les bibliothèques closes décident; l'adaptateur ne reproduit pas leur table de vérité. Un état `on-hold` seul ne crée jamais une grâce : une fenêtre explicite sur l'objet Subscriptions est nécessaire, sans durée métier inventée. Elle est seulement posée par la fixture C-08; le traitement des impayés n'est pas ce lot.

Le site de démonstration doit rester hors ligne. L'adaptateur Robots appelle bien le vérificateur C-03 avec ses interfaces; son fournisseur DNS refuse explicitement toute résolution réseau. Les faux Googlebot/Bingbot restent donc refusés. La vérification d'un vrai robot sur Internet n'est pas prouvée ni activée ici. Ne pas remplacer ce refus par `gethostbyaddr` sans délai dur.
