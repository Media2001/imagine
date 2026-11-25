# A-01 — troisième passe base, 25 novembre 2026

## Commandes et politique

La commande opérateur reste `wp/outils/staging-court/publish.py`. **Ced seul** utilise son archive ; aucun nouvel accord d'import, de publication ou d'accès agent n'est donné par ce lot.

```powershell
# Diagnostic inerte : mêmes paramètres opérateur qu'avant, sans mot de passe.
python .\wp\outils\staging-court\publish.py --diagnose --operator-ced --archive "$ARCHIVE_WPRESS" --expected-core-version 6.9.1
# Ajouter --detail pour les emplacements et la liste des tables ; aucune valeur de ligne.
# Ajouter --table-decisions "$DECISIONS_CED" seulement pour une décision ponctuelle écrite.
```

`wp/outils/staging-court/politique-tables.json`, **version 1**, ne contient que les règles et motifs de noms : Matomo, AHM, FSMPT, Wordfence, PMXI/PMXE et journaux sont vidés ; toute autre table hors catalogue aussi. Schéma et moteurs conservés. Une décision JSON indexée par **nom exact du détail diagnostic**, action `garder`, `vider`, ou `anonymiser` avec `columns`, l'emporte sur la famille. `garder` sur une table à colonnes personnelles reste bloquant ; choisir l'anonymisation ou le vidage, pas un accord tacite de conservation.

Avant d'examiner une ligne conservée, une passe structure seule détermine le préfixe exact ; puis seconde passe SQL bornée. Cela évite qu'une inconnue nommée `...fiction_users`, placée avant `...options`, soit prise pour la table des comptes. Les INSERT vidés sont parcourus lexicalement pour trouver leur fin, **sans décodage, tokenisation, scan de secrets ni insertion de leurs valeurs**. Les deux passes ne portent que sur la base, sans relire les fichiers exclus ni écrire de SQL en mode diagnostic. Pour l'import, le contexte natif transmet les décisions effectives/version ; une table inconnue réapparue avec des lignes pendant le bootstrap bloque la vérification.

Le résumé donne les familles, nombres/actions, inconnues hors familles et disque nécessaire/disponible. Le disponible du diagnostic est celui de son filesystem : le contrôle du **moteur Docker** reste refait avant création/copie/import. Exclusions ajoutées : `uploads/memberships_profile_fields` et `uploads/download-manager-files`.

## Neutralisation, extension par extension

Les deux colonnes de droite décrivent la commande, pas une certification des versions installées chez Imagine. Les correspondances de plugins, options et queues ont été exécutées avec les vrais scripts natifs sur données fictives ; les 22 extensions n'ont pas été installées/activées pour ce lot.

