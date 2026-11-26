# Relecture indépendante Codex — C-16

Date : 26 novembre 2026. Références : `relecteurs/AGENTS.md`, doctrine, grille, brief C-16, cahier des charges §2.3 et §3.13, décisions du dépôt. Examen du code courant et des preuves de `production/C-16/`. Le rapport Claude n'a pas été consulté. Aucun accès à un site, une base ou un compte ; aucune modification hors de ce rapport.

## 1. Conformité

Le périmètre principal est présent : comparaison du parcours natif en dix lignes, trois étapes sous le menu Imagine, recherche et sélection du client, création différée à la confirmation, compte générique, commande et souscription natives `pending`, paiements hors ligne, emplacements nommés pour les offres exclues. `A-VOIR.md`, `PRET` et le rapport court `files/rapports/2026-11-26-00h45-V2.md` sont livrés. La création différée est une interprétation explicitement signalée, cohérente avec l'absence d'objets abandonnés avant confirmation.

**R2 — Important — `wp/plugins/imagine-site/CommandeNative.php:62` — La recherche par localité ne retrouve pas les clients créés par ce parcours.** La recherche ne lit que `billing_city` et `shipping_city` du compte. Or `creerClient()` n'enregistre aucune adresse sur le compte ; `remplir()` la pose uniquement sur la commande et la souscription. Après création d'un nouveau client, avec ou sans email, à « Bourg Fictif C16 », rechercher cette localité seule ne le retrouve donc pas, sauf présence accidentelle du texte dans son nom ou son email. Le contrôle livré utilise la localité du profil C09 préexistant et ne révèle pas cette rupture. Cela manque à la recherche demandée à l'étape 1 du brief (§3.13).

Correction proposée : rendre consultable par la recherche la localité effectivement saisie. Le défaut technique prudent consiste à initialiser l'adresse native du **nouveau** client lors de la confirmation, sans modifier les coordonnées d'un compte préexistant. Ajouter un cas création → nouvelle recherche par une localité distincte du nom/email, avec et sans email.

**R3 — Mineur — `wp/plugins/imagine-site/CommandeAdmin.php:203` — Les apostrophes de recherche restent échappées par WordPress.** La saisie GET est passée directement à `CommandeRegles::texte()`, contrairement aux saisies POST qui passent par `wp_unslash()`. Avec l'échappement des superglobales par WordPress, une recherche `O'Fictif` devient `O\'Fictif` et ne correspond plus au nom stocké. Le champ réaffiché conserve aussi la barre oblique.

Correction proposée : déséchapper la saisie GET avant sa validation, puis conserver l'échappement HTML existant à l'affichage. Ajouter une recherche par nom et par localité comportant une apostrophe, dans le contexte WordPress réel.

## 2. Exactitude métier

Déroulement manuel à partir du code, rapproché des reçus archivés — sans prétendre avoir rejoué ces parcours sur le site :

1. **Compte connu, abonnement par virement.** `V-INSCRIT@EXAMPLE.ORG` est normalisé, résolu dès l'étape 1 vers le compte existant et relu à la création. Commande et souscription partagent le propriétaire, sont liées par la relation parente native et restent impayées. La projection C15 accepte ce parent `pending` en `bacs`. `native-doublon.json` confirme le compte #8 et son nom conservé ; le reçu HTTP confirme sa présence dans les virements. Conforme pour ce cas séquentiel.
2. **Nouveau compte sans email, abonnement par virement.** L'adresse éventuellement saisie est ignorée, une adresse sous `sans-email.imagine.invalid` est générée, et le compte reçoit `imagine_sans_email=1`. Le filtre individuel refuse ce destinataire. La commande et la souscription restent `pending` sans date de paiement ; aucune adhésion n'est créée. `native-sansmail.json` et `acces-sansmail.json` rapportent zéro adhésion et une décision C06 fermée (`sans_droit`). Conforme pour la création et la fermeture initiale ; sa recherche ultérieure par localité échoue selon R2.
3. **Vente directe d'un numéro.** Le mode direct autorise l'adresse vide, réutilise le compte générique possédé par C16 et ne crée pas de souscription pour le produit simple lié au numéro. Le reçu HTTP couvre cette branche. La documentation signale explicitement que C15 exclut actuellement les commandes à l'unité de sa vue des virements ; leur règlement ultérieur n'est donc pas prouvé par C16.

