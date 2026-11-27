# Standard d'abord — liste fermée A-28 (26 novembre 2026)

1. Contact Form 7 seul : « which doesn't store submitted messages » — notice de l'éditeur https://raw.githubusercontent.com/rocklobster-in/flamingo/master/readme.txt ; aucune entrée à reconnaître dans CF7 lui-même (page contactform7.com bloquée par son WAF, non utilisée comme preuve).
2. Même notice officielle : « This plugin stores submission data collected through contact forms » ; Flamingo est le stockage complémentaire, pas la définition `wpcf7_contact_form`.
3. Source officielle Flamingo : `const post_type = 'flamingo_inbound';` — https://raw.githubusercontent.com/rocklobster-in/flamingo/master/includes/class-inbound-message.php ; `wp_insert_post` et `update_post_meta` rangent sujet, champs et métadonnées dans posts/postmeta.
4. Source officielle Flamingo : `const post_type = 'flamingo_contact';` — https://raw.githubusercontent.com/rocklobster-in/flamingo/master/includes/class-contact.php ; carnet dérivé, identité dans posts/postmeta : inclus par prudence, pas assimilé à un article.
5. Fluent Forms : « Storing the form submissions » — https://developers.fluentforms.com/database/ ; table `fluentform_submissions`.
6. Même documentation : « Submission Entry Details » ; table `fluentform_entry_details`, valeurs normalisées des champs.
7. Même documentation : « Form Submission meta » ; table `fluentform_submission_meta`, notes et métadonnées d'entrée.
8. Même documentation : « Store Form activity & api log » ; table `fluentform_logs` (purge entière, aucune sélection de texte).
9. **Doute explicite sur la justification documentaire** de `fluentform_draft_submissions` et `ff_scheduled_actions` : aucune phrase officielle exacte établissant leur stockage n'est livrée ici. Ces deux suffixes restent inclus par prudence dans la politique existante, sans exécuter les tâches ; ils ne sont pas présentés comme des stockages officiellement cités. Aucun élargissement de la liste.
10. Liste fermée : ces six suffixes de tables sous le préfixe exact et ces deux types de contenu, leurs révisions et métadonnées liées ; aucun motif générique « form ». Toute autre extension/table/type reste « autre », sans nouvelle décision A-28. Aucune couverture universelle des extensions de formulaires, fichiers joints ou stockages extérieurs n'est prétendue.

Les citations proviennent de la documentation/source des éditeurs consultée avant toute correction. Les formes de stockage sont éprouvées avec des archives fabriquées de toutes pièces, pas avec l'archive d'Imagine. Le catalogue sert à l'import ; aucune commande de Ced n'est changée.
