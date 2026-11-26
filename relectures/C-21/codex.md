# Relecture indépendante Codex — C-21

Date : 26 novembre 2026. Périmètre : brief C-21, production/C-21, code et tests correspondants dans wp/, producteurs C-13/C-16/C-17 et rapport de livraison. Référence métier : cahier des charges §4.4, notamment lignes 1131 à 1137. Doctrine et grille appliquées. Aucun accès à un site, à une base ou à un compte ; aucun rapport Claude consulté. Seul ce fichier est écrit.

## 1. Conformité

Le raccord aux exporteurs/effaceurs natifs, l’inventaire avec origine des données, les dix lignes sur le standard, A-VOIR et PRET sont présents. L’adaptateur ne modifie pas les réglages de conservation et ne supprime pas lui-même les commandes ou souscriptions. Les journaux C-18 sans données d’abonné sont correctement distingués de l’identité de leur opérateur. La dépendance à la conservation de la demande native terminée est explicitement documentée.

- **C21-01 — important — `wp/plugins/imagine-site/Confidentialite.php:243`.** Le rapprochement d’un brouillon ignore `resultat.client`. Cas concret : C-16 crée un **nouveau client sans email**, conserve dans `client` le mode `nouveau`, le nom et `email=''`, puis stocke l’ID du compte créé dans `resultat.client`. L’email technique du compte ne correspond pas à la chaîne vide, `client.id` est absent et `qui` désigne le référent. Ce brouillon, avec nom et adresse, n’est donc ni exporté ni effacé pour le client, y compris par le hook de suppression du compte. Sa durée de vie d’une heure ne satisfait pas la relecture immédiatement vide demandée par le brief. **Correction proposée :** prendre en compte l’ID natif du client créé dans le résultat, sans rapprochement approximatif par nom ; tester le parcours C-16 réel « nouveau sans email », puis export, effacement et suppression du compte avant expiration du brouillon.

- **C21-02 — mineur — `wp/plugins/imagine-site/Confidentialite.php:356`.** La projection cherche `mode_paiement`, alors que le producteur `CommandeRegles::commande()` renvoie `paiement`. Le mode bacs/imagine_papier d’un vrai brouillon est donc absent de l’export, contrairement à l’inventaire. La fixture C-21 utilise précisément la mauvaise clé `mode_paiement`, ce qui masque l’écart. **Correction proposée :** exporter la clé réellement produite, sous un libellé français, et construire le test à partir du schéma C-16 réel. Il s’agit du mode de règlement, pas d’une référence de moyen de paiement à exclure.

## 2. Exactitude métier

Déroulés manuels, par lecture du code, sans prétendre à une exécution WordPress :

| Cas | Résultat observé dans le code | Appréciation |
|---|---|---|
| Compte ordinaire avec marqueurs, découverte et justificatif ; abonnement actif conservé par le standard | Les ajouts Imagine sont retirés ; l’adaptateur n’annule ni ne supprime l’abonnement | Conforme au partage des responsabilités demandé ; conservation effective seulement attestée par les reçus historiques |
| Brouillon finalisé pour un nouveau compte sans email | Aucune branche de rapprochement ne reconnaît le titulaire | Non conforme, C21-01 |
| Groupe résolu contenant deux bénéficiaires ; un seul demande l’effacement | Le second reste dans le tableau, mais le groupe devient non résolu et disparaît des destinataires éligibles | Non conforme, C21-03 |
| Titulaire/payeur d’un groupe ou cadeau demandant l’effacement, bénéficiaire distinct conservé | L’observation entière est supprimée | Non conforme, C21-04 |

