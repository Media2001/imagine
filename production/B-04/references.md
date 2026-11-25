# B-04 — Standard d’abord

Consultation officielle du 25 novembre 2026, réponses HTTP 200 : `references-consultees.json`.

- WordPress `WP_Query` : `https://developer.wordpress.org/reference/classes/wp_query/` — la requête principale porte déjà `paged`, `posts_per_page`, `found_posts` et `max_num_pages`. B04 retire seulement le `-1` imposé auparavant à l’archive et conserve le tri éditorial ; aucun paginateur ou inventaire miroir.
- WordPress `the_posts_pagination()` : `https://developer.wordpress.org/reference/functions/the_posts_pagination/` — sortie et liens natifs, utilisés par les deux archives. La recette exerce réellement trois pages de taille 2 via le main query sans écrire une option.
- WooCommerce, intégration d’un thème classique : `https://developer.woocommerce.com/docs/theming/theme-development/classic-theme-developer-handbook/` — support natif et hooks de wrappers. Le thème possède déjà son `main` ; les wrappers Woo redondants sont retirés, pas remplacés par un tunnel sur mesure.
- WooCommerce, source officielle du gestionnaire coming soon : `https://raw.githubusercontent.com/woocommerce/woocommerce/trunk/plugins/woocommerce/src/Internal/ComingSoon/ComingSoonRequestHandler.php`. La **source de la version réellement installée** a aussi été lue avant le raccord ; le hook `woocommerce_coming_soon_exclude` permet l’exemption strictement locale de la seule fiche produit B04. Les options de visibilité et la boutique entière ne sont pas ouvertes.

Le sur-mesure restant est de présentation : projection textuelle d’une décision déjà prise par `Imagine\Site\Paywall`, liste de métadonnées publiques, sélection d’un produit simple publié déjà associé par `Imagine\Site\AchatsNumeros::PRODUIT`, et affichage de la route `PdfNumero` seulement après décision complète et fichier disponible. Aucun moteur C06, stockage C11, source C14 ou bootstrap partagé modifié.
