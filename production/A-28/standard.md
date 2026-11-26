# Standard d'abord — liste fermée A-28 (26 novembre 2026)

1. Contact Form 7 seul : « Contact Form 7 doesn’t store submitted messages anywhere. » — documentation officielle https://contactform7.com/save-submitted-messages-with-flamingo/ ; aucune entrée à reconnaître dans CF7 lui-même.
2. La même page : « Flamingo saves all messages through contact forms into the database. » ; c'est le stockage complémentaire, pas la définition `wpcf7_contact_form`.
3. Source officielle Flamingo : `const post_type = 'flamingo_inbound';` — https://raw.githubusercontent.com/rocklobster-in/flamingo/trunk/includes/class-inbound-message.php ; `wp_insert_post` et `update_post_meta` rangent sujet, champs et métadonnées dans posts/postmeta.
4. Source officielle Flamingo : `const post_type = 'flamingo_contact';` — https://raw.githubusercontent.com/rocklobster-in/flamingo/trunk/includes/class-contact.php ; carnet dérivé, identité dans posts/postmeta : inclus par prudence, pas assimilé à un article.
5. Fluent Forms : « Storing the form submissions » — https://developers.fluentforms.com/database/ ; table `fluentform_submissions`.
6. Même documentation : « Submission Entry Details » ; table `fluentform_entry_details`, valeurs normalisées des champs.
7. Même documentation : « Form Submission meta » ; table `fluentform_submission_meta`, notes et métadonnées d'entrée.
8. Documentation officielle https://fluentforms.com/docs/database-tables-of-fluent-forms/ : les journaux détaillent les entrées/intégrations ; table `fluentform_logs` (purge entière, aucune sélection de texte).
9. Schéma développeur officiel : brouillons d'entrées enregistrées et états multiétapes dans `fluentform_draft_submissions` ; actions différées et leurs charges dans `ff_scheduled_actions` : inclus, sans exécuter les tâches.
10. Liste fermée : ces six suffixes de tables sous le préfixe exact et ces deux types de contenu, leurs révisions et métadonnées liées ; aucun motif générique « form ». Toute autre extension/table/type reste « autre », sans nouvelle décision A-28. Aucune couverture universelle des extensions de formulaires, fichiers joints ou stockages extérieurs n'est prétendue.

Les citations proviennent de la documentation/source des éditeurs consultée avant toute correction. Les formes de stockage sont éprouvées avec des archives fabriquées de toutes pièces, pas avec l'archive d'Imagine. Le catalogue sert à l'import ; aucune commande de Ced n'est changée.