- **C21-03 — important — `wp/plugins/imagine-site/ConfidentialiteRegles.php:38`.** Tout retrait d’un bénéficiaire impose `beneficiaires_resolus=false`, même si les autres bénéficiaires d’un groupe restent connus et valides. `EnvoiRegles::calculer()` transforme alors le groupe en situation suspendue, vide ses destinataires et produit `historique_incomplet=true`. `ListeEnvoiAdmin::preparer()` refuse dans ce cas **l’export postal entier**. Dans un gel, cette modification persiste ; le test actuel vérifie seulement que le nom du tiers subsiste et exige même le booléen faux. La conservation d’un tableau ne prouve donc pas la conservation du service aux tiers. **Correction proposée :** représenter le retrait volontaire pour confidentialité sans le confondre avec une attribution inconnue ; conserver l’éligibilité des autres membres et tester la relecture d’un véritable gel, la liste calculée et la génération du CSV après retrait d’un membre.

- **C21-04 — important — `wp/plugins/imagine-site/ConfidentialiteRegles.php:16`.** Lorsque le demandeur est `donnees.user`, la méthode renvoie immédiatement `null`, y compris pour un cadeau ou un groupe avec bénéficiaires distincts. L’effaceur supprime alors l’observation et, dans le gel, le bloc associé. L’historique et les destinataires des autres personnes disparaissent avec ceux du payeur, alors que leurs abonnements/adhésions peuvent rester conservés par le standard. **Correction proposée :** distinguer les informations du titulaire de celles des bénéficiaires ; anonymiser la part du demandeur en préservant les données et les droits postaux des tiers. Ajouter les cas payeur de cadeau et titulaire de groupe, avec export personnel des bénéficiaires et relecture postale avant/après.

## 3. Tests

**Tentative locale effectuée, exécution PHP indisponible.** Le lanceur `c21-unit.py` écrit obligatoirement un reçu dans production/C-21. Pour respecter l’interdiction de modifier un autre fichier, j’ai tenté directement le même environnement PHPUnit, avec dépôt monté en lecture seule et réseau désactivé :

```text
wsl.exe -d Ubuntu -- docker run --rm --pull never --network none --read-only --user 65534:65534 --cap-drop ALL --security-opt no-new-privileges --tmpfs /tmp:rw,nosuid,nodev,size=256m,mode=1777 --mount type=bind,source=/mnt/c/Users/Ced/imagine/wp,target=/repo/wp,readonly --entrypoint php imagine-tests-t01:1 /repo/wp/tests/demo/c16-unit-runtime.php ConfidentialiteReglesTest
```

Résultat : `Wsl/Service/E_ACCESSDENIED`, avant démarrage des tests. Aucun exécutable PHP local disponible dans le PATH. Les parcours HTTP, sécurité, pannes et régressions n’ont pas été lancés : ils accèdent au site/base et plusieurs téléversent du code ou écrivent des reçus. Même le vérificateur dit « lecture seule » appelle `live()`, qui interroge le site ; les droits de `relecteurs/AGENTS.md` ne l’autorisent pas.

**Contrôle local des preuves effectué**, avec Python sans bytecode : les onze fichiers de preuves référencés par le sceau ont tous leur empreinte attendue. Les reçus annoncent 4 tests/17 assertions C-21, 133 tests/695 assertions du paquet, 33 contrôles HTTP, 9 de sécurité et 8 de panne, sans échec déclaré. Ce sont des résultats historiques, pas des tests rejoués pendant cette relecture. Les profils C-09 et l’absence de fixture ne sont donc pas vérifiés en direct.

- **C21-05 — mineur — `wp/tests/demo/c21-verifier.py:126`.** La comparaison intégrale des sources échoue désormais pour `Confidentialite.php`. L’empreinte courante est `f4a6916e10425b82b881a7859ab41f9df80de587e48ec8896c46917ea67fbfc3`, contre `ca240ef50f433db3ff977bfbb464c2ce4a5c9997f7a4da98b00050db4a52c695` dans le sceau C-21. Vérification locale : retirer en mémoire le seul ajout `imagine_newsletters_preferences` redonne exactement l’empreinte C-21 ; les reçus C-22 identifient cette évolution. Ce n’est pas une altération inexpliquée du lot, mais la commande de validation annoncée ne peut plus réussir sur l’arbre livré. **Correction proposée :** fournir un contrat de succession ou une validation de l’état intégré qui prouve l’évolution autorisée et ses régressions, sans réécrire les preuves historiques.