**R1 — Bloquant — `wp/plugins/imagine-site/CommandeAdmin.php:126` — Le brouillon est mis en cache avant le verrou, ce qui permet une double création concurrente.** Pour l'action `creer`, `self::draft($token)` est appelé avant `GET_LOCK`. Cette lecture de transient alimente le cache d'options de la requête WordPress. Si deux POST chargent le même brouillon d'étape 3 avant que le premier n'écrive `commence`, le second attend le verrou avec cette ancienne valeur en cache. La nouvelle lecture à la ligne 154 ne garantit pas une lecture fraîche : elle peut reprendre le brouillon sans `commence` ni `resultat`, malgré la commande déjà créée par le premier POST. Le second écrase alors le brouillon et crée une seconde commande, ainsi qu'une seconde souscription pour un abonnement. Le verrou par client sérialise aussi les créations, mais ne les déduplique pas. Ce scénario existe avec le cache d'options en mémoire propre à chaque requête ; il ne nécessite pas Redis.

Correction proposée : pour `creer`, acquérir le verrou avant toute lecture du brouillon, puis lire un état frais sous verrou et conserver le contrôle du résultat déjà acquis. Réserver la lecture préalable à `preparer`, ou invalider explicitement les caches pertinents si cette lecture est maintenue. Ajouter un test avec deux requêtes synchronisées avant l'acquisition du verrou : les deux réponses doivent désigner le même ID, avec exactement une commande et une souscription. Ajouter aussi une interruption après le marquage `commence`, qui doit rester fermée à une nouvelle création. Constat issu de l'analyse du chemin d'exécution ; reproduction native non effectuée dans cet environnement.

Les frontières de clôture et le changement d'année ne portent pas de règle nouvelle dans ce lot : les droits restent délégués à C06 et les périodes au produit natif. Le cas limite déterminant ici est le rejeu concurrent, insuffisamment protégé.

## 3. Tests

**Exécution locale tentée, bloquée avant PHPUnit.** Le lanceur `wp/outils/demo/c16-unit.py` a été exécuté en mémoire avec ses seules écritures de reçus neutralisées, pour respecter l'interdiction de modifier `production/`. Il échoue dès `wsl.exe -d Ubuntu -- wslpath ...`, avec le code `4294967295` et `Wsl/Service/E_ACCESSDENIED`. Aucun test PHPUnit n'a démarré. Aucun exécutable `php`, `phpunit` ou `docker` n'est disponible dans le PATH Windows. Aucune installation ni élévation n'a été tentée.

Les lanceurs HTTP, de lecture native et de reset ne sont pas exécutés : ils accèdent au site et à ses comptes, ce que les consignes du relecteur interdisent. Le préparateur d'image n'a pas été lancé.

Vérifications locales des preuves effectuées avec succès, sans écriture :

- Les empreintes des onze pièces référencées dans `final.json` correspondent aux fichiers présents.
- Le JUnit de `unit-gates.json` contient **6 tests, 14 assertions**, avec un code de sortie archivé à zéro.
- `http-gates.json` contient **70 contrôles**, tous vrais, sans échec déclaré.
- Les quatre classes C16 et `c16-reset.php` correspondent aux empreintes de livraison. Les deux fichiers partagés `imagine-site.php` et `c09-seed.php` ont évolué depuis ce reçu ; la documentation des lots suivants signale cette succession. Les preuves C16 restent donc historiques et ne certifient pas à elles seules l'intégration courante.

