# C-10 — documentation officielle consultée avant code

23 novembre 2026. Standard retenu : Settings API WordPress, formulaire vers `options.php`, groupe commun et trois options existantes. `options.php` assure capacité et nonce ; le nonce n'accorde aucun droit. Pas de moteur, bancaire ou de renouvellement maison.

- https://developer.wordpress.org/plugins/settings/settings-api/ : pages, sections, champs et formulaire natifs.
- https://developer.wordpress.org/reference/functions/register_setting/ : groupe, validation `sanitize_callback`, défaut et absence d'exposition REST.
- https://developer.wordpress.org/reference/functions/add_menu_page/ : menu natif et contrôle de capacité également dans le callback.
- https://developer.wordpress.org/reference/hooks/updated_option/ : journal après persistance réelle, non dans le sanitizer (qui peut être appelé plusieurs fois).
- https://developer.wordpress.org/reference/hooks/added_option/ : première persistance également journalisée.
- https://developer.wordpress.org/apis/security/nonces/ : nonce distinct du contrôle des droits.
- https://woocommerce.com/document/subscriptions/renewal-process/ : renouvellements natifs ; C10 ne lance ni paiement ni email ni modification de contrat.

Les trois adaptateurs existants sont réutilisés pour validation/lecture ; leurs anciens menus ne sont pas branchés. Les bibliothèques PHP closes restent inchangées. Une nouvelle façade administrative les réunit et journalise les trois options. Le branchement C08 doit transmettre explicitement les réglages à son moteur pour rendre le réglage de contenu futur effectif.