| Extension | Risque | Traitement de la commande |
|---|---|---|
| advanced-custom-fields-pro | Champs et licence | État/réglages conservés ; sorties externes bloquées. |
| custom-post-type-ui | Structures éditoriales | Conservées. |
| flexible-checkout-fields | Champs de commande personnels | Structure conservée ; données comptes/commandes anonymisées. |
| fluent-smtp | Envoi réel et credentials | Désactivée ; secrets récursivement retirés ; `pre_wp_mail` intercepte sans transport ni journal contenant les courriers. Tables `fsmpt_*` vides. |
| loco-translate | Chaînes pouvant contenir des secrets | Conservée ; fichiers candidats signalés, pas déclarés sûrs. |
| matomo | IP/visites et BLOB | Désactivée ; `matomo_*` en structure seule. |
| regenerate-thumbnails | Tâches de fond | Conservée ; cron vidé, recréation/exécution des ordonnanceurs bloquée. |
| simple-file-list | Exports/fichiers privés | Extension conservée ; seuls médias des extensions admises de son dossier sont restaurés. |
| user-switching | Changement d'identité privilégié | État conservé ; comptes anonymisés/sessions retirées ; aucun accès agent autorisé par le lot. |
| woo-order-export-lite | Exports planifiés/personnels | Cron supprimé, actions AS `woe_*`/`woo_order_export*` supprimées ; extension conservée. |
| woocommerce | Clients, commandes, paiements | Données personnelles anonymisées ; tokens/sessions/logs retirés, webhooks WC désactivés, passerelles runtime indisponibles. |
| woocommerce-gateway-stripe | Clés, paiements et webhooks entrants | **Désactivée par prudence**, donc handlers natifs non chargés ; réglages conservés en mode test sans clés ni secret webhook. Les webhooks WC sortants restent neutralisés aussi. |
| woocommerce-memberships | Membres et champs privés | Données comptes/adhésions anonymisées ; structure métier conservée ; dossier de garde exclu. |
| woocommerce-product-addons | Champs de produits/commandes | Réglages produits conservés ; zones personnelles de commandes traitées. |
| woocommerce-subscription-downloads | Téléchargements privés | Structure conservée ; permissions personnelles traitées ; ordonnanceurs bloqués. |
| woocommerce-subscriptions | Renouvellements | État staging imposé si présente ; actions neutralisées ; aucun renouvellement financier. |
| wordfence | Blocage du staging, alertes/journaux | Désactivée ; tables `wf*` en structure seule. |
| wordpress-seo | Réglages éditoriaux | Conservés ; indexation staging interdite par le verrou. |
| worker | Prise de contrôle ManageWP | `worker/init.php` désactivé avant le premier bootstrap. |
| wp-all-export | Exports et tâches de fond | Cron supprimé, actions AS `pmxe_*`/`wp_all_export*` supprimées ; `pmxe_*` en structure seule. |
| wp-all-import-pro | Imports et tâches de fond | Cron supprimé, actions AS `pmxi_*`/`wp_all_import*` supprimées ; `pmxi_*` en structure seule. |
| wpai-acf-add-on | Paramètres d'import ACF | Conservée ; aucune tâche d'import exécutée. |

**Actions planifiées :** `args=[]`, `extended_args=NULL`, charge `schedule` vidée, actions en cours/en attente annulées ; actions terminées/échouées et tâches import/export ci-dessus supprimées ; journaux et claims vidés.
**Commentaires/options :** auteurs/email/IP/agent/texte des commentaires anonymisés ; credentials d'options scrubés récursivement ; quatre options d'adresse opérationnelle WP/Woo remplacées par `imagine-test-admin@example.org`. Les réglages éditoriaux et emails hors périmètre reconnus ne sont pas globalement détruits et restent soumis aux avertissements existants.

## Preuve et limites

Banc existant AI1WM réutilisé en variante petite base : **vraie extension publique inchangée 7.109**, vraie chaîne gratuite d'export, site fictif WordPress 7.0.9/PHP 8.2.36, runner neuf `network=none`, sans port/montage/volume, MariaDB socket seul. BLOB de 283 octets contenant les 256 valeurs d'octet, inconnue `email`, trois tables Matomo datées et familles supplémentaires. Restauration par l'implémentation opérateur et ses trois phases natives, puis lectures PDO/SQL et scan indépendant de tous les fichiers restaurés. Deux cas : défaut fermé et décisions explicites, dont maintien d'un BLOB Matomo malgré sa famille. Aucun export de l'archive fictive hors du runner.

Le vrai plugin épinglé produit du **0xhex** pour ces BLOB ; l'intégrité est relue par SHA-256 dans MariaDB. `_binary'...'`, `X'...'` et les échappements NUL/CR/LF/TAB/BS/Z, barre oblique et apostrophe sont aussi importés et relus, comme preuve supplémentaire distincte du format effectivement écrit par le plugin. Restent refusés : expressions/fonctions SQL, autres introducateurs de charset, littéraux de bits, commentaires au milieu des INSERT et instructions conservées au-delà de 16 Mio ; aucune grammaire SQL générale de repli.

Aucun nouveau paquet Composer : pas de reconstruction d'image nécessaire ; suite globale `rejouer.ps1` réellement relancée. Les grandes archives/médias de la passe précédente restent des preuves historiques, pas une nouvelle qualification de volume. Aucun accès archive Imagine, compte réel, Git, Novamira, outil partagé ou autre voie. Les anciens reçus ne sont pas réécrits. Les chemins des derniers résultats et compteurs exacts sont dans `archive-reelle-3-final.json`.
