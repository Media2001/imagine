# C13 — documentation officielle consultée avant code (24/11/2026)

- WordPress `add_submenu_page` : https://developer.wordpress.org/reference/functions/add_submenu_page/ — capacité du menu ET contrôle du callback ; admin native suffisante.
- WordPress `check_admin_referer` : https://developer.wordpress.org/reference/functions/check_admin_referer/ — nonce vérifie l'intention, ne remplace jamais la capacité.
- WordPress `admin_post_{$action}` : https://developer.wordpress.org/reference/hooks/admin_post_action/ — contrôleur authentifié, réponse CSV à la demande ; aucun fichier export public.
- WooCommerce CRUD : https://developer.woocommerce.com/docs/best-practices/data-management/crud-objects/ — lecture par objets natifs, compatible stockage HPOS, aucune requête SQL sur les commandes.
- Subscriptions : https://woocommerce.com/document/subscriptions/develop/functions/ — dates `get_date(..., 'gmt')`, statuts et getters natifs.

Standard réutilisé : menu/formulaire/tableaux WordPress, capacités natives, nonce, contrôleur admin-post, CRUD Subscriptions/Memberships. Sur-mesure limité au raccord C01/C07, aux observations postales datées et à l'audit. CSV et protection tableur viennent exclusivement de C07/C04 ; format lu dans C10. Aucun changement des bibliothèques closes.

Constats préalables : le rôle dédié existe réellement et e-abo le possède ; aucun élargissement requis. C09 contient des états présents, sans historique postal daté de clôture, aucun paiement, ni attribution persistée des quatre numéros. Ne pas reconstituer un historique passé à partir des états présents ; les clôtures antérieures au premier relevé seront fermées. Offerts/groupés restent absents du natif C09 : ne pas inventer de bénéficiaires.