Les cas manquants prioritaires sont ceux de C21-01, C21-03, C21-04 et C21-06. La fixture actuelle emploie un client déjà existant, contrôle la présence textuelle du bénéficiaire restant et ne rejoue pas le moteur postal sur le gel modifié : elle ne démontre pas ces propriétés métier.

## 4. Sécurité et données

- **C21-06 — bloquant — `wp/plugins/imagine-site/Confidentialite.php:350`.** L’export d’un brouillon restitue systématiquement `client` et l’adresse de `commande`, alors que `draft()` sélectionne aussi le brouillon lorsque le demandeur est uniquement son opérateur (`qui`). Exemple : le référent A prépare une commande pour B ; B possède un autre ID et une autre adresse. Une demande d’export personnel de A reçoit alors le nom, l’email et/ou l’adresse postale de B dans l’archive. Le contrôle de capacité administratif n’empêche pas cette fuite lors de la remise de l’archive au demandeur. **Correction proposée :** distinguer titulaire et opérateur dès la sélection/projection ; pour l’opérateur seul, n’exporter que sa propre activité, sans identité ni coordonnées du client. Tester avec deux véritables utilisateurs fictifs distincts et vérifier l’absence de toutes les valeurs de B dans l’archive de A. Appliquer la même distinction à l’effacement pour ne pas supprimer le dossier d’un client au seul motif que son opérateur exerce ses droits.

Points satisfaisants à la lecture : pas de route publique supplémentaire ; capacités et nonces laissés aux outils natifs ; requêtes de sélection et de remplacement préparées ; liste explicite de champs ; retrait de l’exporteur de jetons ; erreurs de suppression physique signalées ; remplacement concurrent des options contrôlé puis relu. Aucune donnée réelle ni secret identifié dans les éléments examinés. La modification ne touche pas le rendu du paywall ; son étanchéité n’a pas été retestée ici.

## 5. Doctrine

Le standard est privilégié : aucun écran d’export concurrent, aucune modification de bibliothèque tierce ni de durée de conservation. La projection postale est isolée en PHP pur ; namespace Imagine, strict_types et README sont présents.

Les défauts de traitement des tiers empêchent toutefois de tenir la non-régression revendiquée. Les tests doivent prouver le résultat métier obtenu après effacement, et pas seulement la persistance de quelques chaînes ou la forme d’un tableau. Les corrections proposées sont techniques et ne nécessitent pas d’inventer une règle comptable ou un arbitrage visuel.

## 6. Études (lots sans code)

Sans objet comme catégorie principale : le lot contient du code. La note `natif.md` fournit des liens officiels et distingue le standard des ajouts Imagine. Ces pages n’ont pas été consultées, conformément à l’interdiction d’accéder à un site ; leur contenu n’est pas certifié par cette relecture. Les affirmations sur les versions installées et les réglages effectifs restent étayées par les reçus fournis, sans confirmation indépendante de l’installation.

## Verdict

**À corriger.**

- **Bloquant :** C21-06 — données du client divulguées dans l’export personnel de l’opérateur.
- **Important :** C21-01 — brouillon finalisé d’un nouveau compte sans email oublié ; C21-03 — retrait d’un bénéficiaire bloquant l’export postal ; C21-04 — suppression des données postales des tiers lorsque le titulaire est effacé.
- **Mineur :** C21-02 — mode de règlement absent de l’export d’un vrai brouillon ; C21-05 — vérification du sceau incompatible avec l’évolution C-22 identifiée.

Ce verdict n’est pas un GO. Les tests PHP n’ont pas pu être exécutés dans cet environnement ; aucune validation sur site n’a été effectuée.
