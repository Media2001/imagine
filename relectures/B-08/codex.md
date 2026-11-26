# Relecture Codex — B-08

Date : 27 novembre 2026. Relecture indépendante du brief, des §3.1 et §3.12 du cahier des charges, de la doctrine, des décisions, de `production/B-08` et du code concerné dans `wp/`. Le rapport de Claude n’a pas été lu. Aucun site, compte ou base n’a été consulté ; aucune correction de code effectuée.

## 1. Conformité

Le périmètre nominal est couvert : pages natives et sept intitulés exacts, navigation principale, lien vers B-06 sans ouverture de droits, formulaire hors menu, don fermé, URL de parts vide et lien `sponsored` lorsqu’elle est renseignée. Aucun paiement ni raccord CoopHub dans le code examiné. Les pages publiques n’ont pas à entrer dans C-23.

Les interprétations sont explicitées dans `NOTE.md` : consentement facultatif, abonnement renvoyant à l’emplacement B-01, export/effacement également disponibles pour une adresse sans compte. Les cinq lignes « standard d’abord » et les livrables demandés sont présents.

## 2. Exactitude métier

Cas déroulés à la lecture du code, distincts d’une exécution WordPress :

- **Réglages absents** : `Soutenir::configuration()` donne don fermé et URL vide. Le rendu contient abonnement, bénévolat vide et prise de parts sans lien, dans cet ordre ; aucun don. Conforme au §3.12 et au brief.
- **Don ouvert et URL fictive renseignée** : le don apparaît entre abonnement et bénévolat, sans action de paiement ; la prise de parts devient un lien `rel="sponsored"`. Conforme.
- **101 propositions d’une adresse et une d’un tiers** : l’export découpe 50/50/1 ; l’effacement reprend la première tranche de la collection rétrécissante et préserve le tiers. Le principe de pagination est correct.

**B08-01 — important — `wp/plugins/imagine-site/Sujet.php:58` : les antislashs font refuser une proposition valide.** Les valeurs ont déjà été déséchappées dans `traiter()`, puis sont transmises telles quelles dans `meta_input`. L’écriture native des métadonnées les déséchappe à nouveau. Un sujet contenant littéralement `C:\dossier` perd donc son antislash à l’écriture ; la comparaison avec `$meta` échoue et la proposition est supprimée, avec un message de refus. **Correction proposée :** appliquer l’échappement attendu par l’API WordPress à la frontière d’écriture, en conservant les valeurs normalisées pour la relecture. Ajouter un cas passant par le POST, vérifiant le succès puis la conservation exacte du texte dans le détail administratif et l’export.

**B08-02 — important — `wp/outils/demo/b08-seed.php:90` : une création interrompue du menu ne peut pas être reprise.** L’identité du menu et de ses items n’est enregistrée qu’après toutes les créations. Si un item échoue après la création du menu, le rejeu retrouve ce menu mais aucune option d’appartenance ; il s’arrête sur « Collision menu B08 ». Le double passage nominal ne couvre pas cette interruption. **Correction proposée :** rendre la création récupérable, avec un suivi durable des objets appartenant au lot et une reprise sans doublon, ou un retour arrière borné en cas d’échec. Conserver le refus des menus étrangers. Tester un échec au milieu des items, puis un rejeu complet sans intervention manuelle.

## 3. Tests

- **Exécuté :** `python -B production/B-08/verifier.py`, code **0**. Les empreintes et la cohérence des preuves archivées passent.
- **Tenté :** commande Docker isolée de `b08-local.py`, appelée directement pour éviter l’écriture de son journal dans `production/B-08`. Montage du dépôt en lecture seule, réseau coupé, image locale sans téléchargement. Échec avant PHPUnit : **`Wsl/Service/E_ACCESSDENIED`**, code **1**. Aucun PHP/PHPUnit natif n’a été trouvé dans le PATH.
- **Non rejoués ici :** les six tests PHP, les mutations, la suite canonique et la recette HTTP. Les chiffres **6 tests / 181 assertions**, **12 mutations**, **31 contrôles HTTP**, **1 149 tests / 36 036 assertions** restent ceux des reçus contrôlés, pas des exécutions indépendantes de cette relecture. La recette HTTP nécessite un accès au site, interdit par le rôle.

La couverture livrée traite notamment nonce invalide, défauts d’écriture, suppression et lecture en erreur, consentement décoché, pagination et préservation d’un tiers. Toutefois, le double `wp_insert_post()` de `wp/plugins/imagine-site/tests/SujetWPStubs.php:56` copie directement `meta_input` et masque B08-01 : sa fidélité doit être corrigée avec le test de régression de ce point. Le rejeu documenté de création ne simule pas B08-02.

## 4. Sécurité et données

Le stockage est déclaré : type privé `imagine_sujet` dans les tables natives de contenus et métadonnées, champs `imagine_sujet_*`. Le code contrôle le nonce, réserve l’administration à `manage_options`, échappe les sorties et prépare la requête par adresse. Le type est exclu des recherches publiques et du REST. Les callbacks de confidentialité sont enregistrés dans les outils natifs utilisés par C-21.

Aucune recherche de compte dans le dépôt d’une proposition, donc pas de distinction de réponse selon l’existence du compte. Aucun appel mail/HTTP dans le traitement examiné. Aucun secret ni donnée réelle identifié dans les fichiers examinés. La restauration et le retrait des essais sont attestés par les reçus ; leur état actuel sur le site n’a pas été vérifié.

## 5. Doctrine

Le choix des pages, menus, réglages et outils de confidentialité natifs est proportionné. Le code utilise `strict_types`, l’espace de noms et les préfixes attendus. Les références officielles sont consignées dans `standard-officiel.json`, sans consultation extérieure lors de cette relecture.

**B08-03 — mineur — `wp/plugins/imagine-site/README.md:1` : B-08 manque dans la documentation de l’extension.** Le README ne décrit ni ces fonctions, ni leurs réglages, ni leurs tests, contrairement au §5 de la doctrine ; ces informations existent seulement dans le dossier de livraison. **Correction proposée :** ajouter une courte section B-08 décrivant les options, le stockage privé, les callbacks de confidentialité et la commande de test, avec renvoi vers `production/B-08/NOTE.md`.

### Décisions techniques, défaut proposé

Les corrections B08-01 et B08-02 sont techniques : préserver exactement le texte accepté et permettre la reprise des seuls objets appartenant au lot. Défaut proposé : appliquer ces corrections sans modifier les règles de consentement ou d’accès et sans récupérer un menu étranger. Aucune question pour Ced ou Imagine.

## 6. Études (lots sans code)

Sans objet : lot avec code.

## Verdict

**À corriger.** Ce verdict n’est pas un GO.

- **Bloquant :** aucun identifié.
- **Important :** B08-01, refus des propositions contenant des antislashs ; B08-02, reprise impossible après création partielle du menu.
- **Mineur :** B08-03, documentation B-08 absente du README de l’extension.

Le rejeu indépendant des tests PHP reste à obtenir dans un environnement local autorisé ; le refus WSL ne constitue pas un échec fonctionnel de ces tests.
