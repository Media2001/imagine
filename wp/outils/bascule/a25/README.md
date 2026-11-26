# A-25 — Données des visiteurs (lecture seule)

**Attention import : les messages de formulaires laissés en tables inconnues peuvent rester en clair après neutralisation/anonymisation.** Le banc exécute l'import inchangé sur une base fictive et démontre ce cas pour les deux tables de messages. Ce lot ne corrige pas l'import et ne donne aucun accord d'accès à une copie réelle.

Préconditions : Linux isolé, réseau coupé, Landlock, PHP CLI, compte SQL limité à SELECT, photographie A-02 de la même copie vérifiée ; dossier parent hors du site et du dépôt, disjoint dans les deux sens. Ne jamais lancer le PHP brut. Le seul gardien des flux est celui d'A-22 (`stream_guard.py`), réutilisé sans modification.

```sh
python3 wp/outils/bascule/a25/confine.py --wp-path=/copie-verifiee --audit=/hors-web/audit-date/audit.json --output=/hors-web/visiteurs-date
```

La commande suffit telle quelle ; aucun argument caché ni date obligatoire. Sorties privées `visiteurs.json` et `visiteurs.md` (0700/0600), jamais réutilisées si le dossier existe. Codes de refus fermés seulement. Cache/pare-feu en fichiers de remplacement ou lien symbolique : refus avant chargement, sans nom libre. L'opérateur contrôle lui-même ses liens, hors sortie de cet outil. Aucun effacement, anonymisation, choix de durée ni tentative d'envoi.

## Lecture et limites

- Commentaires hors notes de commande Woo : tous types et états présents. Objets natifs `WP_Comment`, date GMT ; année 0 signifie date absente/invalide. États fermés `0`, `1`, `spam`, `trash`, `post-trashed`, autres sous `autre`. Présence d'email, d'IP, rattachement à un compte comptés séparément, pas leur valeur. Le rattachement signifie `user_id > 0`, pas preuve que le compte existe encore.
- Commandes de type `shop_order` exclusivement, tous états y compris corbeille ; magasin autoritaire déterminé par `OrderUtil`, objets `WC_Order`, client 0 par getter natif, année de création UTC. Pas de remboursement ni abonnement, pas de double compte du magasin de synchronisation inactif. Cela qualifie une commande sans compte, pas l'état authentifié du navigateur au moment de l'achat (non reconstructible).
- Liste fermée de formulaires : **Fluent Forms** uniquement ; son schéma officiel documente une entrée dans `fluentform_submissions`, avec `created_at`. L'outil n'en lit que l'année et COUNT, jamais `response`. Le nom fermé est publié si son magasin existe (même vide) ; une liste vide dit explicitement qu'aucun magasin de la liste n'est présent. Il ne prétend pas qu'un plugin sans table est installé ou actif.
- Tables inconnues : candidates structurelles avec `form_id` et une colonne `response`, `message`, `submission` ou `fields`. Le rôle des colonnes vient de `information_schema.COLUMNS.COLUMN_KEY` : clé primaire simple `submission_id` = une entrée par ligne, comptée sous `autre` ; clé primaire simple `id` propre avec `submission_id` non primaire = table-fille de détails, exclue pour ne pas doubler les messages. Les tables à `meta_key` restent exclues, sauf conflit avec une clé `submission_id` (couverture indéterminée). Sans `submission_id`, une clé primaire simple `id` qualifie une entrée. Clé composite, absence de clé ou autre rôle ambigu : `forms.coverage` et le total `counts.forms` disent **`couverture indéterminée`**, jamais un zéro silencieux. Sinon la couverture vaut **`heuristique bornée`**, pas « exhaustive ». `other_tables` compte uniquement les tables d'entrées qualifiées ; en couverture indéterminée, ce n'est pas le total des tables possibles. Noms jamais publiés ; année depuis `created_at`, `date_created` ou `submitted_at`, sinon 0. **Ce n'est pas une détection exhaustive de tout stockage de formulaires** (CPT, colonnes/schémas différents, services distants hors couverture). Un zéro n'est pas une absence générale de messages.
- `clear_messages_after_import = true` est un avertissement constant, **pas une mesure** : le champ fermé `clear_messages_after_import_label` porte exactement « avertissement éditorial permanent, non mesuré sur la copie inspectée ». Il est présent dans les deux fichiers de sortie. Aucune suppression n'est exécutée.
- Chaque cellule année/état ou année/extension inférieure à cinq est intégralement fondue dans `autres`, séparément pour chaque métrique ; aucune année ou étiquette de cette petite cellule ne sort. Les métriques se recoupent : ne pas les additionner.
- L'import remplace toutes les adresses email de commentaires, y compris vides, et efface leurs IP : ces deux métriques disent `inconnu après neutralisation`, jamais zéro. Nombres/états/dates/rattachements de commentaires et commandes sans compte restent lisibles sur le banc. Les décisions d'import pouvant vider/anonymiser les tables inconnues, toutes les entrées de formulaires sont prudemment `inconnu après neutralisation` lorsque la marque d'import est présente ; les magasins et tables candidates restent des présences observées.
- SQL SELECT et transaction READ ONLY, Landlock, réseau coupé, mail/HTTP/cron refusés ; les quatre API Action Scheduler sont court-circuitées avant bootstrap. Aucun journal ne devient une destination d'écriture libre. Gardien A-22 valide les flux puis une projection stricte valide exactement deux rapports avant publication ; l'arrêt anticipé ou le message de fin ne contourne pas cette porte.

## Rejeu Windows sans PHP hôte

```sh
C:/Python314/python.exe -B wp/tests/a25/matrix.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a25-reprise-unique
C:/Python314/python.exe -B wp/tests/a25/verify.py
C:/Python314/python.exe -B wp/tests/a25/verify.py --require-shared-doc
```

Le premier chemin doit être neuf. Le dernier contrôle ne devient vert qu'après intégration parent des deux lignes de `production/A-25/readme-ajout.txt`. Le vérificateur n'exige ni ne scelle un futur PRET ; préparation d'image et portes globales appartiennent au parent.