Les six tests purs vérifient utilement la saisie et les paiements autorisés, mais n'exercent ni le contrôleur ni les objets natifs. Le test de rejeu de `wp/tests/demo/c16-http.py:98` renvoie le formulaire **après** avoir reçu la première réponse : il démontre le rejeu séquentiel, pas la concurrence de R1. La recherche par localité porte seulement sur un profil préexistant ; les apostrophes ne sont pas couvertes. Les tests demandés dans R1–R3 doivent compléter la recette.

La réserve C09 est correctement exposée : **381/382** contrôles archivés, action A-PAPIER #8103 annulée avant l'installation C16 et état annoncé inchangé avant/après. Elle n'est ni présentée comme verte ni attribuée sans preuve à C16. Le reçu T01 annonce **1 040 tests / 34 229 assertions** réussis ; ce résultat n'a pas été reproduit pendant cette relecture.

## 4. Sécurité et données

Contrôles présents : capacités dédiées ou administration, vérification des nonces par action et brouillon, brouillons liés à l'opérateur, refus des écritures GET, validation serveur des produits/paiements/pays, échappement des sorties et préparation SQL des verrous. Les écritures sont limitées à la démonstration identifiée avec contrôle des coupe-circuits. Aucun appel à `payment_complete()` ni création d'adhésion dans C16.

Le marqueur sans email est partagé avec C09/C13. Le filtre examine TO/CC/BCC et refuse également les domaines `.invalid`. Il bloque tout le message en présence d'un destinataire exclu, comportement documenté. Aucun raccord externe d'envoi n'est annoncé comme validé.

Aucun secret ni donnée réelle identifié dans les fichiers examinés ; le fichier privé d'identifiants n'a pas été ouvert. Le lot n'ajoute aucune voie de sortie du contenu réservé. Le reset comporte un prévol des objets possédés et refuse les objets payés ou étrangers ; les reçus annoncent la suppression de onze objets et trois comptes, avec conservation explicite de l'historique postal. La faiblesse d'intégrité concurrente à corriger reste R1.

## 5. Doctrine

Le standard est privilégié pour les commandes, souscriptions et utilisateurs ; aucune table de commandes parallèle ni modification d'extension tierce. Validation pure séparée des adaptateurs, `strict_types`, espace de noms Imagine, interface française et README présents. Les décisions techniques sont explicitées ; aucune nouvelle tarification ou règle d'accès n'est introduite.

### Décisions techniques, défaut proposé

Pour R1, défaut : une seule création par brouillon, lecture fraîche sous verrou et refus en cas d'état incomplet. Pour R2, défaut : initialiser les coordonnées du seul nouveau client, sans écraser celles d'un compte existant. Pour R3, défaut : déséchapper les entrées WordPress avant validation. Ces corrections techniques relèvent d'Hermès, avec arbitrage ultérieur de Claude ; elles ne nécessitent pas de question à Ced.

Aucune nouvelle question métier à transmettre à Imagine. Aucune validation visuelle accordée dans cette relecture.

## 6. Études (lots sans code)

Sans objet : lot avec code. `natif.md` fournit les liens officiels et distingue son comptage documentaire d'une mesure sur installation neuve. Les pages externes n'ont pas été ouvertes, conformément à l'interdiction d'accès aux sites ; leur contenu n'est pas certifié ici.

## Verdict

**À corriger.**

- **Bloquant — R1 :** une confirmation simultanée peut créer deux commandes et deux souscriptions pour le même brouillon.
- **Important — R2 :** les nouveaux clients ne sont pas retrouvés par la localité saisie dans ce parcours.
- **Mineur — R3 :** les recherches contenant une apostrophe sont faussées par l'absence de déséchappement GET.

La relance indépendante de PHPUnit reste à faire dans un environnement où WSL est accessible, avec les cas de régression proposés. Ce verdict n'est pas un GO.
