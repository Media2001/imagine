# Lot A-01 — Troisième passe : la base réelle

**Voie** : 1. **Délai** : trois heures. **Passe avant A-04.**

Ced a relancé le diagnostic le 25/11 à 13 h 15. La reprise d'hier a tenu : l'archive est lue en entier (49 756 entrées, 16,9 Go de contenu, base de 474 Mo), les exports et journaux sont exclus, le résumé tient sur un écran. Il reste trois refus, tous dus à la base ou à deux dossiers minuscules.

## La sortie de Ced (résumé, aucune donnée)

```
UPLOADS_DIRECTORY_REVIEW_REQUIRED: 3 | BLOQUANT | uploads/memberships_profile_fields (2 fichiers, 13 octets), uploads/download-manager-files (1 fichier, 54 octets)
SQL_INSERT: 422762 | BLOQUANT | …matomo_archive_blob_2024_01, _07, _08, _09, _10
TABLE_PERSONNELLE_A_TRANCHER: 185 | BLOQUANT | …ahm_download_stats, …ahm_emails, …matomo_archive_blob_2015_01, _2016_01, _2017_01
TABLE_INCONNUE_CONSERVEE: 220 | AVERTISSEMENT | …ahm_assets, …ahm_download_stats, …ahm_emails, …fsmpt_email_logs, …matomo_access
SOURCE_SECRET_NEUTRALISABLE: 33982 | AVERTISSEMENT | …actionscheduler_actions, …comments, …fsmpt_email_logs, …matomo_log_action, …options
SECRET_OU_IDENTIFIANT: 9 | AVERTISSEMENT | languages
NON_INNODB_TABLE: 1 | AVERTISSEMENT | …wfls_role_counts
```

Extensions présentes : advanced-custom-fields-pro, custom-post-type-ui, flexible-checkout-fields, fluent-smtp, loco-translate, matomo, regenerate-thumbnails, simple-file-list, user-switching, woo-order-export-lite, woocommerce, woocommerce-gateway-stripe, woocommerce-memberships, woocommerce-product-addons, woocommerce-subscription-downloads, woocommerce-subscriptions, wordfence, wordpress-seo, worker, wp-all-export, wp-all-import-pro, wpai-acf-add-on. Thèmes : imaginev2, storefront, twentytwentyfive.

## Décisions (prises par Claude, elles ne touchent aucune règle métier)

**1. Une table inconnue est vidée, pas conservée.** « Table inconnue conservée » en simple avertissement, c'est ouvert par défaut : `fsmpt_email_logs` (le journal des emails envoyés aux abonnés) serait restaurée telle quelle. Nouvelle règle : toute table hors catalogue est restaurée **en structure seulement**, ses lignes ne sont ni lues ni insérées, sauf décision écrite « garder » ou « anonymiser » pour cette table. Ce n'est plus un refus : c'est le défaut, listé au rapport. `TABLE_PERSONNELLE_A_TRANCHER` ne subsiste que pour une table qu'une décision demande de garder.

**2. Les décisions se donnent par famille**, dans un fichier versionné du dépôt (`wp/outils/staging-court/politique-tables.json`, noms de tables seulement) : on ne tranche pas 185 tables une par une. Familles vidées d'office, pour mémoire et pour le rapport : `matomo_*` (statistiques de visite, adresses IP), `ahm_*` (reste de WordPress Download Manager, extension absente), `fsmpt_*` (FluentSMTP), `wf*` (Wordfence), tables de WP All Import et All Export, journaux de toute nature. `--table-decisions` reste possible pour un cas ponctuel et l'emporte.

**3. Les lignes d'une table vidée ne sont pas analysées.** `SQL_INSERT` vient très probablement des valeurs binaires des tables `matomo_archive_blob_*`. Pour une table vidée, saute ses `INSERT` en flux sans les interpréter. Pour les tables gardées, l'analyseur doit accepter les littéraux que la vraie extension écrit (binaire, hexadécimal, échappements) : vérifie-le sur un export réel contenant une colonne BLOB, et dis si un cas reste refusé.

**4. Deux dossiers de `uploads` à exclure** : `memberships_profile_fields` et `download-manager-files` (quelques octets, des fichiers de garde). Ajoute-les à la liste d'exclusion.

**5. Les extensions à neutraliser, maintenant qu'on connaît la liste.** Vérifie, extension par extension, ce que fait la phase de neutralisation, et complète : `worker` (ManageWP : prise de contrôle à distance, à désactiver), `wordfence` (désactivé, sinon il bloquera le staging et écrira des alertes), `fluent-smtp` (aucun envoi : courrier capturé), `matomo` (désactivé), `wp-all-export` et `wp-all-import-pro` (tâches planifiées supprimées), `woo-order-export-lite` (exports planifiés supprimés), `woocommerce-gateway-stripe` (clés retirées, webhooks inertes, mode test sans clé). Tableau dans les notes : extension, risque, ce que fait la commande.

**6. Les avertissements `SOURCE_SECRET_NEUTRALISABLE`** dans `actionscheduler_actions`, `comments` et `options` : confirme en deux lignes que l'anonymisation traite les arguments et journaux des actions planifiées (ils contiennent souvent des adresses email) et les auteurs de commentaires (email, IP). Sinon, corrige.

## Diagnostic

Les tables sont résumées **par famille** (préfixe commun, nombre de tables, action : catalogue / vidée / à trancher), plus la liste des tables hors catalogue qui ne tombent dans aucune famille connue. Affiche aussi l'espace disque nécessaire et disponible.

## Preuve

Un export de la vraie extension, depuis un site fictif auquel tu ajoutes : une table à colonne BLOB avec des octets arbitraires, une table inconnue à colonne `email`, une famille de tables datées. Diagnostic sans refus, restauration : tables inconnues présentes et vides, aucune de leurs valeurs nulle part dans le site restauré.

Tu n'ouvres pas l'archive d'Imagine. Rapport court, preuves proportionnées, puis `PRET`.
